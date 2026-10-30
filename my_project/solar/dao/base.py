from functools import wraps

from my_project.utils.db import DATA_ERRORS, INTEGRITY_ERRORS, get_db
from my_project.utils.errors import ConflictError, ValidationError


def translate_db_errors(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except INTEGRITY_ERRORS as exc:
            raise ConflictError(
                "Порушено обмеження цілісності БД (дублікат унікального значення "
                "або запис пов'язаний з іншими таблицями)",
                details=str(exc),
            )
        except DATA_ERRORS as exc:
            raise ValidationError("Некоректне значення поля для БД", details=str(exc))

    return wrapper


class BaseDao:
    entity = None

    @property
    def db(self):
        return get_db()

    def _select_columns(self, alias=None):
        prefix = f"{alias}." if alias else ""
        return ", ".join(prefix + column for column in self.entity.columns())

    def _pk_where(self):
        return " AND ".join(f"{column} = %s" for column in self.entity.pk_columns())

    def _order_by(self):
        return ", ".join(self.entity.pk_columns())

    def find_all(self, limit=None, offset=0):
        sql = f"SELECT {self._select_columns()} FROM {self.entity.TABLE} ORDER BY {self._order_by()}"
        params = []
        if limit is not None:
            sql += " LIMIT %s OFFSET %s"
            params = [limit, offset]
        return [self.entity.from_row(row) for row in self.db.fetch_all(sql, params)]

    def find_by_id(self, *pk):
        sql = f"SELECT {self._select_columns()} FROM {self.entity.TABLE} WHERE {self._pk_where()}"
        row = self.db.fetch_one(sql, pk)
        return self.entity.from_row(row) if row else None

    def find_by(self, column, value, order_by=None):
        if column not in self.entity.columns():
            raise ValueError(f"Невідомий стовпець {column}")
        sql = f"SELECT {self._select_columns()} FROM {self.entity.TABLE} WHERE {column} = %s"
        sql += f" ORDER BY {order_by or self._order_by()}"
        return [self.entity.from_row(row) for row in self.db.fetch_all(sql, [value])]

    def exists(self, *pk):
        sql = f"SELECT 1 AS found FROM {self.entity.TABLE} WHERE {self._pk_where()}"
        return self.db.fetch_one(sql, pk) is not None

    def count(self):
        row = self.db.fetch_one(f"SELECT COUNT(*) AS cnt FROM {self.entity.TABLE}")
        return int(row["cnt"])

    @translate_db_errors
    def insert(self, values):
        columns = list(values)
        placeholders = ", ".join(["%s"] * len(columns))
        sql = f"INSERT INTO {self.entity.TABLE} ({', '.join(columns)}) VALUES ({placeholders})"
        _, last_id = self.db.execute(sql, [values[c] for c in columns])
        if self.entity.AUTO_PK:
            return (last_id,)
        return tuple(values[c] for c in self.entity.pk_columns())

    @translate_db_errors
    def update(self, pk, values):
        if not values:
            return 0
        assignments = ", ".join(f"{column} = %s" for column in values)
        sql = f"UPDATE {self.entity.TABLE} SET {assignments} WHERE {self._pk_where()}"
        rowcount, _ = self.db.execute(sql, list(values.values()) + list(pk))
        return rowcount

    @translate_db_errors
    def delete(self, *pk):
        sql = f"DELETE FROM {self.entity.TABLE} WHERE {self._pk_where()}"
        rowcount, _ = self.db.execute(sql, pk)
        return rowcount

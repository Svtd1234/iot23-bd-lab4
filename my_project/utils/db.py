import sqlite3
from datetime import date, datetime
from decimal import Decimal

from flask import current_app, g

try:
    import pymysql
    import pymysql.cursors
except ImportError:
    pymysql = None

if pymysql is not None:
    INTEGRITY_ERRORS = (pymysql.err.IntegrityError, sqlite3.IntegrityError)
    DATA_ERRORS = (pymysql.err.DataError, sqlite3.DataError)
else:
    INTEGRITY_ERRORS = (sqlite3.IntegrityError,)
    DATA_ERRORS = (sqlite3.DataError,)


sqlite3.register_adapter(Decimal, str)
sqlite3.register_adapter(date, lambda value: value.isoformat())
sqlite3.register_adapter(datetime, lambda value: value.strftime("%Y-%m-%d %H:%M:%S"))
sqlite3.register_converter("DECIMAL", lambda raw: Decimal(raw.decode()))
sqlite3.register_converter("DATE", lambda raw: date.fromisoformat(raw.decode()))
sqlite3.register_converter("DATETIME", lambda raw: datetime.fromisoformat(raw.decode()))


class Database:
    def __init__(self, conn, paramstyle):
        self.conn = conn
        self.paramstyle = paramstyle

    def _prepare(self, sql):
        if self.paramstyle == "qmark":
            return sql.replace("%s", "?")
        return sql

    def fetch_all(self, sql, params=()):
        cursor = self.conn.cursor()
        try:
            cursor.execute(self._prepare(sql), tuple(params))
            return [dict(row) for row in cursor.fetchall()]
        finally:
            cursor.close()

    def fetch_one(self, sql, params=()):
        rows = self.fetch_all(sql, params)
        return rows[0] if rows else None

    def execute(self, sql, params=()):
        cursor = self.conn.cursor()
        try:
            cursor.execute(self._prepare(sql), tuple(params))
            return cursor.rowcount, cursor.lastrowid
        finally:
            cursor.close()

    def commit(self):
        self.conn.commit()

    def rollback(self):
        self.conn.rollback()

    def close(self):
        self.conn.close()


def open_database(db_config):
    driver = db_config.get("driver", "mysql")
    if driver == "sqlite":
        conn = sqlite3.connect(db_config["sqlite_path"], detect_types=sqlite3.PARSE_DECLTYPES)
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA foreign_keys = ON")
        return Database(conn, "qmark")
    if driver == "mysql":
        if pymysql is None:
            raise RuntimeError("Не встановлено PyMySQL. Виконайте: pip install -r requirements.txt")
        conn = pymysql.connect(
            host=db_config["host"],
            port=int(db_config.get("port", 3306)),
            user=db_config["user"],
            password=db_config["password"],
            database=db_config["name"],
            charset="utf8mb4",
            cursorclass=pymysql.cursors.DictCursor,
            autocommit=False,
        )
        return Database(conn, "format")
    raise RuntimeError(f"Невідомий драйвер БД: {driver}")


def get_db():
    if "db" not in g:
        g.db = open_database(current_app.config["APP_CONFIG"]["database"])
    return g.db


def commit_db():
    db = g.pop("db", None)
    if db is not None:
        db.commit()
        db.close()


def rollback_db():
    db = g.pop("db", None)
    if db is not None:
        db.rollback()
        db.close()

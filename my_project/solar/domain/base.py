from datetime import date, datetime
from decimal import Decimal

from my_project.utils.dates import fmt_datetime, to_date
from my_project.utils.errors import ValidationError


def _normalize(name, kind, value):
    if value is None:
        return None
    if isinstance(kind, tuple):
        allowed = kind[1:]
        if value not in allowed:
            raise ValidationError(f"Поле '{name}' має бути одним зі значень: {', '.join(allowed)}")
        return value
    if kind == "int":
        if isinstance(value, bool) or not isinstance(value, int):
            raise ValidationError(f"Поле '{name}' має бути цілим числом")
        return value
    if kind == "num":
        if isinstance(value, bool) or not isinstance(value, (int, float)):
            raise ValidationError(f"Поле '{name}' має бути числом")
        return value
    if kind == "str":
        if not isinstance(value, str):
            raise ValidationError(f"Поле '{name}' має бути рядком")
        return value.strip()
    if kind == "bool":
        if not isinstance(value, bool):
            raise ValidationError(f"Поле '{name}' має бути true або false")
        return value
    if kind == "date":
        try:
            if not isinstance(value, str):
                raise ValueError
            return to_date(value).isoformat()
        except ValueError:
            raise ValidationError(f"Поле '{name}' має бути датою у форматі YYYY-MM-DD")
    if kind == "datetime":
        try:
            if not isinstance(value, str):
                raise ValueError
            return fmt_datetime(value)
        except ValueError:
            raise ValidationError(f"Поле '{name}' має бути датою і часом у форматі YYYY-MM-DD HH:MM:SS")
    raise ValidationError(f"Невідомий тип поля '{name}'")


def serialize(value):
    if isinstance(value, Decimal):
        return float(value)
    if isinstance(value, datetime):
        return value.strftime("%Y-%m-%d %H:%M:%S")
    if isinstance(value, date):
        return value.isoformat()
    return value


class Entity:
    TABLE = None
    PK = {}
    AUTO_PK = True
    FIELDS = {}
    REQUIRED = ()
    BOOL_FIELDS = ()

    def __init__(self, values):
        self.values = dict(values)

    @classmethod
    def pk_columns(cls):
        return tuple(cls.PK)

    @classmethod
    def columns(cls):
        return tuple(cls.PK) + tuple(cls.FIELDS)

    @classmethod
    def from_row(cls, row):
        return cls(row)

    @classmethod
    def validate(cls, data, partial):
        if not isinstance(data, dict):
            raise ValidationError("Тіло запиту має бути JSON-об'єктом")
        allowed = dict(cls.FIELDS)
        required = list(cls.REQUIRED)
        if not partial and not cls.AUTO_PK:
            allowed.update(cls.PK)
            required = list(cls.PK) + required
        unknown = [key for key in data if key not in allowed]
        if unknown:
            raise ValidationError(
                f"Невідомі або заборонені поля: {', '.join(unknown)}",
                details={"allowed_fields": list(allowed)},
            )
        values = {}
        for name, value in data.items():
            values[name] = _normalize(name, allowed[name], value)
        if not partial:
            missing = [name for name in required if values.get(name) in (None, "")]
            if missing:
                raise ValidationError(f"Відсутні обов'язкові поля: {', '.join(missing)}")
        else:
            for name in cls.REQUIRED:
                if name in values and values[name] in (None, ""):
                    raise ValidationError(f"Поле '{name}' не може бути порожнім")
            if not values:
                raise ValidationError("Не передано жодного поля для оновлення")
        return values

    def get(self, name, default=None):
        return self.values.get(name, default)

    def pk(self):
        return tuple(self.values[name] for name in self.PK)

    def to_dto(self):
        dto = {}
        for column in self.columns():
            value = serialize(self.values.get(column))
            if column in self.BOOL_FIELDS and value is not None:
                value = bool(value)
            dto[column] = value
        return dto

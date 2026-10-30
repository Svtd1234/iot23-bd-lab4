from datetime import date

from my_project.solar.domain.base import Entity
from my_project.utils.dates import to_date


def _usage_days(row):
    start = to_date(row["installation_date"])
    end = to_date(row["decommission_date"]) if row.get("decommission_date") else date.today()
    return (end - start).days


class Station(Entity):
    TABLE = "stations"
    PK = {"station_id": "int"}
    FIELDS = {
        "address_id": "int",
        "station_name": "str",
        "installation_date": "date",
        "grid_connection_id": "str",
        "status": ("enum", "active", "inactive", "maintenance"),
    }
    REQUIRED = ("address_id", "station_name", "installation_date")


class StationOwner(Entity):
    TABLE = "station_owners"
    PK = {"station_id": "int", "owner_id": "int"}
    AUTO_PK = False
    FIELDS = {
        "ownership_share": "num",
        "since_date": "date",
    }
    REQUIRED = ("since_date",)


class Panel(Entity):
    TABLE = "panels"
    PK = {"panel_id": "int"}
    FIELDS = {
        "station_id": "int",
        "panel_type_id": "int",
        "serial_number": "str",
        "installation_date": "date",
        "decommission_date": "date",
        "current_tilt_angle": "num",
    }
    REQUIRED = ("station_id", "panel_type_id", "serial_number", "installation_date")

    def to_dto(self):
        dto = super().to_dto()
        dto["usage_days"] = _usage_days(self.values)
        return dto


class Battery(Entity):
    TABLE = "batteries"
    PK = {"battery_id": "int"}
    FIELDS = {
        "station_id": "int",
        "battery_type_id": "int",
        "serial_number": "str",
        "installation_date": "date",
        "decommission_date": "date",
    }
    REQUIRED = ("station_id", "battery_type_id", "serial_number", "installation_date")

    def to_dto(self):
        dto = super().to_dto()
        dto["usage_days"] = _usage_days(self.values)
        return dto

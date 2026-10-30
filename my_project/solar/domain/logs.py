from my_project.solar.domain.base import Entity


class PanelHourlyGeneration(Entity):
    TABLE = "panel_hourly_generation"
    PK = {"generation_id": "int"}
    FIELDS = {
        "panel_id": "int",
        "reading_datetime": "datetime",
        "generated_kwh": "num",
    }
    REQUIRED = ("panel_id", "reading_datetime", "generated_kwh")


class PanelTiltLog(Entity):
    TABLE = "panel_tilt_log"
    PK = {"tilt_log_id": "int"}
    FIELDS = {
        "panel_id": "int",
        "change_datetime": "datetime",
        "tilt_angle": "num",
    }
    REQUIRED = ("panel_id", "change_datetime", "tilt_angle")


class BatteryChargeLog(Entity):
    TABLE = "battery_charge_log"
    PK = {"charge_log_id": "int"}
    FIELDS = {
        "battery_id": "int",
        "reading_datetime": "datetime",
        "charge_level_pct": "num",
        "charge_level_kwh": "num",
    }
    REQUIRED = ("battery_id", "reading_datetime", "charge_level_pct")


class EnergySale(Entity):
    TABLE = "energy_sales"
    PK = {"sale_id": "int"}
    FIELDS = {
        "station_id": "int",
        "sale_datetime": "datetime",
        "energy_kwh": "num",
        "price_id": "int",
        "total_amount": "num",
    }
    REQUIRED = ("station_id", "sale_datetime", "energy_kwh")

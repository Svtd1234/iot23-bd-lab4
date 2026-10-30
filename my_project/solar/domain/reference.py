from my_project.solar.domain.base import Entity


class Address(Entity):
    TABLE = "addresses"
    PK = {"address_id": "int"}
    FIELDS = {
        "country": "str",
        "region": "str",
        "city": "str",
        "street": "str",
        "building_number": "str",
        "postal_code": "str",
        "latitude": "num",
        "longitude": "num",
    }
    REQUIRED = ("country", "region", "city", "street", "building_number")


class Owner(Entity):
    TABLE = "owners"
    PK = {"owner_id": "int"}
    FIELDS = {
        "first_name": "str",
        "last_name": "str",
        "phone": "str",
        "email": "str",
        "passport_no": "str",
    }
    REQUIRED = ("first_name", "last_name", "phone")


class PanelType(Entity):
    TABLE = "panel_types"
    PK = {"panel_type_id": "int"}
    FIELDS = {
        "manufacturer": "str",
        "model": "str",
        "nominal_power_w": "int",
        "is_adjustable": "bool",
        "warranty_years": "int",
    }
    REQUIRED = ("manufacturer", "model", "nominal_power_w", "warranty_years")
    BOOL_FIELDS = ("is_adjustable",)


class BatteryType(Entity):
    TABLE = "battery_types"
    PK = {"battery_type_id": "int"}
    FIELDS = {
        "manufacturer": "str",
        "model": "str",
        "capacity_kwh": "num",
        "cycle_life": "int",
        "warranty_years": "int",
    }
    REQUIRED = ("manufacturer", "model", "capacity_kwh", "cycle_life", "warranty_years")


class EnergyPrice(Entity):
    TABLE = "energy_prices"
    PK = {"price_id": "int"}
    FIELDS = {
        "price_datetime": "datetime",
        "price_per_kwh": "num",
    }
    REQUIRED = ("price_datetime", "price_per_kwh")

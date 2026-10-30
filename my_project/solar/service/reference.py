import re

from my_project.solar.dao import (
    AddressDao,
    BatteryDao,
    BatteryTypeDao,
    EnergyPriceDao,
    EnergySaleDao,
    OwnerDao,
    PanelDao,
    PanelTypeDao,
    StationDao,
)
from my_project.solar.service.base import BaseService, positive
from my_project.utils.errors import ValidationError

PHONE_RE = re.compile(r"^\+?\d{10,15}$")
EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")


class AddressService(BaseService):
    dao_class = AddressDao
    label = "Адресу"

    def __init__(self):
        super().__init__()
        self.station_dao = StationDao()

    def check(self, v, current):
        lat, lon = v.get("latitude"), v.get("longitude")
        if lat is not None and not -90 <= lat <= 90:
            raise ValidationError("latitude має бути в межах від -90 до 90")
        if lon is not None and not -180 <= lon <= 180:
            raise ValidationError("longitude має бути в межах від -180 до 180")

    def stations_of(self, address_id):
        return self.children_of(self.station_dao.find_by_address, address_id)

    def with_stations(self):
        return self.with_children(self.station_dao, "address_id")


class OwnerService(BaseService):
    dao_class = OwnerDao
    label = "Власника"

    def check(self, v, current):
        if not PHONE_RE.match(v["phone"]):
            raise ValidationError("phone має бути у форматі +380XXXXXXXXX (10-15 цифр)")
        if v.get("email") and not EMAIL_RE.match(v["email"]):
            raise ValidationError("email має некоректний формат")


class PanelTypeService(BaseService):
    dao_class = PanelTypeDao
    label = "Тип панелі"

    def __init__(self):
        super().__init__()
        self.panel_dao = PanelDao()

    def check(self, v, current):
        positive("nominal_power_w", v.get("nominal_power_w"))
        positive("warranty_years", v.get("warranty_years"), allow_zero=True)

    def panels_of(self, panel_type_id):
        return self.children_of(self.panel_dao.find_by_type, panel_type_id)

    def with_panels(self):
        return self.with_children(self.panel_dao, "panel_type_id")


class BatteryTypeService(BaseService):
    dao_class = BatteryTypeDao
    label = "Тип батареї"

    def __init__(self):
        super().__init__()
        self.battery_dao = BatteryDao()

    def check(self, v, current):
        positive("capacity_kwh", v.get("capacity_kwh"))
        positive("cycle_life", v.get("cycle_life"))
        positive("warranty_years", v.get("warranty_years"), allow_zero=True)

    def batteries_of(self, battery_type_id):
        return self.children_of(self.battery_dao.find_by_type, battery_type_id)


class EnergyPriceService(BaseService):
    dao_class = EnergyPriceDao
    label = "Ціну"

    def __init__(self):
        super().__init__()
        self.sale_dao = EnergySaleDao()

    def check(self, v, current):
        positive("price_per_kwh", v.get("price_per_kwh"), allow_zero=True)

    def sales_of(self, price_id):
        return self.children_of(self.sale_dao.find_by_price, price_id)

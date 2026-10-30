from my_project.solar.dao.base import BaseDao
from my_project.solar.domain import Address, BatteryType, EnergyPrice, Owner, PanelType


class AddressDao(BaseDao):
    entity = Address


class OwnerDao(BaseDao):
    entity = Owner


class PanelTypeDao(BaseDao):
    entity = PanelType


class BatteryTypeDao(BaseDao):
    entity = BatteryType


class EnergyPriceDao(BaseDao):
    entity = EnergyPrice

    def find_by_datetime(self, price_datetime):
        rows = self.find_by("price_datetime", price_datetime)
        return rows[0] if rows else None

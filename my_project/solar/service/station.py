from collections import defaultdict
from datetime import date

from my_project.solar.dao import (
    AddressDao,
    BatteryChargeLogDao,
    BatteryDao,
    BatteryTypeDao,
    EnergySaleDao,
    OwnerDao,
    PanelDao,
    PanelGenerationDao,
    PanelTiltLogDao,
    PanelTypeDao,
    StationDao,
    StationOwnerDao,
)
from my_project.solar.service.base import BaseService
from my_project.utils.dates import to_date
from my_project.utils.errors import NotFoundError, ValidationError


def _check_dates(installation, decommission):
    if installation is not None and to_date(installation) > date.today():
        raise ValidationError("installation_date не може бути в майбутньому")
    if decommission is not None and installation is not None and to_date(decommission) < to_date(installation):
        raise ValidationError("decommission_date не може бути раніше за installation_date")


class StationService(BaseService):
    dao_class = StationDao
    label = "Станцію"

    def __init__(self):
        super().__init__()
        self.address_dao = AddressDao()
        self.panel_dao = PanelDao()
        self.battery_dao = BatteryDao()
        self.sale_dao = EnergySaleDao()

    def check(self, v, current):
        self.require_exists(self.address_dao, v.get("address_id"), "Адреса")
        _check_dates(v.get("installation_date"), None)

    def panels_of(self, station_id):
        return self.children_of(self.panel_dao.find_by_station, station_id)

    def batteries_of(self, station_id):
        return self.children_of(self.battery_dao.find_by_station, station_id)

    def sales_of(self, station_id):
        return self.children_of(self.sale_dao.find_by_station, station_id)

    def with_panels(self):
        return self.with_children(self.panel_dao, "station_id")


class StationOwnerService(BaseService):
    dao_class = StationOwnerDao
    label = "Зв'язок станція-власник"

    def __init__(self):
        super().__init__()
        self.station_dao = StationDao()
        self.owner_dao = OwnerDao()

    def check(self, v, current):
        station_id, owner_id = v["station_id"], v["owner_id"]
        self.require_exists(self.station_dao, station_id, "Станція")
        self.require_exists(self.owner_dao, owner_id, "Власник")
        share = float(v.get("ownership_share", 100.0))
        if not 0 < share <= 100:
            raise ValidationError("ownership_share має бути в межах (0; 100]")
        if to_date(v["since_date"]) > date.today():
            raise ValidationError("since_date не може бути в майбутньому")
        others = self.dao.sum_share(station_id, exclude_owner_id=owner_id)
        if others + share > 100.0 + 1e-9:
            raise ValidationError(
                f"Сума часток власників станції не може перевищувати 100% "
                f"(вже розподілено {others}%, доступно {round(100 - others, 2)}%)"
            )

    def owners_of_station(self, station_id):
        station = self.station_dao.find_by_id(station_id)
        if station is None:
            raise NotFoundError(f"Станцію з id={station_id} не знайдено")
        return station, self.dao.find_owners_of_station(station_id)

    def stations_of_owner(self, owner_id):
        owner = self.owner_dao.find_by_id(owner_id)
        if owner is None:
            raise NotFoundError(f"Власника з id={owner_id} не знайдено")
        return owner, self.dao.find_stations_of_owner(owner_id)

    def stations_with_owners(self):
        grouped = defaultdict(list)
        for row in self.dao.find_all_owner_links():
            grouped[row["station_id"]].append(row)
        return [(station, grouped.get(station.get("station_id"), [])) for station in self.station_dao.find_all()]

    def owners_with_stations(self):
        grouped = defaultdict(list)
        for row in self.dao.find_all_station_links():
            grouped[row["owner_id"]].append(row)
        return [(owner, grouped.get(owner.get("owner_id"), [])) for owner in self.owner_dao.find_all()]


class PanelService(BaseService):
    dao_class = PanelDao
    label = "Панель"

    def __init__(self):
        super().__init__()
        self.station_dao = StationDao()
        self.type_dao = PanelTypeDao()
        self.generation_dao = PanelGenerationDao()
        self.tilt_dao = PanelTiltLogDao()

    def check(self, v, current):
        self.require_exists(self.station_dao, v.get("station_id"), "Станція")
        self.require_exists(self.type_dao, v.get("panel_type_id"), "Тип панелі")
        _check_dates(v.get("installation_date"), v.get("decommission_date"))
        tilt = v.get("current_tilt_angle")
        if tilt is not None and not 0 <= tilt <= 90:
            raise ValidationError("current_tilt_angle має бути в межах від 0 до 90 градусів")

    def generation_of(self, panel_id):
        return self.children_of(self.generation_dao.find_by_panel, panel_id)

    def tilt_log_of(self, panel_id):
        return self.children_of(self.tilt_dao.find_by_panel, panel_id)


class BatteryService(BaseService):
    dao_class = BatteryDao
    label = "Батарею"

    def __init__(self):
        super().__init__()
        self.station_dao = StationDao()
        self.type_dao = BatteryTypeDao()
        self.charge_dao = BatteryChargeLogDao()

    def check(self, v, current):
        self.require_exists(self.station_dao, v.get("station_id"), "Станція")
        self.require_exists(self.type_dao, v.get("battery_type_id"), "Тип батареї")
        _check_dates(v.get("installation_date"), v.get("decommission_date"))

    def charge_log_of(self, battery_id):
        return self.children_of(self.charge_dao.find_by_battery, battery_id)

from my_project.solar.dao import (
    BatteryChargeLogDao,
    BatteryDao,
    BatteryTypeDao,
    EnergyPriceDao,
    EnergySaleDao,
    PanelDao,
    PanelGenerationDao,
    PanelTiltLogDao,
    PanelTypeDao,
    StationDao,
)
from my_project.solar.service.base import BaseService, positive
from my_project.utils.dates import floor_hour, fmt_datetime, to_date, to_datetime
from my_project.utils.errors import ValidationError


class PanelGenerationService(BaseService):
    dao_class = PanelGenerationDao
    label = "Запис генерації"

    def __init__(self):
        super().__init__()
        self.panel_dao = PanelDao()
        self.type_dao = PanelTypeDao()

    def check(self, v, current):
        panel = self.panel_dao.find_by_id(v.get("panel_id"))
        if panel is None:
            raise ValidationError(f"Панель з id={v.get('panel_id')} не існує")
        positive("generated_kwh", v["generated_kwh"], allow_zero=True)
        if to_date(v["reading_datetime"]) < to_date(panel.get("installation_date")):
            raise ValidationError("Вимір не може бути раніше за дату встановлення панелі")
        panel_type = self.type_dao.find_by_id(panel.get("panel_type_id"))
        max_kwh = panel_type.get("nominal_power_w") / 1000.0
        if float(v["generated_kwh"]) > max_kwh + 1e-9:
            raise ValidationError(
                f"За годину панель потужністю {panel_type.get('nominal_power_w')} Вт "
                f"не може згенерувати більше {max_kwh} кВт·год"
            )


class PanelTiltLogService(BaseService):
    dao_class = PanelTiltLogDao
    label = "Запис кута нахилу"

    def __init__(self):
        super().__init__()
        self.panel_dao = PanelDao()
        self.type_dao = PanelTypeDao()

    def check(self, v, current):
        panel = self.panel_dao.find_by_id(v.get("panel_id"))
        if panel is None:
            raise ValidationError(f"Панель з id={v.get('panel_id')} не існує")
        if not 0 <= float(v["tilt_angle"]) <= 90:
            raise ValidationError("tilt_angle має бути в межах від 0 до 90 градусів")
        panel_type = self.type_dao.find_by_id(panel.get("panel_type_id"))
        if not panel_type.get("is_adjustable"):
            raise ValidationError("Ця панель має фіксований кут нахилу (is_adjustable = false)")

    def after_write(self, entity):
        panel_id = entity.get("panel_id")
        last = self.dao.latest_datetime(panel_id)
        if last is not None and to_datetime(last) == to_datetime(entity.get("change_datetime")):
            self.panel_dao.set_tilt(panel_id, entity.get("tilt_angle"))


class BatteryChargeLogService(BaseService):
    dao_class = BatteryChargeLogDao
    label = "Запис рівня заряду"

    def __init__(self):
        super().__init__()
        self.battery_dao = BatteryDao()
        self.type_dao = BatteryTypeDao()

    def check(self, v, current):
        battery = self.battery_dao.find_by_id(v.get("battery_id"))
        if battery is None:
            raise ValidationError(f"Батарею з id={v.get('battery_id')} не існує")
        pct = float(v["charge_level_pct"])
        if not 0 <= pct <= 100:
            raise ValidationError("charge_level_pct має бути в межах від 0 до 100")
        capacity = float(self.type_dao.find_by_id(battery.get("battery_type_id")).get("capacity_kwh"))
        expected_kwh = round(capacity * pct / 100.0, 3)
        kwh = v.get("charge_level_kwh")
        pct_changed = current is not None and pct != float(current.get("charge_level_pct"))
        kwh_unchanged = current is not None and kwh is not None and float(kwh) == float(current.get("charge_level_kwh"))
        if kwh is None or (pct_changed and kwh_unchanged):
            return {"charge_level_kwh": expected_kwh}
        kwh = float(kwh)
        if kwh < 0 or kwh > capacity + 1e-9:
            raise ValidationError(f"charge_level_kwh має бути в межах від 0 до {capacity} (ємність батареї)")
        if abs(kwh - expected_kwh) > capacity * 0.01 + 1e-9:
            raise ValidationError(
                f"charge_level_kwh ({kwh}) не відповідає charge_level_pct ({pct}%) "
                f"для ємності {capacity} кВт·год (очікується ~{expected_kwh})"
            )
        return {}


class EnergySaleService(BaseService):
    dao_class = EnergySaleDao
    label = "Продаж"

    def __init__(self):
        super().__init__()
        self.station_dao = StationDao()
        self.price_dao = EnergyPriceDao()

    def check(self, v, current):
        station = self.station_dao.find_by_id(v.get("station_id"))
        if station is None:
            raise ValidationError(f"Станцію з id={v.get('station_id')} не існує")
        if current is None and station.get("status") != "active":
            raise ValidationError(
                f"Станція має статус '{station.get('status')}' — продавати енергію можуть лише активні станції"
            )
        positive("energy_kwh", v["energy_kwh"])
        hour = floor_hour(v["sale_datetime"])
        price_id = v.get("price_id")
        if price_id is None or (current is not None and "sale_datetime" in v and price_id == current.get("price_id")
                                and floor_hour(current.get("sale_datetime")) != hour):
            price = self.price_dao.find_by_datetime(fmt_datetime(hour))
            if price is None:
                raise ValidationError(f"Для години {fmt_datetime(hour)} у таблиці energy_prices немає ціни")
        else:
            price = self.price_dao.find_by_id(price_id)
            if price is None:
                raise ValidationError(f"Ціну з id={price_id} не існує")
            if floor_hour(price.get("price_datetime")) != hour:
                raise ValidationError(
                    f"Ціна id={price_id} діє на {fmt_datetime(price.get('price_datetime'))}, "
                    f"а продаж відбувся о {fmt_datetime(v['sale_datetime'])}"
                )
        total = round(float(v["energy_kwh"]) * float(price.get("price_per_kwh")), 2)
        return {"price_id": price.get("price_id"), "total_amount": total}

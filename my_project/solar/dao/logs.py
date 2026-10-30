from my_project.solar.dao.base import BaseDao
from my_project.solar.domain import (
    BatteryChargeLog,
    EnergySale,
    PanelHourlyGeneration,
    PanelTiltLog,
)


class PanelGenerationDao(BaseDao):
    entity = PanelHourlyGeneration

    def find_by_panel(self, panel_id):
        return self.find_by("panel_id", panel_id, order_by="reading_datetime")


class PanelTiltLogDao(BaseDao):
    entity = PanelTiltLog

    def find_by_panel(self, panel_id):
        return self.find_by("panel_id", panel_id, order_by="change_datetime")

    def latest_datetime(self, panel_id):
        row = self.db.fetch_one(
            "SELECT MAX(change_datetime) AS last_change FROM panel_tilt_log WHERE panel_id = %s",
            [panel_id],
        )
        return row["last_change"] if row else None


class BatteryChargeLogDao(BaseDao):
    entity = BatteryChargeLog

    def find_by_battery(self, battery_id):
        return self.find_by("battery_id", battery_id, order_by="reading_datetime")


class EnergySaleDao(BaseDao):
    entity = EnergySale

    def find_by_station(self, station_id):
        return self.find_by("station_id", station_id, order_by="sale_datetime")

    def find_by_price(self, price_id):
        return self.find_by("price_id", price_id, order_by="sale_datetime")

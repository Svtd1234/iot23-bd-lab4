from my_project.solar.dao.base import BaseDao
from my_project.solar.domain import Battery, Panel, Station, StationOwner


class StationDao(BaseDao):
    entity = Station

    def find_by_address(self, address_id):
        return self.find_by("address_id", address_id)


class StationOwnerDao(BaseDao):
    entity = StationOwner

    def find_owners_of_station(self, station_id):
        sql = (
            "SELECT so.station_id, so.ownership_share, so.since_date, "
            "o.owner_id, o.first_name, o.last_name, o.phone, o.email "
            "FROM station_owners so JOIN owners o ON o.owner_id = so.owner_id "
            "WHERE so.station_id = %s ORDER BY o.owner_id"
        )
        return self.db.fetch_all(sql, [station_id])

    def find_all_owner_links(self):
        sql = (
            "SELECT so.station_id, so.ownership_share, so.since_date, "
            "o.owner_id, o.first_name, o.last_name, o.phone, o.email "
            "FROM station_owners so JOIN owners o ON o.owner_id = so.owner_id "
            "ORDER BY so.station_id, o.owner_id"
        )
        return self.db.fetch_all(sql)

    def find_stations_of_owner(self, owner_id):
        sql = (
            "SELECT so.owner_id, so.ownership_share, so.since_date, "
            "s.station_id, s.station_name, s.address_id, s.status "
            "FROM station_owners so JOIN stations s ON s.station_id = so.station_id "
            "WHERE so.owner_id = %s ORDER BY s.station_id"
        )
        return self.db.fetch_all(sql, [owner_id])

    def find_all_station_links(self):
        sql = (
            "SELECT so.owner_id, so.ownership_share, so.since_date, "
            "s.station_id, s.station_name, s.address_id, s.status "
            "FROM station_owners so JOIN stations s ON s.station_id = so.station_id "
            "ORDER BY so.owner_id, s.station_id"
        )
        return self.db.fetch_all(sql)

    def sum_share(self, station_id, exclude_owner_id=None):
        sql = "SELECT COALESCE(SUM(ownership_share), 0) AS total FROM station_owners WHERE station_id = %s"
        params = [station_id]
        if exclude_owner_id is not None:
            sql += " AND owner_id <> %s"
            params.append(exclude_owner_id)
        return float(self.db.fetch_one(sql, params)["total"])


class PanelDao(BaseDao):
    entity = Panel

    def find_by_station(self, station_id):
        return self.find_by("station_id", station_id)

    def find_by_type(self, panel_type_id):
        return self.find_by("panel_type_id", panel_type_id)

    def set_tilt(self, panel_id, angle):
        return self.update((panel_id,), {"current_tilt_angle": angle})


class BatteryDao(BaseDao):
    entity = Battery

    def find_by_station(self, station_id):
        return self.find_by("station_id", station_id)

    def find_by_type(self, battery_type_id):
        return self.find_by("battery_type_id", battery_type_id)

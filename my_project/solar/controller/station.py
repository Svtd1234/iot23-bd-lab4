from my_project.solar.controller.base import BaseController, children_response, grouped_response
from my_project.solar.service import (
    BatteryService,
    PanelService,
    StationOwnerService,
    StationService,
)


class StationController(BaseController):
    def __init__(self):
        super().__init__(StationService())

    def panels_of(self, station_id):
        parent, children = self.service.panels_of(station_id)
        return children_response("station", parent, "panels", children)

    def batteries_of(self, station_id):
        parent, children = self.service.batteries_of(station_id)
        return children_response("station", parent, "batteries", children)

    def sales_of(self, station_id):
        parent, children = self.service.sales_of(station_id)
        return children_response("station", parent, "sales", children)

    def with_panels(self):
        return grouped_response(self.service.with_panels(), "panels")


class StationOwnerController(BaseController):
    def __init__(self):
        super().__init__(StationOwnerService())

    def owners_of_station(self, station_id):
        station, rows = self.service.owners_of_station(station_id)
        return children_response("station", station, "owners", rows, row_drop=("station_id",))

    def stations_of_owner(self, owner_id):
        owner, rows = self.service.stations_of_owner(owner_id)
        return children_response("owner", owner, "stations", rows, row_drop=("owner_id",))

    def stations_with_owners(self):
        return grouped_response(self.service.stations_with_owners(), "owners", row_drop=("station_id",))

    def owners_with_stations(self):
        return grouped_response(self.service.owners_with_stations(), "stations", row_drop=("owner_id",))


class PanelController(BaseController):
    def __init__(self):
        super().__init__(PanelService())

    def generation_of(self, panel_id):
        parent, children = self.service.generation_of(panel_id)
        return children_response("panel", parent, "generation", children)

    def tilt_log_of(self, panel_id):
        parent, children = self.service.tilt_log_of(panel_id)
        return children_response("panel", parent, "tilt_log", children)


class BatteryController(BaseController):
    def __init__(self):
        super().__init__(BatteryService())

    def charge_log_of(self, battery_id):
        parent, children = self.service.charge_log_of(battery_id)
        return children_response("battery", parent, "charge_log", children)

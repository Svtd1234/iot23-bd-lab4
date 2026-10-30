from my_project.solar.controller.base import BaseController, children_response, grouped_response
from my_project.solar.service import (
    AddressService,
    BatteryTypeService,
    EnergyPriceService,
    OwnerService,
    PanelTypeService,
)


class AddressController(BaseController):
    def __init__(self):
        super().__init__(AddressService())

    def stations_of(self, address_id):
        parent, children = self.service.stations_of(address_id)
        return children_response("address", parent, "stations", children)

    def with_stations(self):
        return grouped_response(self.service.with_stations(), "stations")


class OwnerController(BaseController):
    def __init__(self):
        super().__init__(OwnerService())


class PanelTypeController(BaseController):
    def __init__(self):
        super().__init__(PanelTypeService())

    def panels_of(self, panel_type_id):
        parent, children = self.service.panels_of(panel_type_id)
        return children_response("panel_type", parent, "panels", children)

    def with_panels(self):
        return grouped_response(self.service.with_panels(), "panels")


class BatteryTypeController(BaseController):
    def __init__(self):
        super().__init__(BatteryTypeService())

    def batteries_of(self, battery_type_id):
        parent, children = self.service.batteries_of(battery_type_id)
        return children_response("battery_type", parent, "batteries", children)


class EnergyPriceController(BaseController):
    def __init__(self):
        super().__init__(EnergyPriceService())

    def sales_of(self, price_id):
        parent, children = self.service.sales_of(price_id)
        return children_response("energy_price", parent, "sales", children)

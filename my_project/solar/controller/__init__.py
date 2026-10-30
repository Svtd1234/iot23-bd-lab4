from my_project.solar.controller.logs import (
    BatteryChargeLogController,
    EnergySaleController,
    PanelGenerationController,
    PanelTiltLogController,
)
from my_project.solar.controller.reference import (
    AddressController,
    BatteryTypeController,
    EnergyPriceController,
    OwnerController,
    PanelTypeController,
)
from my_project.solar.controller.station import (
    BatteryController,
    PanelController,
    StationController,
    StationOwnerController,
)

address_controller = AddressController()
owner_controller = OwnerController()
panel_type_controller = PanelTypeController()
battery_type_controller = BatteryTypeController()
energy_price_controller = EnergyPriceController()
station_controller = StationController()
station_owner_controller = StationOwnerController()
panel_controller = PanelController()
battery_controller = BatteryController()
panel_generation_controller = PanelGenerationController()
panel_tilt_log_controller = PanelTiltLogController()
battery_charge_log_controller = BatteryChargeLogController()
energy_sale_controller = EnergySaleController()

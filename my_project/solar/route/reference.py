from my_project.solar.controller import (
    address_controller,
    battery_type_controller,
    energy_price_controller,
    owner_controller,
    panel_type_controller,
)
from my_project.solar.route.base import register_crud, register_view


def register_reference_routes(bp):
    register_crud(bp, "/addresses", "address", address_controller, ("address_id",))
    register_view(bp, "/addresses/with-stations", "addresses_with_stations", address_controller.with_stations)
    register_view(bp, "/addresses/<int:address_id>/stations", "address_stations", address_controller.stations_of)

    register_crud(bp, "/owners", "owner", owner_controller, ("owner_id",))

    register_crud(bp, "/panel-types", "panel_type", panel_type_controller, ("panel_type_id",))
    register_view(bp, "/panel-types/with-panels", "panel_types_with_panels", panel_type_controller.with_panels)
    register_view(bp, "/panel-types/<int:panel_type_id>/panels", "panel_type_panels", panel_type_controller.panels_of)

    register_crud(bp, "/battery-types", "battery_type", battery_type_controller, ("battery_type_id",))
    register_view(bp, "/battery-types/<int:battery_type_id>/batteries", "battery_type_batteries",
                  battery_type_controller.batteries_of)

    register_crud(bp, "/energy-prices", "energy_price", energy_price_controller, ("price_id",))
    register_view(bp, "/energy-prices/<int:price_id>/sales", "energy_price_sales", energy_price_controller.sales_of)

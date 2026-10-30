from my_project.solar.controller import (
    battery_controller,
    panel_controller,
    station_controller,
    station_owner_controller,
)
from my_project.solar.route.base import register_crud, register_view


def register_station_routes(bp):
    register_crud(bp, "/stations", "station", station_controller, ("station_id",))
    register_view(bp, "/stations/with-panels", "stations_with_panels", station_controller.with_panels)
    register_view(bp, "/stations/with-owners", "stations_with_owners", station_owner_controller.stations_with_owners)
    register_view(bp, "/stations/<int:station_id>/panels", "station_panels", station_controller.panels_of)
    register_view(bp, "/stations/<int:station_id>/batteries", "station_batteries", station_controller.batteries_of)
    register_view(bp, "/stations/<int:station_id>/sales", "station_sales", station_controller.sales_of)
    register_view(bp, "/stations/<int:station_id>/owners", "station_owners_of", station_owner_controller.owners_of_station)

    register_view(bp, "/owners/with-stations", "owners_with_stations", station_owner_controller.owners_with_stations)
    register_view(bp, "/owners/<int:owner_id>/stations", "owner_stations", station_owner_controller.stations_of_owner)

    register_crud(bp, "/station-owners", "station_owner", station_owner_controller, ("station_id", "owner_id"))

    register_crud(bp, "/panels", "panel", panel_controller, ("panel_id",))
    register_view(bp, "/panels/<int:panel_id>/generation", "panel_generation", panel_controller.generation_of)
    register_view(bp, "/panels/<int:panel_id>/tilt-log", "panel_tilt_log", panel_controller.tilt_log_of)

    register_crud(bp, "/batteries", "battery", battery_controller, ("battery_id",))
    register_view(bp, "/batteries/<int:battery_id>/charge-log", "battery_charge_log", battery_controller.charge_log_of)

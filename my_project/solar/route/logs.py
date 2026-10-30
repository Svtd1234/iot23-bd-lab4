from my_project.solar.controller import (
    battery_charge_log_controller,
    energy_sale_controller,
    panel_generation_controller,
    panel_tilt_log_controller,
)
from my_project.solar.route.base import register_crud


def register_log_routes(bp):
    register_crud(bp, "/panel-generation", "panel_generation_rec", panel_generation_controller, ("generation_id",))
    register_crud(bp, "/panel-tilt-log", "panel_tilt_rec", panel_tilt_log_controller, ("tilt_log_id",))
    register_crud(bp, "/battery-charge-log", "battery_charge_rec", battery_charge_log_controller, ("charge_log_id",))
    register_crud(bp, "/energy-sales", "energy_sale", energy_sale_controller, ("sale_id",))

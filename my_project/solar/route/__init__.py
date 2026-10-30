from flask import Blueprint

from my_project.solar.route.logs import register_log_routes
from my_project.solar.route.reference import register_reference_routes
from my_project.solar.route.station import register_station_routes


def create_api_blueprint():
    bp = Blueprint("api", __name__, url_prefix="/api")
    register_reference_routes(bp)
    register_station_routes(bp)
    register_log_routes(bp)
    return bp

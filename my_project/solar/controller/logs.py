from my_project.solar.controller.base import BaseController
from my_project.solar.service import (
    BatteryChargeLogService,
    EnergySaleService,
    PanelGenerationService,
    PanelTiltLogService,
)


class PanelGenerationController(BaseController):
    def __init__(self):
        super().__init__(PanelGenerationService())


class PanelTiltLogController(BaseController):
    def __init__(self):
        super().__init__(PanelTiltLogService())


class BatteryChargeLogController(BaseController):
    def __init__(self):
        super().__init__(BatteryChargeLogService())


class EnergySaleController(BaseController):
    def __init__(self):
        super().__init__(EnergySaleService())

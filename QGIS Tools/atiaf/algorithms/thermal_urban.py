"""Native ATIAF thermal_urban adapter; shared workflow is in atiaf_core."""
from .common import ATIAFAlgorithm


class ThermalUrbanAlgorithm(ATIAFAlgorithm):
    tool_id = "thermal_urban"

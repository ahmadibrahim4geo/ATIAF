"""Native ATIAF surface_temperature adapter; shared workflow is in atiaf_core."""
from .common import ATIAFAlgorithm


class SurfaceTemperatureAlgorithm(ATIAFAlgorithm):
    tool_id = "surface_temperature"

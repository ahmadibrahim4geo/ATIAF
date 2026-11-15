"""Native ATIAF environmental_drought adapter; shared workflow is in atiaf_core."""
from .common import ATIAFAlgorithm


class EnvironmentalDroughtAlgorithm(ATIAFAlgorithm):
    tool_id = "environmental_drought"

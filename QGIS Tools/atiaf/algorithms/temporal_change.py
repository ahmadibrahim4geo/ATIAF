"""Native ATIAF temporal_change adapter; shared workflow is in atiaf_core."""
from .common import ATIAFAlgorithm


class TemporalChangeAlgorithm(ATIAFAlgorithm):
    tool_id = "temporal_change"

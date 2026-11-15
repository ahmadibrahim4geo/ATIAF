"""Native ATIAF geological_analysis adapter; shared workflow is in atiaf_core."""
from .common import ATIAFAlgorithm


class GeologicalAnalysisAlgorithm(ATIAFAlgorithm):
    tool_id = "geological_analysis"

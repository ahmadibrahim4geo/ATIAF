"""ATIAF native Python toolbox. MIT; keep the complete repository together."""
from pathlib import Path
import sys
HERE = Path(__file__).resolve().parent
if str(HERE) not in sys.path:
    sys.path.insert(0, str(HERE))
from atiaf_arcgis import NativeTool


class SpectralIndicesTool(NativeTool):
    tool_id = "spectral_indices"
    language = "en"


class SurfaceTemperatureTool(NativeTool):
    tool_id = "surface_temperature"
    language = "en"


class ThermalUrbanTool(NativeTool):
    tool_id = "thermal_urban"
    language = "en"


class EnvironmentalDroughtTool(NativeTool):
    tool_id = "environmental_drought"
    language = "en"


class GeologicalAnalysisTool(NativeTool):
    tool_id = "geological_analysis"
    language = "en"


class TemporalChangeTool(NativeTool):
    tool_id = "temporal_change"
    language = "en"


class Toolbox:
    def __init__(self):
        self.label = "ATIAF — Imagery Analysis"
        self.alias = "atiaf"
        self.tools = [SpectralIndicesTool, SurfaceTemperatureTool, ThermalUrbanTool, EnvironmentalDroughtTool, GeologicalAnalysisTool, TemporalChangeTool]

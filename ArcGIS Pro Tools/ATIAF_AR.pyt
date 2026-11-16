"""ATIAF native Python toolbox. MIT; keep the complete repository together."""
from pathlib import Path
import site
import sys
HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
for path in (str(HERE), str(ROOT)):
    if path not in sys.path:
        sys.path.insert(0, path)
try:
    user_site = site.getusersitepackages()
    if user_site and Path(user_site).exists() and user_site not in sys.path:
        sys.path.append(user_site)
except Exception:
    pass
from atiaf_arcgis import NativeTool


class SpectralIndicesTool(NativeTool):
    tool_id = "spectral_indices"
    language = "ar"


class SurfaceTemperatureTool(NativeTool):
    tool_id = "surface_temperature"
    language = "ar"


class ThermalUrbanTool(NativeTool):
    tool_id = "thermal_urban"
    language = "ar"


class EnvironmentalDroughtTool(NativeTool):
    tool_id = "environmental_drought"
    language = "ar"


class GeologicalAnalysisTool(NativeTool):
    tool_id = "geological_analysis"
    language = "ar"


class TemporalChangeTool(NativeTool):
    tool_id = "temporal_change"
    language = "ar"


class Toolbox:
    def __init__(self):
        self.label = "أطياف — تحليل المرئيات"
        self.alias = "atiaf_ar"
        self.tools = [SpectralIndicesTool, SurfaceTemperatureTool, ThermalUrbanTool, EnvironmentalDroughtTool, GeologicalAnalysisTool, TemporalChangeTool, GeologicalColorCompositesTool]


class GeologicalColorCompositesTool(NativeTool):
    tool_id = "geological_composites"
    language = "ar"

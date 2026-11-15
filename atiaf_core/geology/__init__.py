"""ATIAF Geological & Mineral Analysis Package — spectral alteration ratios and thermal mineral indices."""

from atiaf_core.geology.engine import GeologicalAnalysisEngine
from atiaf_core.geology.registry import GEOLOGICAL_CATALOG, GeologicalIndexDefinition

__all__ = [
    "GEOLOGICAL_CATALOG",
    "GeologicalIndexDefinition",
    "GeologicalAnalysisEngine",
]

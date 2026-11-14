"""ATIAF Geological & Mineral Analysis Package — spectral alteration ratios and thermal mineral indices."""

from atyaf_core.geology.engine import GeologicalAnalysisEngine
from atyaf_core.geology.registry import GEOLOGICAL_CATALOG, GeologicalIndexDefinition

__all__ = [
    "GEOLOGICAL_CATALOG",
    "GeologicalIndexDefinition",
    "GeologicalAnalysisEngine",
]

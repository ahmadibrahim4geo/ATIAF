"""ATIAF Spectral Indices Package — mathematical catalog and execution engine."""

from atiaf_core.indices.engine import SpectralIndicesEngine
from atiaf_core.indices.registry import INDEX_CATALOG, SpectralIndexDefinition

__all__ = [
    "INDEX_CATALOG",
    "SpectralIndexDefinition",
    "SpectralIndicesEngine",
]

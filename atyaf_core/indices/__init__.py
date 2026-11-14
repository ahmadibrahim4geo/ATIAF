"""ATIAF Spectral Indices Package — mathematical catalog and execution engine."""

from atyaf_core.indices.engine import SpectralIndicesEngine
from atyaf_core.indices.registry import INDEX_CATALOG, SpectralIndexDefinition

__all__ = [
    "INDEX_CATALOG",
    "SpectralIndexDefinition",
    "SpectralIndicesEngine",
]

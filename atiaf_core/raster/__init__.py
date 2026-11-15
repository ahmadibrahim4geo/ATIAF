"""ATIAF Core Raster Engine — windowed computation, masks, CRS validation, and workspace management."""

from atiaf_core.raster.clip import PolygonClipEngine
from atiaf_core.raster.crs_utils import CRSManager, CRSValidationResult
from atiaf_core.raster.masks import QualityMaskEngine
from atiaf_core.raster.windowed import WindowedRasterEngine
from atiaf_core.raster.workspace import WorkspaceManager

__all__ = [
    "CRSManager",
    "CRSValidationResult",
    "QualityMaskEngine",
    "PolygonClipEngine",
    "WindowedRasterEngine",
    "WorkspaceManager",
]

"""Discovery module for detecting satellite products, metadata, and band assets."""

from atiaf_core.discovery.aster import AsterParser
from atiaf_core.discovery.landsat import LandsatParser
from atiaf_core.discovery.manual_mapper import ManualBandMapper
from atiaf_core.discovery.models import (
    BandAsset,
    BandRole,
    ProductLevel,
    QualityAsset,
    SceneInfo,
    SceneMetadata,
    SensorFamily,
)
from atiaf_core.discovery.scanner import SceneScanner, ScanResult
from atiaf_core.discovery.sentinel1 import Sentinel1Parser
from atiaf_core.discovery.sentinel2 import Sentinel2Parser

__all__ = [
    "BandRole",
    "ProductLevel",
    "SensorFamily",
    "BandAsset",
    "QualityAsset",
    "SceneMetadata",
    "SceneInfo",
    "LandsatParser",
    "Sentinel2Parser",
    "Sentinel1Parser",
    "AsterParser",
    "SceneScanner",
    "ScanResult",
    "ManualBandMapper",
]

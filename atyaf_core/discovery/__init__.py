"""Discovery module for detecting satellite products, metadata, and band assets."""

from atyaf_core.discovery.aster import AsterParser
from atyaf_core.discovery.landsat import LandsatParser
from atyaf_core.discovery.manual_mapper import ManualBandMapper
from atyaf_core.discovery.models import (
    BandAsset,
    BandRole,
    ProductLevel,
    QualityAsset,
    SceneInfo,
    SceneMetadata,
    SensorFamily,
)
from atyaf_core.discovery.scanner import SceneScanner, ScanResult
from atyaf_core.discovery.sentinel2 import Sentinel2Parser

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
    "AsterParser",
    "SceneScanner",
    "ScanResult",
    "ManualBandMapper",
]

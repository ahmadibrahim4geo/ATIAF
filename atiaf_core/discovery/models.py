"""Data models and representations for satellite products, bands, and scene metadata."""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional


class BandRole(str, Enum):
    COASTAL_AEROSOL = "coastal_aerosol"
    BLUE = "blue"
    GREEN = "green"
    RED = "red"
    RED_EDGE_1 = "red_edge_1"
    RED_EDGE_2 = "red_edge_2"
    RED_EDGE_3 = "red_edge_3"
    NIR = "nir"
    NARROW_NIR = "narrow_nir"
    SWIR_1 = "swir_1"
    SWIR_2 = "swir_2"
    THERMAL_1 = "thermal_1"
    THERMAL_2 = "thermal_2"
    CIRRUS = "cirrus"
    WATER_VAPOUR = "water_vapour"
    PANCHROMATIC = "panchromatic"
    QA_PIXEL = "qa_pixel"
    QA_RADSAT = "qa_radsat"
    QA_AEROSOL = "qa_aerosol"
    SCL = "scl"
    SAR_VV = "sar_vv"
    SAR_VH = "sar_vh"
    SAR_HH = "sar_hh"
    SAR_HV = "sar_hv"


class ProductLevel(str, Enum):
    L1_MSS = "L1_MSS"
    L1C_TOA = "L1C_TOA"
    L2A_BOA = "L2A_BOA"
    L2_SR = "L2_SR"
    L2_ST = "L2_ST"
    L1T = "L1T"
    AST_07 = "AST_07"
    AST_08 = "AST_08"
    L1_GRD = "L1_GRD"
    L1_SLC = "L1_SLC"
    L2A_HYPER = "L2A_HYPER"
    UNKNOWN = "UNKNOWN"


class SensorFamily(str, Enum):
    LANDSAT = "Landsat"
    SENTINEL_2 = "Sentinel-2"
    ASTER = "ASTER"
    SENTINEL_1 = "Sentinel-1"
    ENMAP = "EnMAP"
    PRISMA = "PRISMA"
    EMIT = "EMIT"
    ALOS_PALSAR = "ALOS PALSAR"
    UNKNOWN = "Unknown"


@dataclass
class BandAsset:
    role: BandRole
    file_path: Path
    band_name: str
    center_wavelength_nm: Optional[float] = None
    resolution_m: Optional[float] = None
    scale_factor: float = 1.0
    offset: float = 0.0
    valid_min: Optional[float] = None
    valid_max: Optional[float] = None
    nodata: Optional[float] = None
    unit: str = "reflectance"
    is_thermal: bool = False
    calibration_provenance: str = 'Product parser profile and official product guide; not claimed as an extracted metadata key'

    def to_dict(self) -> Dict[str, Any]:
        return {
            "role": self.role.value,
            "file_name": self.file_path.name,
            "band_name": self.band_name,
            "center_wavelength_nm": self.center_wavelength_nm,
            "resolution_m": self.resolution_m,
            "scale_factor": self.scale_factor,
            "offset": self.offset,
            "valid_min": self.valid_min,
            "valid_max": self.valid_max,
            "nodata": self.nodata,
            "unit": self.unit,
            "is_thermal": self.is_thermal,
            "calibration_provenance": self.calibration_provenance,
        }


@dataclass
class QualityAsset:
    role: str
    file_path: Path
    description: str = ""
    flags_info: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "role": self.role,
            "file_name": self.file_path.name,
            "description": self.description,
            "flags_info": self.flags_info,
        }


@dataclass
class SceneMetadata:
    scene_id: str
    sensor_family: SensorFamily
    sensor_id: str
    platform: str
    instrument: str
    product_level: ProductLevel
    acquisition_date: Optional[datetime] = None
    sun_elevation_deg: Optional[float] = None
    sun_azimuth_deg: Optional[float] = None
    cloud_cover_percent: Optional[float] = None
    metadata_file: Optional[Path] = None
    warnings: List[str] = field(default_factory=list)
    restrictions: List[str] = field(default_factory=list)
    source_scene_id: Optional[str] = None
    product_id: Optional[str] = None
    collection: Optional[str] = None
    processing_level: Optional[str] = None
    processing_date: Optional[str] = None
    product_generation: Optional[str] = None
    radiometric_unit: Optional[str] = None
    wrs_path: Optional[int] = None
    wrs_row: Optional[int] = None
    ground_station: Optional[str] = None
    archive_version: Optional[str] = None
    calibration_fields: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "scene_id": self.scene_id,
            "sensor_family": self.sensor_family.value,
            "sensor_id": self.sensor_id,
            "platform": self.platform,
            "instrument": self.instrument,
            "product_level": self.product_level.value,
            "acquisition_date": self.acquisition_date.isoformat() if self.acquisition_date else None,
            "sun_elevation_deg": self.sun_elevation_deg,
            "sun_azimuth_deg": self.sun_azimuth_deg,
            "cloud_cover_percent": self.cloud_cover_percent,
            "metadata_file": str(self.metadata_file) if self.metadata_file else None,
            "warnings": self.warnings,
            "restrictions": self.restrictions,
            **{name:getattr(self,name) for name in ('source_scene_id','product_id','collection','processing_level',
                'processing_date','product_generation','radiometric_unit','wrs_path','wrs_row','ground_station',
                'archive_version','calibration_fields')},
        }


@dataclass
class SceneInfo:
    scene_path: Path
    metadata: SceneMetadata
    bands: Dict[BandRole, BandAsset] = field(default_factory=dict)
    quality_masks: Dict[str, QualityAsset] = field(default_factory=dict)
    expert_mapped: bool = False

    def has_role(self, role: BandRole) -> bool:
        return role in self.bands and self.bands[role].file_path.exists()

    def get_band(self, role: BandRole) -> Optional[BandAsset]:
        return self.bands.get(role)

    def has_thermal(self) -> bool:
        return any(b.is_thermal for b in self.bands.values())

    def to_dict(self) -> Dict[str, Any]:
        return {
            "scene_path": str(self.scene_path),
            "metadata": self.metadata.to_dict(),
            "bands": {k.value: v.to_dict() for k, v in self.bands.items()},
            "quality_masks": {k: v.to_dict() for k, v in self.quality_masks.items()},
            "expert_mapped": self.expert_mapped,
        }

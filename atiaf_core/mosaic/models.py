"""Data models and configuration for multi-scene quality-aware mosaic blending."""

from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional


class MosaicStrategy(str, Enum):
    """Pixel selection and blending strategies for multi-scene mosaics."""
    HIGHEST_QUALITY = "highest_quality"  # Uses clear QA pixels, ranks clear > shadow > cloud
    MEAN_VALID = "mean_valid"            # Calculates mathematical mean across valid overlapping pixels
    LATEST_DATE = "latest_date"          # Prioritizes the most recently acquired scene
    FIRST_VALID = "first_valid"          # Fast first non-nodata pixel


@dataclass
class SceneContribution:
    """Metadata describing a single scene's contribution to the mosaic."""
    scene_id: str
    acquisition_date: str
    numeric_id: int
    raster_path: Path
    qa_path: Optional[Path] = None


@dataclass
class MosaicResult:
    """Result of a quality-aware multi-scene mosaic operation."""
    mosaic_id: str
    product_name: str
    category: str
    full_path: str
    clipped_path: Optional[str]
    provenance_path: str
    scene_contributions: List[Dict[str, Any]]
    statistics: Dict[str, float]
    valid_pixels: int
    nodata_pixels: int

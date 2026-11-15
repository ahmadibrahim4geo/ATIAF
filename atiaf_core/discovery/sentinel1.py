# -*- coding: utf-8 -*-
"""Parser and asset mapper for Copernicus Sentinel-1 C-SAR products."""

from datetime import datetime
from pathlib import Path
import re
from typing import Any, Dict, List, Optional
import xml.etree.ElementTree as ET

from atiaf_core.discovery.models import (
    BandAsset,
    BandRole,
    ProductLevel,
    QualityAsset,
    SceneInfo,
    SceneMetadata,
    SensorFamily,
)


class Sentinel1Parser:
    """Discovers and parses Sentinel-1 C-SAR products (.SAFE directory or unpacked structure)."""

    POLARIZATION_MAP = {
        "vv": BandRole.SAR_VV,
        "vh": BandRole.SAR_VH,
        "hh": BandRole.SAR_HH,
        "hv": BandRole.SAR_HV,
    }

    @classmethod
    def can_parse(cls, folder: Path) -> bool:
        """Determines if the directory is a Sentinel-1 product."""
        if not folder.is_dir():
            return False

        name_upper = folder.name.upper()
        if name_upper.startswith(("S1A_", "S1B_", "S1_")):
            return True

        manifest = folder / "manifest.safe"
        if manifest.is_file():
            try:
                txt = manifest.read_text(encoding="utf-8", errors="ignore")[:1000]
                if "SENTINEL-1" in txt.upper() or "SAR" in txt.upper():
                    return True
            except Exception:
                pass

        # Check for measurement folder or S1 tiff files
        meas_dir = folder / "measurement"
        if meas_dir.is_dir():
            if list(meas_dir.glob("s1*.tiff")) or list(meas_dir.glob("s1*.tif")):
                return True

        if list(folder.glob("s1[ab]*.tiff")) or list(folder.glob("s1[ab]*.tif")):
            return True

        return False

    @classmethod
    def parse(cls, folder: Path) -> Optional[SceneInfo]:
        """Parses the Sentinel-1 scene directory and discovers polarimetric bands."""
        if not cls.can_parse(folder):
            return None

        scene_id = folder.name
        if scene_id.endswith(".SAFE"):
            scene_id = scene_id[:-5]

        # Extract satellite platform
        platform = "Sentinel-1"
        sensor_id = "C-SAR"
        if scene_id.upper().startswith("S1A"):
            platform = "Sentinel-1A"
        elif scene_id.upper().startswith("S1B"):
            platform = "Sentinel-1B"

        # Determine product level (GRD vs SLC)
        product_level = ProductLevel.L1_GRD
        if "_SLC" in scene_id.upper():
            product_level = ProductLevel.L1_SLC

        acq_date = None
        manifest_file = folder / "manifest.safe"
        if not manifest_file.is_file():
            candidates = list(folder.glob("manifest.safe")) or list(folder.rglob("manifest.safe"))
            manifest_file = candidates[0] if candidates else None

        # Parse date from manifest or filename
        if manifest_file and manifest_file.is_file():
            try:
                tree = ET.parse(manifest_file)
                root = tree.getroot()
                # Find start time
                for elem in root.iter():
                    if "startTime" in elem.tag and elem.text:
                        acq_date = datetime.fromisoformat(elem.text.strip().replace("Z", "+00:00"))
                        break
            except Exception:
                pass

        if acq_date is None:
            # S1A_IW_GRDH_1SDV_20230715T160000...
            m = re.search(r"_(\d{8}T\d{6})_", scene_id)
            if m:
                try:
                    acq_date = datetime.strptime(m.group(1), "%Y%m%dT%H%M%S")
                except ValueError:
                    pass

        metadata = SceneMetadata(
            scene_id=scene_id,
            sensor_family=SensorFamily.SENTINEL_1,
            sensor_id=sensor_id,
            platform=platform,
            instrument="C-SAR",
            product_level=product_level,
            acquisition_date=acq_date,
            metadata_file=manifest_file,
            warnings=["SAR microwave data: optical surface reflectance equations not applicable."],
            restrictions=["Dedicated SAR calibration/polarimetric analysis only."],
        )

        bands: Dict[BandRole, BandAsset] = {}

        # Search measurement directory or current folder for tiff/jp2 files
        search_dirs = [folder / "measurement", folder]
        for s_dir in search_dirs:
            if not s_dir.is_dir():
                continue
            for f in sorted(list(s_dir.glob("*.tiff")) + list(s_dir.glob("*.tif"))):
                f_name = f.name.lower()
                for pol_key, role in cls.POLARIZATION_MAP.items():
                    if f"-{pol_key}-" in f_name or f"_{pol_key}_" in f_name or f_name.endswith(f"_{pol_key}.tif"):
                        bands[role] = BandAsset(
                            role=role,
                            file_path=f,
                            band_name=pol_key.upper(),
                            resolution_m=10.0 if "grd" in f_name else 20.0,
                            scale_factor=1.0,
                            offset=0.0,
                            nodata=0.0,
                            unit="linear_amplitude",
                            is_thermal=False,
                        )

        return SceneInfo(
            scene_path=folder,
            metadata=metadata,
            bands=bands,
            quality_masks={},
            expert_mapped=False,
        )

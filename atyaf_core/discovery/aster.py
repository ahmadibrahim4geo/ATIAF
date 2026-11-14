"""Parser and asset mapper for NASA/METI ASTER products on Terra."""

from datetime import datetime
import json
from pathlib import Path
import re
from typing import Any, Dict, List, Optional, Tuple

from atyaf_core.discovery.models import (
    BandAsset,
    BandRole,
    ProductLevel,
    QualityAsset,
    SceneInfo,
    SceneMetadata,
    SensorFamily,
)


class AsterParser:
    """Discovers and parses ASTER scenes (L1T, AST_07, AST_08)."""

    # Scientific thresholds
    SWIR_DEGRADATION_DATE = datetime(2008, 4, 1)
    TIR_END_OPERATIONS_DATE = datetime(2026, 1, 16)

    @classmethod
    def can_parse(cls, folder: Path) -> bool:
        """Determines if the directory contains ASTER metadata or assets."""
        if not folder.is_dir():
            return False
        # Look for ASTER files: must be actual files, not child subdirectories
        aster_files = [
            p
            for p in folder.glob("*")
            if p.is_file()
            and (
                p.suffix.lower() in (".met", ".hdf", ".h5")
                or (
                    p.suffix.lower() in (".tif", ".tiff")
                    and any(b in p.name.upper() for b in ["B01", "B1", "VNIR", "TIR", "AST"])
                )
            )
        ]
        return len(aster_files) > 0

    @classmethod
    def parse(cls, folder: Path) -> Optional[SceneInfo]:
        """Parses ASTER scene directory, metadata, and band assets."""
        meta_files = list(folder.glob("*.met")) + list(folder.glob("*.xml")) + list(folder.glob("*_met.txt"))
        meta_file = meta_files[0] if meta_files else None

        scene_id = folder.name
        prod_level = ProductLevel.UNKNOWN
        acq_date = None
        sun_elev = None
        sun_az = None
        cloud_cov = None

        # Determine level and scene ID
        folder_upper = folder.name.upper()
        if "AST_07" in folder_upper or "AST07" in folder_upper:
            prod_level = ProductLevel.AST_07
        elif "AST_08" in folder_upper or "AST08" in folder_upper:
            prod_level = ProductLevel.AST_08
        elif "AST_L1T" in folder_upper or "L1T" in folder_upper or "AST1T" in folder_upper:
            prod_level = ProductLevel.L1T

        # Parse text metadata if available
        if meta_file and meta_file.suffix.lower() in (".met", ".txt"):
            content = meta_file.read_text(encoding="utf-8", errors="replace")
            for line in content.splitlines():
                line = line.strip()
                if "CALENDARDATE" in line or "ACQUISITIONDATE" in line or "STARTDATE" in line:
                    match = re.search(r"\b(\d{4}-\d{2}-\d{2})\b", line)
                    if match:
                        try:
                            acq_date = datetime.strptime(match.group(1), "%Y-%m-%d")
                        except Exception:
                            pass
                if "SOLARZENITHANGLE" in line:
                    match = re.search(r"=\s*([0-9.]+)", line)
                    if match:
                        sun_elev = 90.0 - float(match.group(1))
                if "SOLARAZIMUTHANGLE" in line:
                    match = re.search(r"=\s*([0-9.]+)", line)
                    if match:
                        sun_az = float(match.group(1))

        if not acq_date:
            # Parse from scene ID date pattern e.g. AST_07_00305202005... or 20050520
            match = re.search(r"\b(20[0-2][0-9][0-1][0-9][0-3][0-9])\b", folder.name)
            if match:
                try:
                    acq_date = datetime.strptime(match.group(1), "%Y%m%d")
                except Exception:
                    pass

        warnings: List[str] = []
        restrictions: List[str] = []

        # Check SWIR physical degradation rule (April 2008)
        swir_degraded = False
        if acq_date and acq_date >= cls.SWIR_DEGRADATION_DATE:
            swir_degraded = True
            warnings.append(
                f"ASTER SWIR subsystem degraded after April 2008 (Acquisition: {acq_date.strftime('%Y-%m-%d')}). "
                "SWIR bands (B4-B9) are scientifically invalid and disabled for mineral and alteration ratios."
            )
            restrictions.append("ASTER_SWIR_INVALID_POST_2008")

        if acq_date and acq_date >= cls.TIR_END_OPERATIONS_DATE:
            warnings.append("ASTER TIR imaging ceased on January 16, 2026. No valid TIR data after this date.")
            restrictions.append("ASTER_TIR_POST_2026")

        metadata = SceneMetadata(
            scene_id=scene_id,
            sensor_family=SensorFamily.ASTER,
            sensor_id="ASTER_TERRA",
            platform="Terra",
            instrument="ASTER",
            product_level=prod_level,
            acquisition_date=acq_date,
            sun_elevation_deg=sun_elev,
            sun_azimuth_deg=sun_az,
            cloud_cover_percent=cloud_cov,
            metadata_file=meta_file,
            warnings=warnings,
            restrictions=restrictions,
        )

        bands, masks = cls._discover_bands(folder, prod_level, swir_degraded)

        return SceneInfo(
            scene_path=folder,
            metadata=metadata,
            bands=bands,
            quality_masks=masks,
            expert_mapped=False,
        )

    @classmethod
    def _discover_bands(
        cls, folder: Path, level: ProductLevel, swir_degraded: bool
    ) -> Tuple[Dict[BandRole, BandAsset], Dict[str, QualityAsset]]:
        bands: Dict[BandRole, BandAsset] = {}
        masks: Dict[str, QualityAsset] = {}

        raster_extensions = {".tif", ".tiff", ".hdf", ".h5"}
        files = [p for p in folder.glob("*") if p.suffix.lower() in raster_extensions]
        file_map = {f.name.upper(): f for f in files}

        def find_file(keyword: str) -> Optional[Path]:
            kw = keyword.upper()
            for name, path in file_map.items():
                if kw in name:
                    return path
            return None

        # VNIR bands (15m)
        vnir_defs = [
            (BandRole.GREEN, ["B01", "B1", "BAND1", "VNIR1"], "B1", 560.0, 15.0),
            (BandRole.RED, ["B02", "B2", "BAND2", "VNIR2"], "B2", 660.0, 15.0),
            (BandRole.NIR, ["B3N", "B03", "B3", "BAND3", "VNIR3"], "B3N", 810.0, 15.0),
        ]
        for role, kws, bname, wvl, res in vnir_defs:
            match = None
            for kw in kws:
                match = find_file(kw)
                if match:
                    break
            if match:
                bands[role] = BandAsset(
                    role=role,
                    file_path=match,
                    band_name=bname,
                    center_wavelength_nm=wvl,
                    resolution_m=res,
                    unit="reflectance" if level == ProductLevel.AST_07 else "radiance",
                    is_thermal=False,
                )

        # SWIR bands (30m) - only include if not degraded
        if not swir_degraded:
            swir_defs = [
                (BandRole.SWIR_1, ["B04", "B4", "BAND4", "SWIR4"], "B4", 1650.0, 30.0),
                (BandRole.SWIR_2, ["B05", "B5", "BAND5", "SWIR5"], "B5", 2165.0, 30.0),
            ]
            for role, kws, bname, wvl, res in swir_defs:
                match = None
                for kw in kws:
                    match = find_file(kw)
                    if match:
                        break
                if match:
                    bands[role] = BandAsset(
                        role=role,
                        file_path=match,
                        band_name=bname,
                        center_wavelength_nm=wvl,
                        resolution_m=res,
                        unit="reflectance" if level == ProductLevel.AST_07 else "radiance",
                        is_thermal=False,
                    )

        # TIR bands (90m) - or Kinetic Temperature in AST_08
        tir_defs = [
            (BandRole.THERMAL_1, ["B10", "BAND10", "TIR10", "TEMPERATURE", "KIN_TEMP"], "B10", 8300.0, 90.0),
            (BandRole.THERMAL_2, ["B13", "BAND13", "TIR13"], "B13", 10600.0, 90.0),
        ]
        for role, kws, bname, wvl, res in tir_defs:
            match = None
            for kw in kws:
                match = find_file(kw)
                if match:
                    break
            if match:
                is_temp = level == ProductLevel.AST_08 or "TEMP" in match.name.upper()
                bands[role] = BandAsset(
                    role=role,
                    file_path=match,
                    band_name=bname,
                    center_wavelength_nm=wvl,
                    resolution_m=res,
                    scale_factor=0.1 if is_temp else 1.0,
                    offset=0.0,
                    unit="Kelvin" if is_temp else "radiance",
                    is_thermal=True,
                )

        # QA file
        qa_file = find_file("QA") or find_file("QUALITY")
        if qa_file:
            masks["QA"] = QualityAsset(
                role="QA",
                file_path=qa_file,
                description="ASTER Quality Assessment plane",
            )

        return bands, masks

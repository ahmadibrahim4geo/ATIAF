"""Parser and asset mapper for USGS Landsat Collection 2 products."""

from datetime import datetime
import json
from pathlib import Path
import re
from typing import Any, Dict, Optional, Tuple

from atiaf_core.discovery.models import (
    BandAsset,
    BandRole,
    ProductLevel,
    QualityAsset,
    SceneInfo,
    SceneMetadata,
    SensorFamily,
)


class LandsatParser:
    """Discovers and parses USGS Landsat scenes (C2 L2 SR/ST and L1)."""

    SR_SCALE = 0.0000275
    SR_OFFSET = -0.2
    SR_NODATA = 0
    SR_VALID_MIN = 1
    SR_VALID_MAX = 65455

    ST_SCALE = 0.00341802
    ST_OFFSET = 149.0
    ST_NODATA = 0
    ST_VALID_MIN = 1
    ST_VALID_MAX = 65455

    @classmethod
    def can_parse(cls, folder: Path) -> bool:
        """Determines if the directory contains Landsat metadata or assets."""
        if not folder.is_dir():
            return False
        # Search for MTL file
        mtl_files = list(folder.glob("*_MTL.txt")) + list(folder.glob("*_MTL.json")) + list(folder.glob("*_MTL.xml"))
        if not mtl_files:
            mtl_files=[p for p in folder.glob('*.xml') if p.stat().st_size<4*1024*1024 and 'espa_metadata' in p.read_text('utf-8-sig')[:4096]]
        if mtl_files:
            return True
        # Check scene product filenames e.g. LC08_*, LC09_*, LE07_*, LT05_*
        tif_files = list(folder.glob("L[CEMT][0-9][0-9]_*.TIF")) + list(folder.glob("L[CEMT][0-9][0-9]_*.tif"))
        return len(tif_files) > 0

    @classmethod
    def parse_mtl_text(cls, mtl_path: Path) -> Dict[str, str]:
        """Parses standard USGS ODL/key-value MTL.txt file."""
        data = {}
        for line in mtl_path.read_text(encoding="utf-8", errors="replace").splitlines():
            line = line.strip()
            if "=" in line:
                key, val = line.split("=", 1)
                key = key.strip()
                val = val.strip().strip('"')
                data[key] = val
        return data

    @classmethod
    def parse(cls, folder: Path) -> Optional[SceneInfo]:
        """Parses the scene folder and extracts scene metadata and bands."""
        from atiaf_core.discovery.landsat_profiles import parse_profile
        profiled=parse_profile(folder)
        if profiled is not None:
            return profiled
        mtl_txt = list(folder.glob("*_MTL.txt"))
        mtl_json = list(folder.glob("*_MTL.json"))
        mtl_data: Dict[str, Any] = {}
        meta_file: Optional[Path] = None

        if mtl_json:
            meta_file = mtl_json[0]
            try:
                raw_json = json.loads(meta_file.read_text(encoding="utf-8"))
                # USGS nested JSON has LANDSAT_METADATA_FILE
                if "LANDSAT_METADATA_FILE" in raw_json:
                    for section in raw_json["LANDSAT_METADATA_FILE"].values():
                        if isinstance(section, dict):
                            mtl_data.update(section)
                else:
                    mtl_data.update(raw_json)
            except Exception:
                mtl_data = {}

        if not mtl_data and mtl_txt:
            meta_file = mtl_txt[0]
            mtl_data = cls.parse_mtl_text(meta_file)

        # Extract basic identity
        product_id = mtl_data.get("LANDSAT_PRODUCT_ID")
        if not product_id:
            # Fall back to inferring from file names
            tifs = list(folder.glob("L[CEMT][0-9][0-9]_*.TIF")) + list(folder.glob("L[CEMT][0-9][0-9]_*.tif"))
            if tifs:
                match = re.match(r"(L[CEMT][0-9]{2}_[A-Z0-9]{4}_[0-9]{6}_[0-9]{8}_[0-9]{8}_[0-9]{2}_[A-Z0-9]{2})", tifs[0].name)
                if match:
                    product_id = match.group(1)
        if not product_id:
            product_id = folder.name

        spacecraft = mtl_data.get("SPACECRAFT_ID", "").upper()
        sensor = mtl_data.get("SENSOR_ID", "").upper()
        proc_level = mtl_data.get("PROCESSING_LEVEL", "").upper()

        # Infer from product ID if missing from MTL
        if not spacecraft and len(product_id) >= 4:
            prefix = product_id[:4]
            if prefix.startswith("LC08") or prefix.startswith("LO08"):
                spacecraft = "LANDSAT_8"
                sensor = "OLI_TIRS" if prefix.startswith("LC") else "OLI"
            elif prefix.startswith("LC09") or prefix.startswith("LO09"):
                spacecraft = "LANDSAT_9"
                sensor = "OLI_TIRS" if prefix.startswith("LC") else "OLI"
            elif prefix.startswith("LE07"):
                spacecraft = "LANDSAT_7"
                sensor = "ETM"
            elif prefix.startswith("LT05"):
                spacecraft = "LANDSAT_5"
                sensor = "TM"
            elif prefix.startswith("LT04"):
                spacecraft = "LANDSAT_4"
                sensor = "TM"
            elif prefix.startswith("LM"):
                num = product_id[2:4]
                spacecraft = f"LANDSAT_{int(num)}" if num.isdigit() else "LANDSAT_MSS"
                sensor = "MSS"

        # Determine Product Level
        if "L2" in proc_level or "_L2" in product_id:
            level = ProductLevel.L2_SR
        elif "MSS" in sensor or spacecraft.endswith("MSS") or product_id.startswith("LM"):
            level = ProductLevel.L1_MSS
        elif "L1" in proc_level or "_L1" in product_id:
            level = ProductLevel.L1T
        else:
            level = ProductLevel.UNKNOWN

        # Acquisition Date
        acq_date = None
        date_str = mtl_data.get("DATE_ACQUIRED")
        time_str = mtl_data.get("SCENE_CENTER_TIME")
        if date_str:
            try:
                if time_str:
                    time_clean = time_str.split(".")[0].rstrip("Z")
                    acq_date = datetime.strptime(f"{date_str} {time_clean}", "%Y-%m-%d %H:%M:%S")
                else:
                    acq_date = datetime.strptime(date_str, "%Y-%m-%d")
            except Exception:
                pass
        if not acq_date:
            # Try parsing from product_id date field
            parts = product_id.split("_")
            if len(parts) >= 4 and len(parts[3]) == 8 and parts[3].isdigit():
                try:
                    acq_date = datetime.strptime(parts[3], "%Y%m%d")
                except Exception:
                    pass

        sun_elev = float(mtl_data["SUN_ELEVATION"]) if "SUN_ELEVATION" in mtl_data else None
        sun_az = float(mtl_data["SUN_AZIMUTH"]) if "SUN_AZIMUTH" in mtl_data else None
        cloud_cov = float(mtl_data["CLOUD_COVER"]) if "CLOUD_COVER" in mtl_data else None

        warnings = []
        restrictions = []

        if level == ProductLevel.L1_MSS:
            warnings.append("Landsat MSS has no SWIR or Thermal bands. SWIR indices and LST are unsupported.")
            restrictions.append("NO_SWIR")
            restrictions.append("NO_THERMAL")

        if spacecraft == "LANDSAT_7" and acq_date and acq_date.year >= 2003 and acq_date.month >= 5:
            warnings.append("Landsat 7 acquired after May 2003 has SLC-off scan-line gaps.")

        sensor_id_map = {
            "LANDSAT_8": "LANDSAT_OLI_TIRS_8",
            "LANDSAT_9": "LANDSAT_OLI2_TIRS2_9",
            "LANDSAT_7": "LANDSAT_ETM_7",
            "LANDSAT_5": "LANDSAT_TM_4_5",
            "LANDSAT_4": "LANDSAT_TM_4_5",
        }
        sensor_id = sensor_id_map.get(spacecraft, f"LANDSAT_{sensor}")

        metadata = SceneMetadata(
            scene_id=product_id,
            sensor_family=SensorFamily.LANDSAT,
            sensor_id=sensor_id,
            platform=spacecraft.replace("_", " ").title(),
            instrument=sensor,
            product_level=level,
            acquisition_date=acq_date,
            sun_elevation_deg=sun_elev,
            sun_azimuth_deg=sun_az,
            cloud_cover_percent=cloud_cov,
            metadata_file=meta_file,
            warnings=warnings,
            restrictions=restrictions,
        )

        bands, quality_masks = cls._discover_bands(folder, spacecraft, level)

        return SceneInfo(
            scene_path=folder,
            metadata=metadata,
            bands=bands,
            quality_masks=quality_masks,
            expert_mapped=False,
        )

    @classmethod
    def _discover_bands(
        cls, folder: Path, spacecraft: str, level: ProductLevel
    ) -> Tuple[Dict[BandRole, BandAsset], Dict[str, QualityAsset]]:
        bands: Dict[BandRole, BandAsset] = {}
        masks: Dict[str, QualityAsset] = {}

        # Collect all raster files
        files = list(folder.glob("*.TIF")) + list(folder.glob("*.tif"))
        file_map = {f.name.upper(): f for f in files}

        def find_file(suffix: str) -> Optional[Path]:
            suffix = suffix.upper()
            for name, path in file_map.items():
                if name.endswith(suffix):
                    return path
            return None

        is_oli = spacecraft in ("LANDSAT_8", "LANDSAT_9")
        is_tm_etm = spacecraft in ("LANDSAT_4", "LANDSAT_5", "LANDSAT_7")
        is_mss = "MSS" in spacecraft or spacecraft in ("LANDSAT_1", "LANDSAT_2", "LANDSAT_3")

        if is_oli and level == ProductLevel.L2_SR:
            role_specs = [
                (BandRole.COASTAL_AEROSOL, "_SR_B1.TIF", "B1", 443.0, 30.0, False),
                (BandRole.BLUE, "_SR_B2.TIF", "B2", 482.0, 30.0, False),
                (BandRole.GREEN, "_SR_B3.TIF", "B3", 561.0, 30.0, False),
                (BandRole.RED, "_SR_B4.TIF", "B4", 655.0, 30.0, False),
                (BandRole.NIR, "_SR_B5.TIF", "B5", 865.0, 30.0, False),
                (BandRole.SWIR_1, "_SR_B6.TIF", "B6", 1609.0, 30.0, False),
                (BandRole.SWIR_2, "_SR_B7.TIF", "B7", 2201.0, 30.0, False),
                (BandRole.THERMAL_1, "_ST_B10.TIF", "B10", 10895.0, 100.0, True),
            ]
            for role, suffix, bname, wvl, res, is_therm in role_specs:
                path = find_file(suffix)
                if path:
                    scale = cls.ST_SCALE if is_therm else cls.SR_SCALE
                    offset = cls.ST_OFFSET if is_therm else cls.SR_OFFSET
                    unit = "Kelvin" if is_therm else "reflectance"
                    bands[role] = BandAsset(
                        role=role,
                        file_path=path,
                        band_name=bname,
                        center_wavelength_nm=wvl,
                        resolution_m=res,
                        scale_factor=scale,
                        offset=offset,
                        valid_min=cls.ST_VALID_MIN if is_therm else cls.SR_VALID_MIN,
                        valid_max=cls.ST_VALID_MAX if is_therm else cls.SR_VALID_MAX,
                        nodata=cls.ST_NODATA if is_therm else cls.SR_NODATA,
                        unit=unit,
                        is_thermal=is_therm,
                    )

        elif is_tm_etm and level == ProductLevel.L2_SR:
            role_specs = [
                (BandRole.BLUE, "_SR_B1.TIF", "B1", 485.0, 30.0, False),
                (BandRole.GREEN, "_SR_B2.TIF", "B2", 560.0, 30.0, False),
                (BandRole.RED, "_SR_B3.TIF", "B3", 660.0, 30.0, False),
                (BandRole.NIR, "_SR_B4.TIF", "B4", 830.0, 30.0, False),
                (BandRole.SWIR_1, "_SR_B5.TIF", "B5", 1650.0, 30.0, False),
                (BandRole.THERMAL_1, "_ST_B6.TIF", "B6", 11450.0, 60.0 if spacecraft == "LANDSAT_7" else 120.0, True),
                (BandRole.SWIR_2, "_SR_B7.TIF", "B7", 2215.0, 30.0, False),
            ]
            for role, suffix, bname, wvl, res, is_therm in role_specs:
                path = find_file(suffix)
                if path:
                    scale = cls.ST_SCALE if is_therm else cls.SR_SCALE
                    offset = cls.ST_OFFSET if is_therm else cls.SR_OFFSET
                    unit = "Kelvin" if is_therm else "reflectance"
                    bands[role] = BandAsset(
                        role=role,
                        file_path=path,
                        band_name=bname,
                        center_wavelength_nm=wvl,
                        resolution_m=res,
                        scale_factor=scale,
                        offset=offset,
                        valid_min=cls.ST_VALID_MIN if is_therm else cls.SR_VALID_MIN,
                        valid_max=cls.ST_VALID_MAX if is_therm else cls.SR_VALID_MAX,
                        nodata=cls.ST_NODATA if is_therm else cls.SR_NODATA,
                        unit=unit,
                        is_thermal=is_therm,
                    )

        elif is_mss:
            # MSS Level-1 bands
            mss_specs = [
                (BandRole.GREEN, "_B4.TIF", "B4", 550.0, 60.0),
                (BandRole.RED, "_B5.TIF", "B5", 650.0, 60.0),
                (BandRole.NIR, "_B6.TIF", "B6", 750.0, 60.0),
                (BandRole.NARROW_NIR, "_B7.TIF", "B7", 900.0, 60.0),
            ]
            for role, suffix, bname, wvl, res in mss_specs:
                path = find_file(suffix) or find_file(f"_B0{bname[1]}.TIF")
                if path:
                    bands[role] = BandAsset(
                        role=role,
                        file_path=path,
                        band_name=bname,
                        center_wavelength_nm=wvl,
                        resolution_m=res,
                        unit="DN",
                        is_thermal=False,
                    )

        # Quality masks
        qa_pixel = find_file("_QA_PIXEL.TIF")
        if qa_pixel:
            masks["QA_PIXEL"] = QualityAsset(
                role="QA_PIXEL",
                file_path=qa_pixel,
                description="USGS Collection 2 Surface Reflectance pixel quality bitmask (cloud, shadow, dilated, cirrus, snow, water)",
                flags_info={
                    "fill_bit": 0,
                    "dilated_cloud_bit": 1,
                    "cirrus_bit": 2,
                    "cloud_bit": 3,
                    "cloud_shadow_bit": 4,
                    "snow_bit": 5,
                    "clear_bit": 6,
                    "water_bit": 7,
                },
            )

        qa_radsat = find_file("_QA_RADSAT.TIF")
        if qa_radsat:
            masks["QA_RADSAT"] = QualityAsset(
                role="QA_RADSAT",
                file_path=qa_radsat,
                description="Radiometric saturation quality bitmask",
            )

        qa_aerosol = find_file("_QA_AEROSOL.TIF")
        if qa_aerosol:
            masks["QA_AEROSOL"] = QualityAsset(
                role="QA_AEROSOL",
                file_path=qa_aerosol,
                description="Surface reflectance aerosol quality bitmask",
            )

        return bands, masks

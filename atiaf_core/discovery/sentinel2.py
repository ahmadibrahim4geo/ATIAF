"""Parser and asset mapper for Copernicus Sentinel-2 MSI products."""

from datetime import datetime
from pathlib import Path
import re
from typing import Any, Dict, List, Optional, Tuple
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


class Sentinel2Parser:
    """Discovers and parses Sentinel-2 MSI products (.SAFE structure or unpacked flat)."""

    DEFAULT_SCALE = 0.0001  # 1 / 10000
    DEFAULT_OFFSET = 0.0
    DEFAULT_NODATA = 0

    @classmethod
    def can_parse(cls, folder: Path) -> bool:
        """Determines if the directory contains Sentinel-2 metadata or bands."""
        if not folder.is_dir():
            return False
        # SAFE directory format
        if folder.name.endswith(".SAFE") or (folder / "manifest.safe").is_file():
            return True
        # Check XML metadata
        if list(folder.glob("MTD_MSIL*.xml")) or list(folder.glob("*MTD*.xml")):
            return True
        # Check files matching S2 naming convention in current directory
        s2_patterns = ["*B0[1-9]*.jp2", "*B[1-8][0-2A]*.jp2", "*B0[1-9]*.tif", "*B[1-8][0-2A]*.tif"]
        for pat in s2_patterns:
            if list(folder.glob(pat)):
                return True
        return False

    @classmethod
    def parse(cls, folder: Path) -> Optional[SceneInfo]:
        """Parses the Sentinel-2 scene directory and extracts metadata and bands."""
        # Check for root metadata XML
        mtd_files = list(folder.glob("MTD_MSIL*.xml"))
        if not mtd_files:
            mtd_files = list(folder.rglob("MTD_MSIL*.xml"))
        if not mtd_files:
            mtd_files = list(folder.glob("manifest.safe"))

        meta_file = mtd_files[0] if mtd_files else None

        scene_id = folder.name
        if scene_id.endswith(".SAFE"):
            scene_id = scene_id[:-5]

        platform = "Sentinel-2"
        proc_level = ProductLevel.UNKNOWN
        acq_date = None
        sun_elev = None
        sun_az = None
        cloud_cov = None
        scale = cls.DEFAULT_SCALE
        offset = cls.DEFAULT_OFFSET

        # Parse XML if available
        if meta_file and meta_file.name.endswith(".xml"):
            try:
                tree = ET.parse(meta_file)
                root = tree.getroot()

                # Extract Product ID
                prod_node = root.find(".//PRODUCT_URI")
                if prod_node is None:
                    prod_node = root.find(".//PRODUCT_NAME")
                if prod_node is not None and prod_node.text:
                    scene_id = prod_node.text.replace(".SAFE", "")

                # Extract Platform (S2A, S2B, S2C)
                plat_node = root.find(".//SPACECRAFT_NAME")
                if plat_node is not None and plat_node.text:
                    platform = plat_node.text.strip()

                # Extract Processing Level
                level_node = root.find(".//PROCESSING_LEVEL")
                if level_node is not None and level_node.text:
                    lvl_text = level_node.text.strip().upper()
                    if "2A" in lvl_text or "L2A" in lvl_text:
                        proc_level = ProductLevel.L2A_BOA
                    elif "1C" in lvl_text or "L1C" in lvl_text:
                        proc_level = ProductLevel.L1C_TOA

                # Acquisition Datetime
                time_node = root.find(".//PRODUCT_START_TIME")
                if time_node is None:
                    time_node = root.find(".//DATATAKE_SENSING_START")
                if time_node is not None and time_node.text:
                    try:
                        clean_time = time_node.text.split(".")[0].rstrip("Z")
                        acq_date = datetime.fromisoformat(clean_time)
                    except Exception:
                        pass

                # Sun angles
                zenith_node = root.find(".//Mean_Sun_Angle/ZENITH_ANGLE")
                azimuth_node = root.find(".//Mean_Sun_Angle/AZIMUTH_ANGLE")
                if zenith_node is not None and zenith_node.text:
                    zenith = float(zenith_node.text)
                    sun_elev = 90.0 - zenith
                if azimuth_node is not None and azimuth_node.text:
                    sun_az = float(azimuth_node.text)

                # Cloud Cover
                cloud_node = root.find(".//Cloud_Coverage_Assessment")
                if cloud_node is not None and cloud_node.text:
                    cloud_cov = float(cloud_node.text)

                # Baseline radiometric offset check (N0400+)
                offset_node = root.find(".//BOA_ADD_OFFSET")
                if offset_node is not None and offset_node.text:
                    offset = float(offset_node.text) * scale
            except Exception:
                pass

        # If metadata XML didn't give full info, extract from product title
        if proc_level == ProductLevel.UNKNOWN:
            if "MSIL2A" in scene_id or "_L2A_" in scene_id:
                proc_level = ProductLevel.L2A_BOA
            elif "MSIL1C" in scene_id or "_L1C_" in scene_id:
                proc_level = ProductLevel.L1C_TOA

        if "S2A_" in scene_id:
            platform = "Sentinel-2A"
        elif "S2B_" in scene_id:
            platform = "Sentinel-2B"
        elif "S2C_" in scene_id:
            platform = "Sentinel-2C"

        if not acq_date:
            match = re.search(r"_(\d{8}T\d{6})_", scene_id)
            if match:
                try:
                    acq_date = datetime.strptime(match.group(1), "%Y%m%dT%H%M%S")
                except Exception:
                    pass

        warnings: List[str] = [
            "Sentinel-2 MSI has NO thermal bands. Surface Temperature (LST) calculations are strictly unsupported."
        ]
        restrictions: List[str] = ["NO_THERMAL"]

        if proc_level == ProductLevel.L1C_TOA:
            warnings.append(
                "Detected Sentinel-2 Level-1C (TOA Reflectance). Surface reflectance indices require atmospheric correction."
            )
            restrictions.append("TOA_ONLY_WARNING")

        metadata = SceneMetadata(
            scene_id=scene_id,
            sensor_family=SensorFamily.SENTINEL_2,
            sensor_id="SENTINEL_2_MSI",
            platform=platform,
            instrument="MSI",
            product_level=proc_level,
            acquisition_date=acq_date,
            sun_elevation_deg=sun_elev,
            sun_azimuth_deg=sun_az,
            cloud_cover_percent=cloud_cov,
            metadata_file=meta_file,
            warnings=warnings,
            restrictions=restrictions,
        )

        bands, masks = cls._discover_bands(folder, scale, offset)

        return SceneInfo(
            scene_path=folder,
            metadata=metadata,
            bands=bands,
            quality_masks=masks,
            expert_mapped=False,
        )

    @classmethod
    def _discover_bands(
        cls, folder: Path, scale: float, offset: float
    ) -> Tuple[Dict[BandRole, BandAsset], Dict[str, QualityAsset]]:
        bands: Dict[BandRole, BandAsset] = {}
        masks: Dict[str, QualityAsset] = {}

        # Look for band files recursively (.jp2, .tif, .tiff)
        raster_extensions = {".jp2", ".tif", ".tiff"}
        all_rasters = [p for p in folder.rglob("*") if p.suffix.lower() in raster_extensions]

        # Definitions for Sentinel-2 bands
        band_defs = [
            (BandRole.COASTAL_AEROSOL, ["B01", "B1"], "B01", 442.7, 60.0),
            (BandRole.BLUE, ["B02", "B2"], "B02", 492.4, 10.0),
            (BandRole.GREEN, ["B03", "B3"], "B03", 559.8, 10.0),
            (BandRole.RED, ["B04", "B4"], "B04", 664.6, 10.0),
            (BandRole.RED_EDGE_1, ["B05", "B5"], "B05", 704.1, 20.0),
            (BandRole.RED_EDGE_2, ["B06", "B6"], "B06", 740.5, 20.0),
            (BandRole.RED_EDGE_3, ["B07", "B7"], "B07", 782.8, 20.0),
            (BandRole.NIR, ["B08", "B8"], "B08", 832.8, 10.0),
            (BandRole.NARROW_NIR, ["B8A"], "B8A", 864.7, 20.0),
            (BandRole.WATER_VAPOUR, ["B09", "B9"], "B09", 945.1, 60.0),
            (BandRole.CIRRUS, ["B10"], "B10", 1373.5, 60.0),
            (BandRole.SWIR_1, ["B11"], "B11", 1613.7, 20.0),
            (BandRole.SWIR_2, ["B12"], "B12", 2202.4, 20.0),
        ]

        # Prioritize 10m/20m over 60m when multiple resolutions exist
        def score_path(p: Path) -> int:
            name = p.name.upper()
            if "R10M" in str(p).upper():
                return 3
            if "R20M" in str(p).upper():
                return 2
            if "R60M" in str(p).upper():
                return 1
            return 0

        for role, patterns, bname, wvl, res in band_defs:
            matches = []
            for p in all_rasters:
                stem = p.stem.upper()
                # Check for exact band pattern e.g. _B02_ or _B02 or -B02
                for pat in patterns:
                    if re.search(rf"(?:^|[_\-]){pat}(?:[_\-.]|$)", stem):
                        matches.append(p)
                        break
            if matches:
                # Pick highest priority resolution
                best = max(matches, key=score_path)
                bands[role] = BandAsset(
                    role=role,
                    file_path=best,
                    band_name=bname,
                    center_wavelength_nm=wvl,
                    resolution_m=res,
                    scale_factor=scale,
                    offset=offset,
                    valid_min=1,
                    valid_max=10000,
                    nodata=cls.DEFAULT_NODATA,
                    unit="reflectance",
                    is_thermal=False,
                )

        # Look for Scene Classification Layer (SCL)
        for p in all_rasters:
            if "SCL" in p.stem.upper():
                masks["SCL"] = QualityAsset(
                    role="SCL",
                    file_path=p,
                    description="Sentinel-2 Scene Classification Layer (categorical: 3=cloud shadow, 4=vegetation, 5=bare soil, 6=water, 7=unclassified, 8=cloud medium prob, 9=cloud high prob, 10=thin cirrus, 11=snow)",
                    flags_info={
                        "0": "NO_DATA",
                        "1": "SATURATED_OR_DEFECTIVE",
                        "2": "DARK_AREA_PIXELS",
                        "3": "CLOUD_SHADOWS",
                        "4": "VEGETATION",
                        "5": "NOT_VEGETATED",
                        "6": "WATER",
                        "7": "UNCLASSIFIED",
                        "8": "CLOUD_MEDIUM_PROBABILITY",
                        "9": "CLOUD_HIGH_PROBABILITY",
                        "10": "THIN_CIRRUS",
                        "11": "SNOW",
                    },
                )
                break

        return bands, masks

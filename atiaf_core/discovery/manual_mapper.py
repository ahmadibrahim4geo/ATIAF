"""Expert Manual Band Mapping interface and validator."""

from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional

from atiaf_core.discovery.models import (
    BandAsset,
    BandRole,
    ProductLevel,
    SceneInfo,
    SceneMetadata,
    SensorFamily,
)


class ManualBandMapper:
    """Allows expert users to manually map physical raster bands when auto-detection
    is unavailable or when custom band files are provided.
    """

    # Reference wavelengths for common physical roles (nm)
    ROLE_REFERENCE_WAVELENGTHS = {
        BandRole.COASTAL_AEROSOL: 443.0,
        BandRole.BLUE: 490.0,
        BandRole.GREEN: 560.0,
        BandRole.RED: 665.0,
        BandRole.RED_EDGE_1: 705.0,
        BandRole.RED_EDGE_2: 740.0,
        BandRole.RED_EDGE_3: 783.0,
        BandRole.NIR: 842.0,
        BandRole.NARROW_NIR: 865.0,
        BandRole.WATER_VAPOUR: 945.0,
        BandRole.CIRRUS: 1375.0,
        BandRole.SWIR_1: 1610.0,
        BandRole.SWIR_2: 2190.0,
        BandRole.THERMAL_1: 10800.0,
        BandRole.THERMAL_2: 12000.0,
    }

    @classmethod
    def create_custom_scene(
        cls,
        scene_path: Path,
        scene_id: str,
        platform_name: str,
        instrument_name: str,
        product_level: ProductLevel,
        mappings: Dict[BandRole, Path],
        scale_factors: Optional[Dict[BandRole, float]] = None,
        offsets: Optional[Dict[BandRole, float]] = None,
        units: Optional[Dict[BandRole, str]] = None,
        acquisition_date: Optional[datetime] = None,
    ) -> SceneInfo:
        """Constructs and validates a SceneInfo from user-defined manual band mappings."""
        scale_factors = scale_factors or {}
        offsets = offsets or {}
        units = units or {}

        warnings: List[str] = [
            "Scene configured via Expert Manual Band Mapping. Verify band calibrations and units."
        ]
        restrictions: List[str] = []

        bands: Dict[BandRole, BandAsset] = {}

        for role, file_path in mappings.items():
            file_path = Path(file_path).resolve()
            if not file_path.is_file():
                warnings.append(f"Mapped band file not found: {file_path}")
                continue

            is_therm = role in (BandRole.THERMAL_1, BandRole.THERMAL_2)
            default_unit = "Kelvin" if is_therm else ("reflectance" if "L2" in product_level.value or "AST_07" in product_level.value else "DN")
            unit = units.get(role, default_unit)
            scale = scale_factors.get(role, 1.0)
            offset = offsets.get(role, 0.0)
            wvl = cls.ROLE_REFERENCE_WAVELENGTHS.get(role)

            bands[role] = BandAsset(
                role=role,
                file_path=file_path,
                band_name=f"USER_{role.value.upper()}",
                center_wavelength_nm=wvl,
                scale_factor=scale,
                offset=offset,
                unit=unit,
                is_thermal=is_therm,
            )

        metadata = SceneMetadata(
            scene_id=scene_id,
            sensor_family=SensorFamily.UNKNOWN,
            sensor_id=f"EXPERT_{instrument_name.upper()}",
            platform=platform_name,
            instrument=instrument_name,
            product_level=product_level,
            acquisition_date=acquisition_date,
            warnings=warnings,
            restrictions=restrictions,
        )

        return SceneInfo(
            scene_path=scene_path,
            metadata=metadata,
            bands=bands,
            quality_masks={},
            expert_mapped=True,
        )

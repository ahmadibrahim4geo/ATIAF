"""Geological and mineral index registry and mathematical definitions."""

from dataclasses import dataclass
from typing import Callable, Dict, List
import numpy as np

from atiaf_core.discovery.models import BandRole


@dataclass
class GeologicalIndexDefinition:
    id: str
    acronym: str
    name_en: str
    name_ar: str
    target_mineral: str
    required_roles: List[BandRole]
    compute_fn: Callable[..., np.ndarray]
    formula_text: str
    requires_swir: bool = False
    requires_thermal: bool = False
    citation: str = ""
    notes: str = ""


def _safe_ratio(num: np.ndarray, denom: np.ndarray) -> np.ndarray:
    with np.errstate(divide="ignore", invalid="ignore"):
        res = np.where(denom == 0, np.nan, num / denom)
    return res


def calc_iron_oxide(bands: Dict[BandRole, np.ndarray], **_) -> np.ndarray:
    return _safe_ratio(bands[BandRole.RED], bands[BandRole.BLUE])


def calc_ferric_iron(bands: Dict[BandRole, np.ndarray], **_) -> np.ndarray:
    return _safe_ratio(bands[BandRole.RED], bands[BandRole.GREEN])


def calc_ferrous_iron(bands: Dict[BandRole, np.ndarray], **_) -> np.ndarray:
    return _safe_ratio(bands[BandRole.SWIR_1], bands[BandRole.NIR])


def calc_clay_alteration(bands: Dict[BandRole, np.ndarray], **_) -> np.ndarray:
    return _safe_ratio(bands[BandRole.SWIR_1], bands[BandRole.SWIR_2])


def calc_gossan(bands: Dict[BandRole, np.ndarray], **_) -> np.ndarray:
    return _safe_ratio(bands[BandRole.SWIR_1], bands[BandRole.RED])


def calc_aster_qi(bands: Dict[BandRole, np.ndarray], **_) -> np.ndarray:
    b10 = bands[BandRole.THERMAL_1]
    b12 = bands[BandRole.THERMAL_2]
    # Synthetic thermal band approximation
    denom = b10 * b12
    return _safe_ratio(b12 * b12, denom)


def calc_aster_ci(bands: Dict[BandRole, np.ndarray], **_) -> np.ndarray:
    return _safe_ratio(bands[BandRole.THERMAL_1], bands[BandRole.THERMAL_2])


def calc_aster_mi(bands: Dict[BandRole, np.ndarray], **_) -> np.ndarray:
    return _safe_ratio(bands[BandRole.THERMAL_2], bands[BandRole.THERMAL_1])


def calc_feai(bands: Dict[BandRole, np.ndarray], **_) -> np.ndarray:
    return _safe_ratio(bands[BandRole.SWIR_2], bands[BandRole.NIR]) + _safe_ratio(bands[BandRole.GREEN], bands[BandRole.RED])


def calc_fei(bands: Dict[BandRole, np.ndarray], **_) -> np.ndarray:
    return _safe_ratio(bands[BandRole.SWIR_2] + bands[BandRole.NIR], bands[BandRole.GREEN] + bands[BandRole.RED])


def calc_fesi(bands: Dict[BandRole, np.ndarray], **_) -> np.ndarray:
    return _safe_ratio(bands[BandRole.SWIR_2], bands[BandRole.SWIR_1])


def calc_lati(bands: Dict[BandRole, np.ndarray], **_) -> np.ndarray:
    return _safe_ratio(bands[BandRole.SWIR_1], bands[BandRole.GREEN])


GEOLOGICAL_CATALOG: Dict[str, GeologicalIndexDefinition] = {
    "IRON_OXIDE": GeologicalIndexDefinition(
        id="IRON_OXIDE",
        acronym="Iron_Oxide",
        name_en="Iron Oxide Ratio (Hematite / Goethite / Limonite)",
        name_ar="نسبة أكاسيد الحديد (الهيماتيت / الجيوثايت)",
        target_mineral="Iron Oxides",
        required_roles=[BandRole.RED, BandRole.BLUE],
        compute_fn=calc_iron_oxide,
        formula_text="Red / Blue",
        citation="Sabins (1999), Remote sensing for mineral exploration",
    ),
    "FERRIC_IRON": GeologicalIndexDefinition(
        id="FERRIC_IRON",
        acronym="Ferric_Iron",
        name_en="Ferric Iron Ratio (Fe3+)",
        name_ar="نسبة الحديد ثلاثي التكافؤ (Ferric Iron)",
        target_mineral="Ferric Minerals",
        required_roles=[BandRole.RED, BandRole.GREEN],
        compute_fn=calc_ferric_iron,
        formula_text="Red / Green",
        citation="Hunt (1977), Spectral signatures of particulate minerals",
    ),
    "FERROUS_IRON": GeologicalIndexDefinition(
        id="FERROUS_IRON",
        acronym="Ferrous_Iron",
        name_en="Ferrous Iron Ratio (Fe2+)",
        name_ar="نسبة الحديد ثنائي التكافؤ (Ferrous Iron)",
        target_mineral="Ferrous Minerals",
        required_roles=[BandRole.SWIR_1, BandRole.NIR],
        compute_fn=calc_ferrous_iron,
        formula_text="SWIR1 / NIR",
        requires_swir=True,
        citation="Rowan et al. (1977), Discrimination of hydrothermally altered and unaltered rocks in Nevada",
    ),
    "CLAY_ALTERATION": GeologicalIndexDefinition(
        id="CLAY_ALTERATION",
        acronym="Clay_Alteration",
        name_en="Clay / Hydroxyl / Al-OH Alteration Ratio",
        name_ar="نسبة تحورات الطين والهيدروكسيل (Clay / Hydroxyl)",
        target_mineral="Al-OH Clays / Kaolinite / Alunite",
        required_roles=[BandRole.SWIR_1, BandRole.SWIR_2],
        compute_fn=calc_clay_alteration,
        formula_text="SWIR1 / SWIR2",
        requires_swir=True,
        citation="Drury (1993), Image Interpretation in Geology",
    ),
    "GOSSAN": GeologicalIndexDefinition(
        id="GOSSAN",
        acronym="Gossan",
        name_en="Gossan / Laterite Index",
        name_ar="مؤشر الجوسان ورواسب اللاتريت",
        target_mineral="Gossan / Iron capping",
        required_roles=[BandRole.SWIR_1, BandRole.RED],
        compute_fn=calc_gossan,
        formula_text="SWIR1 / Red",
        requires_swir=True,
        citation="Sabins (1999), Remote sensing for mineral exploration",
    ),
    "ASTER_QUARTZ": GeologicalIndexDefinition(
        id="ASTER_QUARTZ",
        acronym="ASTER_QI",
        name_en="ASTER Thermal Quartz Index (QI)",
        name_ar="مؤشر الكوارتز الحراري (أستير)",
        target_mineral="Quartz / Silica",
        required_roles=[BandRole.THERMAL_1, BandRole.THERMAL_2],
        compute_fn=calc_aster_qi,
        formula_text="(B11 * B11) / (B10 * B12)",
        requires_thermal=True,
        citation="Ninomiya et al. (2005), Mineral mapping with ASTER thermal infrared multispectral data",
    ),
    "ASTER_CARBONATE": GeologicalIndexDefinition(
        id="ASTER_CARBONATE",
        acronym="ASTER_CI",
        name_en="ASTER Thermal Carbonate Index (CI)",
        name_ar="مؤشر صخور الكربونات الحراري (أستير)",
        target_mineral="Carbonates / Calcite / Dolomite",
        required_roles=[BandRole.THERMAL_1, BandRole.THERMAL_2],
        compute_fn=calc_aster_ci,
        formula_text="B13 / B14",
        requires_thermal=True,
        citation="Ninomiya et al. (2005), Mineral mapping with ASTER thermal infrared multispectral data",
    ),
    "ASTER_MAFIC": GeologicalIndexDefinition(
        id="ASTER_MAFIC",
        acronym="ASTER_MI",
        name_en="ASTER Thermal Mafic / Silicate Index (MI)",
        name_ar="مؤشر الصخور المافية والقاعدية الحراري (أستير)",
        target_mineral="Mafic minerals / Pyroxene / Olivine",
        required_roles=[BandRole.THERMAL_1, BandRole.THERMAL_2],
        compute_fn=calc_aster_mi,
        formula_text="B12 / B13",
        requires_thermal=True,
        citation="Ninomiya et al. (2005), Mineral mapping with ASTER thermal infrared multispectral data",
    ),
    "FEAI": GeologicalIndexDefinition(
        id="FEAI",
        acronym="FEAI",
        name_en="Ferric Iron Alteration Index (FEAI)",
        name_ar="مؤشر تحورات الحديد ثلاثي التكافؤ",
        target_mineral="Ferric Iron Alteration",
        required_roles=[BandRole.SWIR_2, BandRole.NIR, BandRole.GREEN, BandRole.RED],
        compute_fn=calc_feai,
        formula_text="(SWIR2 / NIR) + (Green / Red)",
        requires_swir=True,
        citation="NV5 ENVI Spectral Indices / Crowley et al. (1989)",
    ),
    "FEI": GeologicalIndexDefinition(
        id="FEI",
        acronym="FEI",
        name_en="Ferrous Iron Index (FEI)",
        name_ar="مؤشر الحديد ثنائي التكافؤ",
        target_mineral="Ferrous Iron Minerals",
        required_roles=[BandRole.SWIR_2, BandRole.NIR, BandRole.GREEN, BandRole.RED],
        compute_fn=calc_fei,
        formula_text="(SWIR2 + NIR) / (Green + Red)",
        requires_swir=True,
        citation="NV5 ENVI Spectral Indices / Segal (1983)",
    ),
    "FESI": GeologicalIndexDefinition(
        id="FESI",
        acronym="FESI",
        name_en="Ferrous Silicates Index (FESI)",
        name_ar="مؤشر سيليكات الحديد",
        target_mineral="Ferrous Silicates",
        required_roles=[BandRole.SWIR_2, BandRole.SWIR_1],
        compute_fn=calc_fesi,
        formula_text="SWIR2 / SWIR1",
        requires_swir=True,
        citation="NV5 ENVI Spectral Indices / Rowan et al. (1986)",
    ),
    "LATI": GeologicalIndexDefinition(
        id="LATI",
        acronym="LATI",
        name_en="Laterite Index (LATI)",
        name_ar="مؤشر صخور اللاتريت",
        target_mineral="Laterite / Iron-rich soil",
        required_roles=[BandRole.SWIR_1, BandRole.GREEN],
        compute_fn=calc_lati,
        formula_text="SWIR1 / Green",
        requires_swir=True,
        citation="NV5 ENVI Spectral Indices / Boettinger et al. (2008)",
    ),
}

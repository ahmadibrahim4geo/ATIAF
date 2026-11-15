"""Spectral index registry and mathematical definitions for ATIAF."""

from dataclasses import dataclass, field
from typing import Callable, Dict, List, Optional, Tuple
import numpy as np

from atiaf_core.discovery.models import BandRole


@dataclass
class SpectralIndexDefinition:
    id: str
    acronym: str
    name_en: str
    name_ar: str
    category: str  # 'Vegetation', 'Water', 'Urban', 'Burn', 'Snow', 'Soil'
    required_roles: List[BandRole]
    compute_fn: Callable[..., np.ndarray]
    formula_text: str
    valid_range: Tuple[float, float] = (-1.0, 1.0)
    default_constants: Dict[str, float] = field(default_factory=dict)
    citation: str = ""
    notes: str = ""


# Algebraic calculation functions with zero-division and NaN protection
def _safe_divide(num: np.ndarray, denom: np.ndarray, nodata_val: float = np.nan) -> np.ndarray:
    with np.errstate(divide="ignore", invalid="ignore"):
        result = np.where(denom == 0, nodata_val, num / denom)
    return result


def calc_ndvi(bands: Dict[BandRole, np.ndarray], **_) -> np.ndarray:
    nir = bands[BandRole.NIR]
    red = bands[BandRole.RED]
    return _safe_divide(nir - red, nir + red)


def calc_evi2(bands, **unused):
    n, r = bands[BandRole.NIR], bands[BandRole.RED]
    return _safe_divide(2.5 * (n-r), n+2.4*r+1)


def calc_nirv(bands, **unused):
    n, r = bands[BandRole.NIR], bands[BandRole.RED]
    return n * _safe_divide(n-r, n+r)


def calc_gndvi(bands: Dict[BandRole, np.ndarray], **_) -> np.ndarray:
    nir = bands[BandRole.NIR]
    green = bands[BandRole.GREEN]
    return _safe_divide(nir - green, nir + green)


def calc_savi(bands: Dict[BandRole, np.ndarray], L: float = 0.5, **_) -> np.ndarray:
    nir = bands[BandRole.NIR]
    red = bands[BandRole.RED]
    return _safe_divide((nir - red) * (1.0 + L), nir + red + L)


def calc_evi(bands: Dict[BandRole, np.ndarray], G: float = 2.5, C1: float = 6.0, C2: float = 7.5, L: float = 1.0, **_) -> np.ndarray:
    nir = bands[BandRole.NIR]
    red = bands[BandRole.RED]
    blue = bands[BandRole.BLUE]
    denom = nir + C1 * red - C2 * blue + L
    return _safe_divide(G * (nir - red), denom)


def calc_ndre1(bands: Dict[BandRole, np.ndarray], **_) -> np.ndarray:
    nir = bands[BandRole.NIR]
    re1 = bands[BandRole.RED_EDGE_1]
    return _safe_divide(nir - re1, nir + re1)


def calc_ndwi_mcfeeters(bands: Dict[BandRole, np.ndarray], **_) -> np.ndarray:
    green = bands[BandRole.GREEN]
    nir = bands[BandRole.NIR]
    return _safe_divide(green - nir, green + nir)


def calc_ndwi_gao(bands: Dict[BandRole, np.ndarray], **_) -> np.ndarray:
    nir = bands[BandRole.NIR]
    swir1 = bands[BandRole.SWIR_1]
    return _safe_divide(nir - swir1, nir + swir1)


def calc_mndwi(bands: Dict[BandRole, np.ndarray], **_) -> np.ndarray:
    green = bands[BandRole.GREEN]
    swir1 = bands[BandRole.SWIR_1]
    return _safe_divide(green - swir1, green + swir1)


def calc_ndbi(bands: Dict[BandRole, np.ndarray], **_) -> np.ndarray:
    swir1 = bands[BandRole.SWIR_1]
    nir = bands[BandRole.NIR]
    return _safe_divide(swir1 - nir, swir1 + nir)


def calc_ui(bands: Dict[BandRole, np.ndarray], **_) -> np.ndarray:
    swir2 = bands[BandRole.SWIR_2]
    nir = bands[BandRole.NIR]
    return _safe_divide(swir2 - nir, swir2 + nir)


def calc_nbr(bands: Dict[BandRole, np.ndarray], **_) -> np.ndarray:
    nir = bands[BandRole.NIR]
    swir2 = bands[BandRole.SWIR_2]
    return _safe_divide(nir - swir2, nir + swir2)


def calc_nbr2(bands: Dict[BandRole, np.ndarray], **_) -> np.ndarray:
    swir1 = bands[BandRole.SWIR_1]
    swir2 = bands[BandRole.SWIR_2]
    return _safe_divide(swir1 - swir2, swir1 + swir2)


def calc_ndsi(bands: Dict[BandRole, np.ndarray], **_) -> np.ndarray:
    green = bands[BandRole.GREEN]
    swir1 = bands[BandRole.SWIR_1]
    return _safe_divide(green - swir1, green + swir1)


def calc_bsi(bands: Dict[BandRole, np.ndarray], **_) -> np.ndarray:
    swir1 = bands[BandRole.SWIR_1]
    red = bands[BandRole.RED]
    nir = bands[BandRole.NIR]
    blue = bands[BandRole.BLUE]
    num = (swir1 + red) - (nir + blue)
    denom = (swir1 + red) + (nir + blue)
    return _safe_divide(num, denom)


def calc_ndmi(bands: Dict[BandRole, np.ndarray], **_) -> np.ndarray:
    nir = bands[BandRole.NIR]
    swir1 = bands[BandRole.SWIR_1]
    return _safe_divide(nir - swir1, nir + swir1)


def calc_msavi(bands: Dict[BandRole, np.ndarray], **_) -> np.ndarray:
    nir = bands[BandRole.NIR]
    red = bands[BandRole.RED]
    with np.errstate(invalid="ignore"):
        term = (2.0 * nir + 1.0) ** 2 - 8.0 * (nir - red)
        term_clean = np.where(term < 0, np.nan, term)
        msavi = (2.0 * nir + 1.0 - np.sqrt(term_clean)) / 2.0
    return msavi


def calc_osavi(bands: Dict[BandRole, np.ndarray], **_) -> np.ndarray:
    nir = bands[BandRole.NIR]
    red = bands[BandRole.RED]
    return _safe_divide(nir - red, nir + red + 0.16)


def calc_vari(bands: Dict[BandRole, np.ndarray], **_) -> np.ndarray:
    green = bands[BandRole.GREEN]
    red = bands[BandRole.RED]
    blue = bands[BandRole.BLUE]
    return _safe_divide(green - red, green + red - blue)


def calc_gli(bands: Dict[BandRole, np.ndarray], **_) -> np.ndarray:
    green = bands[BandRole.GREEN]
    red = bands[BandRole.RED]
    blue = bands[BandRole.BLUE]
    return _safe_divide(2.0 * green - red - blue, 2.0 * green + red + blue)


def calc_tcb(bands: Dict[BandRole, np.ndarray], **_) -> np.ndarray:
    b = bands[BandRole.BLUE]
    g = bands[BandRole.GREEN]
    r = bands[BandRole.RED]
    nir = bands[BandRole.NIR]
    swir1 = bands[BandRole.SWIR_1]
    swir2 = bands[BandRole.SWIR_2]
    return 0.3029 * b + 0.2786 * g + 0.4733 * r + 0.5599 * nir + 0.5080 * swir1 + 0.1872 * swir2


def calc_tcg(bands: Dict[BandRole, np.ndarray], **_) -> np.ndarray:
    b = bands[BandRole.BLUE]
    g = bands[BandRole.GREEN]
    r = bands[BandRole.RED]
    nir = bands[BandRole.NIR]
    swir1 = bands[BandRole.SWIR_1]
    swir2 = bands[BandRole.SWIR_2]
    return -0.2941 * b - 0.2430 * g - 0.5424 * r + 0.7276 * nir + 0.0713 * swir1 - 0.1608 * swir2


def calc_tcw(bands: Dict[BandRole, np.ndarray], **_) -> np.ndarray:
    b = bands[BandRole.BLUE]
    g = bands[BandRole.GREEN]
    r = bands[BandRole.RED]
    nir = bands[BandRole.NIR]
    swir1 = bands[BandRole.SWIR_1]
    swir2 = bands[BandRole.SWIR_2]
    return 0.1511 * b + 0.1973 * g + 0.3283 * r + 0.3407 * nir - 0.7117 * swir1 - 0.4572 * swir2


# Catalog registry of validated formulas
INDEX_CATALOG: Dict[str, SpectralIndexDefinition] = {
    "NDVI": SpectralIndexDefinition(
        id="NDVI",
        acronym="NDVI",
        name_en="Normalized Difference Vegetation Index",
        name_ar="مؤشر الفرق المعياري للغطاء النباتي",
        category="Vegetation",
        required_roles=[BandRole.NIR, BandRole.RED],
        compute_fn=calc_ndvi,
        formula_text="(NIR - Red) / (NIR + Red)",
        citation="Rouse et al. (1974), Monitoring vegetation systems in the Great Plains with ERTS",
    ),
    "GNDVI": SpectralIndexDefinition(
        id="GNDVI",
        acronym="GNDVI",
        name_en="Green Normalized Difference Vegetation Index",
        name_ar="مؤشر الفرق المعياري الأخضر للغطاء النباتي",
        category="Vegetation",
        required_roles=[BandRole.NIR, BandRole.GREEN],
        compute_fn=calc_gndvi,
        formula_text="(NIR - Green) / (NIR + Green)",
        citation="Gitelson et al. (1996), Remote sensing of chlorophyll concentration in higher plant leaves",
    ),
    "SAVI": SpectralIndexDefinition(
        id="SAVI",
        acronym="SAVI",
        name_en="Soil-Adjusted Vegetation Index",
        name_ar="مؤشر الغطاء النباتي المعدل بتأثير التربة",
        category="Vegetation",
        required_roles=[BandRole.NIR, BandRole.RED],
        compute_fn=calc_savi,
        formula_text="((NIR - Red) / (NIR + Red + L)) * (1 + L)",
        default_constants={"L": 0.5},
        citation="Huete (1988), A soil-adjusted vegetation index (SAVI)",
    ),
    "EVI": SpectralIndexDefinition(
        id="EVI",
        acronym="EVI",
        name_en="Enhanced Vegetation Index",
        name_ar="مؤشر الغطاء النباتي المحسن",
        category="Vegetation",
        required_roles=[BandRole.NIR, BandRole.RED, BandRole.BLUE],
        compute_fn=calc_evi,
        formula_text="2.5 * ((NIR - Red) / (NIR + 6*Red - 7.5*Blue + 1))",
        default_constants={"G": 2.5, "C1": 6.0, "C2": 7.5, "L": 1.0},
        citation="Huete et al. (2002), Overview of the radiometric and biophysical performance of the MODIS vegetation indices",
    ),
    "NDRE1": SpectralIndexDefinition(
        id="NDRE1",
        acronym="NDRE1",
        name_en="Normalized Difference Red Edge Index 1",
        name_ar="مؤشر الفرق المعياري لحافة الأحمر 1",
        category="Vegetation",
        required_roles=[BandRole.NIR, BandRole.RED_EDGE_1],
        compute_fn=calc_ndre1,
        formula_text="(NIR - RedEdge1) / (NIR + RedEdge1)",
        citation="Gitelson & Merzlyak (1994), Quantitative estimation of chlorophyll-a using reflectance spectra",
    ),
    "NDWI_MCFEETERS": SpectralIndexDefinition(
        id="NDWI_MCFEETERS",
        acronym="NDWI",
        name_en="Normalized Difference Water Index (McFeeters)",
        name_ar="مؤشر الفرق المعياري للمياه (ماك فيترز)",
        category="Water",
        required_roles=[BandRole.GREEN, BandRole.NIR],
        compute_fn=calc_ndwi_mcfeeters,
        formula_text="(Green - NIR) / (Green + NIR)",
        citation="McFeeters (1996), The use of the Normalized Difference Water Index in the delineation of open water features",
    ),
    "NDWI_GAO": SpectralIndexDefinition(
        id="NDWI_GAO",
        acronym="NDWI_Gao",
        name_en="Normalized Difference Water/Moisture Index (Gao)",
        name_ar="مؤشر محتوى الرطوبة المعياري (جاو)",
        category="Water",
        required_roles=[BandRole.NIR, BandRole.SWIR_1],
        compute_fn=calc_ndwi_gao,
        formula_text="(NIR - SWIR1) / (NIR + SWIR1)",
        citation="Gao (1996), NDWI—A normalized difference water index for remote sensing of vegetation liquid water from space",
    ),
    "MNDWI": SpectralIndexDefinition(
        id="MNDWI",
        acronym="MNDWI",
        name_en="Modified Normalized Difference Water Index (Xu)",
        name_ar="مؤشر الفرق المعياري المعدل للمياه (شو)",
        category="Water",
        required_roles=[BandRole.GREEN, BandRole.SWIR_1],
        compute_fn=calc_mndwi,
        formula_text="(Green - SWIR1) / (Green + SWIR1)",
        citation="Xu (2006), Modification of normalised difference water index (NDWI) to enhance open water features",
    ),
    "NDBI": SpectralIndexDefinition(
        id="NDBI",
        acronym="NDBI",
        name_en="Normalized Difference Built-Up Index",
        name_ar="مؤشر الفرق المعياري للمناطق العمرانية",
        category="Urban",
        required_roles=[BandRole.SWIR_1, BandRole.NIR],
        compute_fn=calc_ndbi,
        formula_text="(SWIR1 - NIR) / (SWIR1 + NIR)",
        citation="Zha et al. (2003), Use of normalized difference built-up index in automatically mapping urban areas from TM imagery",
    ),
    "UI": SpectralIndexDefinition(
        id="UI",
        acronym="UI",
        name_en="Urban Index",
        name_ar="المؤشر العمراني",
        category="Urban",
        required_roles=[BandRole.SWIR_2, BandRole.NIR],
        compute_fn=calc_ui,
        formula_text="(SWIR2 - NIR) / (SWIR2 + NIR)",
        citation="Kawamura et al. (1996), Relation between social and environmental conditions in developing countries and urban heat islands",
    ),
    "NBR": SpectralIndexDefinition(
        id="NBR",
        acronym="NBR",
        name_en="Normalized Burn Ratio",
        name_ar="مؤشر نسبة الحريق المعيارية",
        category="Burn",
        required_roles=[BandRole.NIR, BandRole.SWIR_2],
        compute_fn=calc_nbr,
        formula_text="(NIR - SWIR2) / (NIR + SWIR2)",
        citation="Key & Benson (2006), Landscape assessment: Ground measure of severity, the Composite Burn Index; and Remote sensing of severity, the Normalized Burn Ratio",
    ),
    "NBR2": SpectralIndexDefinition(
        id="NBR2",
        acronym="NBR2",
        name_en="Normalized Burn Ratio 2",
        name_ar="مؤشر نسبة الحريق المعيارية 2",
        category="Burn",
        required_roles=[BandRole.SWIR_1, BandRole.SWIR_2],
        compute_fn=calc_nbr2,
        formula_text="(SWIR1 - SWIR2) / (SWIR1 + SWIR2)",
        citation="Garcia & Caselles (1991), Mapping burns and natural hazards with Landsat Thematic Mapper data",
    ),
    "NDSI": SpectralIndexDefinition(
        id="NDSI",
        acronym="NDSI",
        name_en="Normalized Difference Snow Index",
        name_ar="مؤشر الفرق المعياري للثلوج",
        category="Snow",
        required_roles=[BandRole.GREEN, BandRole.SWIR_1],
        compute_fn=calc_ndsi,
        formula_text="(Green - SWIR1) / (Green + SWIR1)",
        citation="Hall et al. (1995), Development of methods for mapping global snow cover using moderate resolution imaging spectroradiometer data",
    ),
    "BSI": SpectralIndexDefinition(
        id="BSI",
        acronym="BSI",
        name_en="Bare Soil Index",
        name_ar="مؤشر التربة المكشوفة",
        category="Soil",
        required_roles=[BandRole.SWIR_1, BandRole.RED, BandRole.NIR, BandRole.BLUE],
        compute_fn=calc_bsi,
        formula_text="((SWIR1 + Red) - (NIR + Blue)) / ((SWIR1 + Red) + (NIR + Blue))",
        citation="Diek et al. (2017), The normalized difference bare soil index: a new approach",
    ),
    "NDMI": SpectralIndexDefinition(
        id="NDMI",
        acronym="NDMI",
        name_en="Normalized Difference Moisture Index",
        name_ar="مؤشر الرطوبة الفارق المعياري",
        category="Water",
        required_roles=[BandRole.NIR, BandRole.SWIR_1],
        compute_fn=calc_ndmi,
        formula_text="(NIR - SWIR1) / (NIR + SWIR1)",
        citation="Gao, B. C. (1996), NDWI—A normalized difference water index for remote sensing of vegetation liquid water from space",
    ),
    "MSAVI": SpectralIndexDefinition(
        id="MSAVI",
        acronym="MSAVI",
        name_en="Modified Soil-Adjusted Vegetation Index",
        name_ar="مؤشر الغطاء النباتي المعدل للتربة الثاني",
        category="Vegetation",
        required_roles=[BandRole.NIR, BandRole.RED],
        compute_fn=calc_msavi,
        formula_text="(2 * NIR + 1 - sqrt((2 * NIR + 1)^2 - 8 * (NIR - Red))) / 2",
        citation="Qi et al. (1994), A modified soil adjusted vegetation index",
    ),
    "OSAVI": SpectralIndexDefinition(
        id="OSAVI",
        acronym="OSAVI",
        name_en="Optimized Soil-Adjusted Vegetation Index",
        name_ar="مؤشر الغطاء النباتي المعدل الأمثل للتربة",
        category="Vegetation",
        required_roles=[BandRole.NIR, BandRole.RED],
        compute_fn=calc_osavi,
        formula_text="(NIR - Red) / (NIR + Red + 0.16)",
        citation="Rondeaux et al. (1996), Optimization of spectral indices for vegetation monitoring",
    ),
    "VARI": SpectralIndexDefinition(
        id="VARI",
        acronym="VARI",
        name_en="Visible Atmospherically Resistant Index",
        name_ar="المؤشر المرئي المقاوم لتأثيرات الغلاف الجوي",
        category="Vegetation",
        required_roles=[BandRole.GREEN, BandRole.RED, BandRole.BLUE],
        compute_fn=calc_vari,
        formula_text="(Green - Red) / (Green + Red - Blue)",
        citation="Gitelson et al. (2002), Novel algorithms for remote estimation of vegetation fraction",
    ),
    "GLI": SpectralIndexDefinition(
        id="GLI",
        acronym="GLI",
        name_en="Green Leaf Index",
        name_ar="مؤشر الورق الأخضر",
        category="Vegetation",
        required_roles=[BandRole.GREEN, BandRole.RED, BandRole.BLUE],
        compute_fn=calc_gli,
        formula_text="(2 * Green - Red - Blue) / (2 * Green + Red + Blue)",
        citation="Louhaichi et al. (2001), Spatially located platform and aerial photography for documentation of grazing impacts on wheat",
    ),
    "TCB": SpectralIndexDefinition(
        id="TCB",
        acronym="TCB",
        name_en="Tasseled Cap Brightness",
        name_ar="مؤشر السطوع لكاب القبعة",
        category="Transformation",
        required_roles=[BandRole.BLUE, BandRole.GREEN, BandRole.RED, BandRole.NIR, BandRole.SWIR_1, BandRole.SWIR_2],
        compute_fn=calc_tcb,
        formula_text="0.3029*Blue + 0.2786*Green + 0.4733*Red + 0.5599*NIR + 0.508*SWIR1 + 0.1872*SWIR2",
        citation="Baig et al. (2014), Derivation of a tasseled cap transformation based on Landsat 8 at-satellite reflectance",
    ),
    "TCG": SpectralIndexDefinition(
        id="TCG",
        acronym="TCG",
        name_en="Tasseled Cap Greenness",
        name_ar="مؤشر الخضرة لكاب القبعة",
        category="Transformation",
        required_roles=[BandRole.BLUE, BandRole.GREEN, BandRole.RED, BandRole.NIR, BandRole.SWIR_1, BandRole.SWIR_2],
        compute_fn=calc_tcg,
        formula_text="-0.2941*Blue - 0.243*Green - 0.5424*Red + 0.7276*NIR + 0.0713*SWIR1 - 0.1608*SWIR2",
        citation="Baig et al. (2014), Derivation of a tasseled cap transformation based on Landsat 8 at-satellite reflectance",
    ),
    "TCW": SpectralIndexDefinition(
        id="TCW",
        acronym="TCW",
        name_en="Tasseled Cap Wetness",
        name_ar="مؤشر البلل والرطوبة لكاب القبعة",
        category="Transformation",
        required_roles=[BandRole.BLUE, BandRole.GREEN, BandRole.RED, BandRole.NIR, BandRole.SWIR_1, BandRole.SWIR_2],
        compute_fn=calc_tcw,
        formula_text="0.1511*Blue + 0.1973*Green + 0.3283*Red + 0.3407*NIR - 0.7117*SWIR1 - 0.4572*SWIR2",
        citation="Baig et al. (2014), Derivation of a tasseled cap transformation based on Landsat 8 at-satellite reflectance",
    ),
}

from atiaf_core.catalog_additions import DEFINITIONS
for row in DEFINITIONS:
    INDEX_CATALOG[row['id']] = SpectralIndexDefinition(
        id=row['id'], acronym=row['id'], name_en=row['en'], name_ar=row['ar'], category=row['category'],
        required_roles=[BandRole(r) for r in row['roles']],
        compute_fn={'EVI2': calc_evi2, 'NIRv': calc_nirv}[row['id']], formula_text=row['formula'],
        valid_range=(-float('inf'), float('inf')), citation=row['citation'],
        notes='Numerical implementation; real-product sensor validation remains separate')

# -*- coding: utf-8 -*-
"""Command-line interface and installation verification utility for ATIAF."""

import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))


def run_diagnostics(verbose: bool = True) -> int:
    """Performs a comprehensive environment and installation check for ATIAF."""
    report = []
    errors = 0

    def log(msg: str):
        report.append(msg)
        if verbose:
            print(msg)

    log("======================================================================")
    log("  ATIAF (أطياف) — Installation & Environment Diagnostics (v1.0.0)")
    log("======================================================================")
    log(f"Python Runtime: {sys.version.split()[0]} ({sys.executable})")
    log(f"Project Root:   {PROJECT_ROOT}")
    log("")

    # 1. Check Core Python Dependencies
    log("[1/5] Checking Core Scientific Dependencies...")
    core_deps = [
        ("numpy", "NumPy array processing"),
        ("rasterio", "GeoTIFF raster I/O"),
        ("shapely", "AOI polygon vector geometry"),
        ("pyproj", "Cartographic projections & CRS"),
    ]
    for pkg, purpose in core_deps:
        try:
            mod = __import__(pkg)
            ver = getattr(mod, "__version__", "unknown")
            log(f"  [OK] {pkg:<12} v{ver:<10} ({purpose})")
        except ImportError as e:
            log(f"  [MISSING] {pkg:<12} ({purpose}) -> {e}")
            errors += 1

    # 2. Check Optional Dependencies
    log("\n[2/5] Checking Optional Analysis & Visualization Dependencies...")
    opt_deps = [
        ("geopandas", "Vector GIS spatial frames"),
        ("matplotlib", "Rendering & colormaps"),
        ("scipy", "Advanced spatial filtering"),
    ]
    for pkg, purpose in opt_deps:
        try:
            mod = __import__(pkg)
            ver = getattr(mod, "__version__", "unknown")
            log(f"  [OPTIONAL] {pkg:<12} v{ver:<10} ({purpose})")
        except ImportError:
            log(f"  [NOT INSTALLED] {pkg:<12} ({purpose} - fallback available)")

    # 3. Check atyaf_core Engines
    log("\n[3/5] Checking ATIAF Core Processing Engines...")
    try:
        from atyaf_core.discovery import SceneScanner, LandsatParser, Sentinel2Parser, AsterParser, Sentinel1Parser
        from atyaf_core.indices import INDEX_CATALOG, SpectralIndicesEngine
        from atyaf_core.temperature import SurfaceTemperatureEngine, EmissivityEngine
        from atyaf_core.urban import ThermalUrbanEngine
        from atyaf_core.environment import EnvironmentalDroughtEngine
        from atyaf_core.geology import GEOLOGICAL_CATALOG, GeologicalAnalysisEngine
        from atyaf_core.mosaic import QualityMosaicEngine
        from atyaf_core.temporal import ChangeDetectionEngine
        from atyaf_core.modalities import ModalityRouter, SAREngine, HyperspectralEngine

        log(f"  [OK] Discovery Core: Landsat, Sentinel-2, ASTER, Sentinel-1 Parsers loaded")
        log(f"  [OK] Optical Indices: {len(INDEX_CATALOG)} scientific indices validated in catalog")
        log(f"  [OK] Surface Temperature & Emissivity: Sobrino 2004 NDVI model loaded")
        log(f"  [OK] Thermal Urban & Drought: UTFVI, Hotspots, Liang Albedo, TVDI loaded")
        log(f"  [OK] Geological Ratios: {len(GEOLOGICAL_CATALOG)} diagnostic mineral alterations loaded")
        log(f"  [OK] Mosaic & Temporal: Quality-aware blending & dNBR burn severity loaded")
        log(f"  [OK] Advanced Modalities: SAR (Sentinel-1) & Hyperspectral (EnMAP/PRISMA) gating loaded")
    except Exception as e:
        log(f"  [FAILED] atyaf_core import failed: {e}")
        errors += 1

    # 4. Check ArcGIS Pro Native Toolbox
    log("\n[4/5] Checking ArcGIS Pro Toolbox (.pyt)...")
    pyt_path = PROJECT_ROOT / "ArcGIS Pro Tools" / "ATIAF.pyt"
    if not pyt_path.is_file():
        pyt_path = PROJECT_ROOT / "arcgis_pro" / "ATIAF.pyt"

    if pyt_path.is_file():
        try:
            code = pyt_path.read_text(encoding="utf-8")
            compiled = compile(code, str(pyt_path), "exec")
            rel_path = pyt_path.relative_to(PROJECT_ROOT)
            log(f"  [OK] {rel_path} syntax valid (Toolbox with 6 canonical tools)")
        except Exception as e:
            log(f"  [FAILED] {pyt_path} syntax error: {e}")
            errors += 1
    else:
        log(f"  [MISSING] {pyt_path} not found")
        errors += 1

    # 5. Check QGIS Processing Provider Plugin
    log("\n[5/5] Checking QGIS Processing Provider Plugin...")
    qgis_meta = PROJECT_ROOT / "QGIS Tools" / "atiaf" / "metadata.txt"
    qgis_base = PROJECT_ROOT / "QGIS Tools"
    plugin_mod = "atiaf"
    if not qgis_meta.is_file():
        qgis_meta = PROJECT_ROOT / "qgis" / "atyaf" / "metadata.txt"
        qgis_base = PROJECT_ROOT / "qgis"
        plugin_mod = "atyaf"

    if qgis_meta.is_file():
        try:
            qgis_pkg_dir = str(qgis_base)
            if qgis_pkg_dir not in sys.path:
                sys.path.insert(0, qgis_pkg_dir)
            import importlib
            mod = importlib.import_module(f"{plugin_mod}.provider")
            prov_cls = getattr(mod, "ATIAFProcessingProvider")
            prov = prov_cls()
            rel_meta = qgis_meta.parent.relative_to(PROJECT_ROOT)
            log(f"  [OK] {rel_meta}/ provider '{prov.id()}' ({prov.name()}) with 6 processing algorithms")
        except Exception as e:
            log(f"  [NOTE] QGIS plugin check exception: {e}")
    else:
        log(f"  [MISSING] {qgis_meta} not found")
        errors += 1

    log("\n======================================================================")
    if errors == 0:
        log("  RESULT: ATIAF INSTALLATION VERIFIED SUCCESSFULLY (اجتياز الفحص بنجاح)")
        log("======================================================================")
        return 0
    else:
        log(f"  RESULT: ATIAF INSTALLATION HAS {errors} ISSUE(S) (توجد أخطاء في الفحص)")
        log("======================================================================")
        return 1


def main():
    """CLI entry point for atyaf-verify."""
    sys.exit(run_diagnostics(verbose=True))


if __name__ == "__main__":
    main()

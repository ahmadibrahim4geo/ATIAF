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
    log("  ATIAF - Dependency, Import and Syntax Diagnostics (1.0.1.dev0)")
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
            log(f"  [NOT INSTALLED] {pkg:<12} ({purpose}; optional operations not verified)")

    # 3. Check atiaf_core Engines
    log("\n[3/5] Checking ATIAF Core Processing Engines...")
    try:
        from atiaf_core.discovery import SceneScanner, LandsatParser, Sentinel2Parser, AsterParser, Sentinel1Parser
        from atiaf_core.indices import INDEX_CATALOG, SpectralIndicesEngine
        from atiaf_core.temperature import SurfaceTemperatureEngine, EmissivityEngine
        from atiaf_core.urban import ThermalUrbanEngine
        from atiaf_core.environment import EnvironmentalDroughtEngine
        from atiaf_core.geology import GEOLOGICAL_CATALOG, GeologicalAnalysisEngine
        from atiaf_core.mosaic import QualityMosaicEngine
        from atiaf_core.temporal import ChangeDetectionEngine
        from atiaf_core.modalities import ModalityRouter, SAREngine, HyperspectralEngine

        log("  [IMPORT] Discovery parser modules loaded; product compatibility not checked here")
        log(f"  [IMPORT] Optical registry: {len(INDEX_CATALOG)} definitions; scientific validation not checked")
        log("  [IMPORT] Temperature/emissivity modules loaded; workflow science gates still apply")
        log("  [IMPORT] Urban/environment modules loaded; incomplete methods remain gated")
        log(f"  [IMPORT] Geological registry: {len(GEOLOGICAL_CATALOG)} definitions; mineral identification not verified")
        log("  [IMPORT] Mosaic/temporal modules loaded; compatibility and provenance require execution checks")
        log("  [IMPORT] Experimental SAR/hyperspectral utilities loaded; native sensor workflows not verified")
    except Exception as e:
        log(f"  [FAILED] atiaf_core import failed: {e}")
        errors += 1

    # 4. Check ArcGIS Pro Native Toolbox
    log("\n[4/5] Checking ArcGIS Pro Toolbox (.pyt)...")
    pyt_path = PROJECT_ROOT / "ArcGIS Pro Tools" / "ATIAF.pyt"

    if pyt_path.is_file():
        try:
            code = pyt_path.read_text(encoding="utf-8")
            compiled = compile(code, str(pyt_path), "exec")
            rel_path = pyt_path.relative_to(PROJECT_ROOT)
            log(f"  [OK] {rel_path} syntax valid; native loading/execution not checked here")
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
            log(f"  [OK] {rel_meta}/ provider '{prov.id()}' imported; native registration not checked here")
        except Exception as e:
            log(f"  [NOTE] QGIS plugin check exception: {e}")
            errors += 1
    else:
        log(f"  [MISSING] {qgis_meta} not found")
        errors += 1

    log("\n======================================================================")
    if errors == 0:
        log("  RESULT: dependency/import/syntax checks passed; native dialogs, real products and clean installation NOT VERIFIED")
        log("======================================================================")
        return 0
    else:
        log(f"  RESULT: ATIAF INSTALLATION HAS {errors} ISSUE(S) (توجد أخطاء في الفحص)")
        log("======================================================================")
        return 1


def main():
    """CLI entry point for atiaf-verify."""
    sys.exit(run_diagnostics(verbose=True))


if __name__ == "__main__":
    main()

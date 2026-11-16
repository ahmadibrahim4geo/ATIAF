"""Comprehensive dual-scene validation test script for PLAN-0019 r2.
Runs all applicable tools on:
1) Modern Scene: Landsat 9 C2 L2 (LC09_L2SP_174043_20261105_20261110_02_T1)
2) Legacy Scene: Landsat 8 Pre-Collection L1T (LC81760392014234LGN00)
Saves outputs to: Testing Results/PLAN-0019_r2/
Inspects and logs detailed pixel statistics, metadata, CRS, and visual validity.
"""
import os
import sys
import json
import traceback
from pathlib import Path
import numpy as np
import rasterio

from atiaf_core.workflow import run_tool

ROOT = Path(__file__).resolve().parent.parent
MODERN_SCENE = ROOT / "Testing Data" / "LC09_L2SP_174043_20261105_20261110_02_T1"
LEGACY_SCENE = ROOT / "Testing Data" / "LC81760392014234LGN00"
OUTPUT_BASE = ROOT / "Testing Results" / "PLAN-0019_r2"
OUTPUT_BASE.mkdir(parents=True, exist_ok=True)

results_log = []

def analyze_raster(path: Path):
    if not path.is_file():
        return {"status": "FILE_NOT_FOUND", "path": str(path)}
    try:
        with rasterio.open(path) as ds:
            stats = {
                "file_name": path.name,
                "path": str(path),
                "count": ds.count,
                "width": ds.width,
                "height": ds.height,
                "crs": str(ds.crs),
                "dtypes": ds.dtypes,
                "nodata": ds.nodata,
                "bands_stats": []
            }
            for b in range(1, ds.count + 1):
                arr = ds.read(b, masked=True)
                valid = arr.compressed()
                if len(valid) == 0:
                    b_stat = {"valid_pixels": 0, "status": "ALL_NODATA"}
                else:
                    b_stat = {
                        "valid_pixels": int(len(valid)),
                        "total_pixels": int(arr.size),
                        "valid_pct": float(round(100.0 * len(valid) / arr.size, 2)),
                        "min": float(round(float(valid.min()), 4)),
                        "max": float(round(float(valid.max()), 4)),
                        "mean": float(round(float(valid.mean()), 4)),
                        "std": float(round(float(valid.std()), 4)),
                        "has_nan": bool(np.isnan(valid).any())
                    }
                stats["bands_stats"].append(b_stat)
            return stats
    except Exception as e:
        return {"status": "ERROR_READING", "error": str(e), "path": str(path)}

def run_test(name, tool, input_folder, selected, **kwargs):
    print(f"\n=======================================================")
    print(f"RUNNING TEST: {name}")
    print(f"Tool: {tool}, Selected: {selected}")
    print(f"Input: {input_folder}")
    print(f"Options: {kwargs.get('options', {})}")
    print(f"=======================================================")
    test_record = {
        "test_name": name,
        "tool": tool,
        "selected": selected,
        "input_folder": str(input_folder),
        "options": kwargs.get("options", {}),
        "success": False,
        "outputs": [],
        "raster_analysis": [],
        "error": None
    }
    try:
        res = run_tool(
            tool=tool,
            input_folder=input_folder,
            selected=selected,
            **kwargs
        )
        print("Run succeeded! Outputs:")
        outputs = res.get("OUTPUT_RASTERS", []) if isinstance(res, dict) else getattr(res, "outputs", [])
        for out in outputs:
            print(f" - {out}")
            test_record["outputs"].append(str(out))
            stats = analyze_raster(Path(out))
            test_record["raster_analysis"].append(stats)
            if "bands_stats" in stats and stats["bands_stats"]:
                b0 = stats["bands_stats"][0]
                print(f"   Shape: {stats['width']}x{stats['height']}, Bands: {stats['count']}, CRS: {stats['crs']}")
                print(f"   Valid: {b0.get('valid_pct')}% | Min: {b0.get('min')}, Max: {b0.get('max')}, Mean: {b0.get('mean')}")
        test_record["success"] = True
    except Exception as e:
        print(f"FAILED: {e}")
        traceback.print_exc()
        test_record["error"] = str(e)
    results_log.append(test_record)
    return test_record

def main():
    print("Starting PLAN-0019 r2 Dual-Scene Execution...")

    # ---------------------------------------------------------
    # TEST 1: Modern Scene (LC09 C2 L2) - Tool 01 Spectral Indices
    # ---------------------------------------------------------
    run_test(
        name="MODERN_TOOL01_SPECTRAL_INDICES",
        tool="spectral_indices",
        input_folder=MODERN_SCENE,
        selected=["NDVI", "GNDVI", "SAVI", "EVI", "NDWI_MCFEETERS", "MNDWI", "NDBI", "UI", "NBR", "BSI", "MSAVI"],
        apply_qa=True,
        output_folder=OUTPUT_BASE / "Modern_Tool01_Indices",
        options={"study_area_name": "ModernNile"}
    )

    # ---------------------------------------------------------
    # TEST 2: Modern Scene (LC09 C2 L2) - Tool 02 Surface Temperature
    # ---------------------------------------------------------
    run_test(
        name="MODERN_TOOL02_SURFACE_TEMPERATURE",
        tool="surface_temperature",
        input_folder=MODERN_SCENE,
        selected=["LST_CELSIUS"],
        apply_qa=True,
        output_folder=OUTPUT_BASE / "Modern_Tool02_Temperature",
        options={"study_area_name": "ModernNile"}
    )

    # ---------------------------------------------------------
    # TEST 3: Modern Scene (LC09 C2 L2) - Tool 03 Thermal Urban
    # ---------------------------------------------------------
    run_test(
        name="MODERN_TOOL03_THERMAL_URBAN",
        tool="thermal_urban",
        input_folder=MODERN_SCENE,
        selected=["UTFVI", "HOTSPOTS"],
        apply_qa=True,
        output_folder=OUTPUT_BASE / "Modern_Tool03_Urban",
        options={"study_area_name": "ModernNile", "allow_large_scene": True}
    )

    # ---------------------------------------------------------
    # TEST 4: Modern Scene (LC09 C2 L2) - Tool 05 Geological Analysis
    # Including traditional ratios + NEW ENVI Mineral Indices (FEAI, FEI, FESI, LATI)
    # ---------------------------------------------------------
    run_test(
        name="MODERN_TOOL05_GEOLOGY_AND_ENVI",
        tool="geological_analysis",
        input_folder=MODERN_SCENE,
        selected=[
            "IRON_OXIDE", "FERRIC_IRON", "FERROUS_IRON", "CLAY_ALTERATION", "GOSSAN",
            "FEAI", "FEI", "FESI", "LATI"
        ],
        apply_qa=True,
        output_folder=OUTPUT_BASE / "Modern_Tool05_Geology",
        options={"study_area_name": "ModernDesert"}
    )

    # ---------------------------------------------------------
    # TEST 5: Modern Scene (LC09 C2 L2) - Tool 07 Geological Composites
    # Presets: L89_753, L89_762, L89_CRC1, L89_CRC2
    # ---------------------------------------------------------
    run_test(
        name="MODERN_TOOL07_GEOLOGICAL_COMPOSITES",
        tool="geological_composites",
        input_folder=MODERN_SCENE,
        selected=["L89_753", "L89_762", "L89_CRC1", "L89_CRC2"],
        apply_qa=True,
        output_folder=OUTPUT_BASE / "Modern_Tool07_Composites",
        options={"study_area_name": "ModernDesert"}
    )

    # ---------------------------------------------------------
    # TEST 6: Legacy Scene (LC8 Pre-Collection L1T) - Tool 01 Spectral Indices
    # (allow_toa=True, apply_qa=False because legacy BQA has no cloud confidence threshold)
    # ---------------------------------------------------------
    run_test(
        name="LEGACY_TOOL01_SPECTRAL_INDICES",
        tool="spectral_indices",
        input_folder=LEGACY_SCENE,
        selected=["NDVI"],
        apply_qa=False,
        output_folder=OUTPUT_BASE / "Legacy_Tool01_Indices",
        options={"allow_toa": True, "study_area_name": "LegacySinai"}
    )

    # ---------------------------------------------------------
    # TEST 7: Legacy Scene (LC8 Pre-Collection L1T) - Tool 02 Surface Temperature
    # (allow_toa=True, automatic radiance-to-Kelvin derivation + NDVI emissivity)
    # ---------------------------------------------------------
    run_test(
        name="LEGACY_TOOL02_SURFACE_TEMPERATURE",
        tool="surface_temperature",
        input_folder=LEGACY_SCENE,
        selected=["LST_CELSIUS"],
        apply_qa=False,
        output_folder=OUTPUT_BASE / "Legacy_Tool02_Temperature",
        options={"allow_toa": True, "ndvi_assisted": True, "study_area_name": "LegacySinai"}
    )

    # ---------------------------------------------------------
    # TEST 8: Legacy Scene (LC8 Pre-Collection L1T) - Tool 05 Geological Analysis
    # (allow_toa=True)
    # ---------------------------------------------------------
    run_test(
        name="LEGACY_TOOL05_GEOLOGY",
        tool="geological_analysis",
        input_folder=LEGACY_SCENE,
        selected=["IRON_OXIDE", "FERRIC_IRON", "FERROUS_IRON", "CLAY_ALTERATION", "FEAI", "FEI", "FESI", "LATI"],
        apply_qa=False,
        output_folder=OUTPUT_BASE / "Legacy_Tool05_Geology",
        options={"allow_toa": True, "study_area_name": "LegacySinai"}
    )

    # ---------------------------------------------------------
    # TEST 9: Legacy Scene (LC8 Pre-Collection L1T) - Tool 07 Geological Composites
    # (allow_toa=True)
    # ---------------------------------------------------------
    run_test(
        name="LEGACY_TOOL07_GEOLOGICAL_COMPOSITES",
        tool="geological_composites",
        input_folder=LEGACY_SCENE,
        selected=["L89_753", "L89_CRC1"],
        apply_qa=False,
        output_folder=OUTPUT_BASE / "Legacy_Tool07_Composites",
        options={"allow_toa": True, "study_area_name": "LegacySinai"}
    )

    log_path = OUTPUT_BASE / "dual_scene_test_summary.json"
    log_path.write_text(json.dumps(results_log, indent=2, default=str), encoding="utf-8")
    print(f"\nAll dual-scene tests completed. Summary saved to {log_path}")

if __name__ == "__main__":
    main()

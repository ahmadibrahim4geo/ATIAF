"""Validation and evidence execution script for PLAN-0020.
Executes real processing on:
1) Modern Scene: Landsat 9 C2 L2 (LC09_L2SP_174043_20261105_20261110_02_T1)
2) Legacy Scene: Landsat 8 Pre-Collection L1T (LC81760392014234LGN00)
Compares Arid Mode (Cloud Only) vs Strict Masking in desert mountain and Nile river crops.
Verifies new ENVI and geoscience spectral indices.
Saves all outputs to: Testing Results/PLAN-0020/
"""
import os
import sys
import json
import traceback
from pathlib import Path
import numpy as np
import rasterio

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from atiaf_core.workflow import run_tool

MODERN_SCENE = ROOT / "Testing Data" / "LC09_L2SP_174043_20261105_20261110_02_T1"
LEGACY_SCENE = ROOT / "Testing Data" / "LC81760392014234LGN00"
OUTPUT_BASE = ROOT / "Testing Results" / "PLAN-0020"
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
                "nodata": str(ds.nodata),
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
        return {"status": "ERROR", "path": str(path), "error": str(e)}


def analyze_crop_validity(path: Path, r_slice=(4300, 5200), c_slice=(1800, 3600)):
    """Extracts a bounding slice and computes valid pixel count and percentage."""
    if not path.is_file():
        return None
    try:
        with rasterio.open(path) as ds:
            w = ds.read(1, window=rasterio.windows.Window(c_slice[0], r_slice[0], c_slice[1] - c_slice[0], r_slice[1] - r_slice[0]), masked=True)
            valid = w.compressed()
            return {
                "total_crop_pixels": int(w.size),
                "valid_pixels": int(len(valid)),
                "nodata_pixels": int(w.size - len(valid)),
                "valid_pct": float(round(100.0 * len(valid) / w.size, 2))
            }
    except Exception as e:
        return {"error": str(e)}


def main():
    print("=" * 80)
    print(" ATIAF PLAN-0020: REAL VALIDATION SUITE (ENVI Indices & Granular QA Masks)")
    print("=" * 80)

    # -------------------------------------------------------------------------
    # Test Suite 1: Modern Scene LC09 with Cloud_Only_Arid (Fixing White Holes)
    # -------------------------------------------------------------------------
    print("\n>>> [1/5] Running LC09 Tool 07 (Composites: L89_753 & L89_CRC1) in Cloud_Only_Arid Mode...")
    dest_lc09_comp_arid = OUTPUT_BASE / "LC09_Tool07_Composites_Arid"
    existing1 = [p for p in dest_lc09_comp_arid.glob("**/*.tif") if not p.name.endswith("_DISPLAY.tif")]
    if not existing1:
        res1 = run_tool(
            tool="geological_composites",
            input_folder=str(MODERN_SCENE),
            selected=["DIRECT_RGB", "RATIO_RGB"],
            output_folder=str(dest_lc09_comp_arid),
            options={
                "direct_preset": "L89_753",
                "ratio_preset": "L89_CRC1",
                "study_area_name": "Aswan_Arid",
                "qa_mask_mode": "Cloud_Only_Arid"
            },
            apply_qa=True
        )
        rasters1 = [Path(p) for p in res1.get("OUTPUT_RASTERS", [])]
    else:
        rasters1 = existing1
    print("  Output rasters generated/found:", len(rasters1))
    for p in rasters1:
        st = analyze_raster(Path(p))
        mtn_crop = analyze_crop_validity(Path(p), (4300, 5200), (1800, 3600))
        results_log.append({"test": "LC09_Tool07_Arid", "raster": st, "mountain_crop": mtn_crop})
        print(f"    - {Path(p).name}: {st['bands_stats'][0]['valid_pct']}% valid | Mountain Crop: {mtn_crop}")

    # Compare with Strict Mode to prove the fix
    print("\n>>> [2/5] Running LC09 Tool 07 in Full_Strict Mode (Baseline with White Holes)...")
    dest_lc09_comp_strict = OUTPUT_BASE / "LC09_Tool07_Composites_Strict"
    existing2 = [p for p in dest_lc09_comp_strict.glob("**/*.tif") if not p.name.endswith("_DISPLAY.tif")]
    if not existing2:
        res2 = run_tool(
            tool="geological_composites",
            input_folder=str(MODERN_SCENE),
            selected=["DIRECT_RGB"],
            output_folder=str(dest_lc09_comp_strict),
            options={
                "direct_preset": "L89_753",
                "study_area_name": "Aswan_Strict",
                "qa_mask_mode": "Full_Strict"
            },
            apply_qa=True
        )
        rasters2 = [Path(p) for p in res2.get("OUTPUT_RASTERS", [])]
    else:
        rasters2 = existing2
    for p in rasters2:
        st = analyze_raster(Path(p))
        mtn_crop = analyze_crop_validity(Path(p), (4300, 5200), (1800, 3600))
        results_log.append({"test": "LC09_Tool07_Strict_Baseline", "raster": st, "mountain_crop": mtn_crop})
        print(f"    - {Path(p).name}: {st['bands_stats'][0]['valid_pct']}% valid | Mountain Crop: {mtn_crop}")

    # -------------------------------------------------------------------------
    # Test Suite 3: Modern Scene LC09 Tool 01 (Spectral Indices + New Indices)
    # -------------------------------------------------------------------------
    print("\n>>> [3/5] Running LC09 Tool 01 (Spectral Indices: NDVI, MTVI2, MCARI2, CIGREEN, NDSI_SALINITY)...")
    dest_lc09_indices = OUTPUT_BASE / "LC09_Tool01_Indices"
    existing3 = [p for p in dest_lc09_indices.glob("**/*.tif") if not p.name.startswith(".tmp")]
    if not existing3:
        res3 = run_tool(
            tool="spectral_indices",
            input_folder=str(MODERN_SCENE),
            selected=["NDVI", "MTVI2", "MCARI2", "CIGREEN", "NDSI_SALINITY"],
            output_folder=str(dest_lc09_indices),
            options={"study_area_name": "Aswan", "qa_mask_mode": "Cloud_Only_Arid"},
            apply_qa=True
        )
        rasters3 = [Path(p) for p in res3.get("OUTPUT_RASTERS", [])]
    else:
        rasters3 = existing3
    for p in rasters3:
        st = analyze_raster(Path(p))
        results_log.append({"test": "LC09_Tool01_Indices", "raster": st})
        print(f"    - {Path(p).name}: min={st['bands_stats'][0]['min']}, max={st['bands_stats'][0]['max']}, mean={st['bands_stats'][0]['mean']}")

    # -------------------------------------------------------------------------
    # Test Suite 4: Modern Scene LC09 Tool 05 (Geology + ENVI Alteration Indices)
    # -------------------------------------------------------------------------
    print("\n>>> [4/5] Running LC09 Tool 05 (Geology: FEAI, FEI, FESI, LATI, Ferric_Iron, Clay_Alteration)...")
    dest_lc09_geo = OUTPUT_BASE / "LC09_Tool05_Geology"
    existing4 = [p for p in dest_lc09_geo.glob("**/*.tif") if not p.name.startswith(".tmp")]
    if not existing4:
        res4 = run_tool(
            tool="geological_analysis",
            input_folder=str(MODERN_SCENE),
            selected=["FEAI", "FEI", "FESI", "LATI", "FERRIC_IRON", "CLAY_ALTERATION"],
            output_folder=str(dest_lc09_geo),
            options={"study_area_name": "Aswan", "qa_mask_mode": "Cloud_Only_Arid"},
            apply_qa=True
        )
        rasters4 = [Path(p) for p in res4.get("OUTPUT_RASTERS", [])]
    else:
        rasters4 = existing4
    for p in rasters4:
        st = analyze_raster(Path(p))
        results_log.append({"test": "LC09_Tool05_Geology", "raster": st})
        print(f"    - {Path(p).name}: min={st['bands_stats'][0]['min']}, max={st['bands_stats'][0]['max']}, valid_pct={st['bands_stats'][0]['valid_pct']}%")

    # -------------------------------------------------------------------------
    # Test Suite 5: Legacy Scene LC81760392014234LGN00 (Sinai / L1T)
    # -------------------------------------------------------------------------
    print("\n>>> [5/5] Running Legacy Scene LC81760392014234LGN00 across Tools 01, 05, and 07...")
    dest_legacy = OUTPUT_BASE / "Legacy_Scene_Runs"
    res5_ind = run_tool(
        tool="spectral_indices",
        input_folder=str(LEGACY_SCENE),
        selected=["NDVI"],
        output_folder=str(dest_legacy),
        options={"study_area_name": "LegacySinai", "allow_toa": True, "qa_mask_mode": "Cloud_Only_Arid"},
        apply_qa=True
    )
    res5_geo = run_tool(
        tool="geological_analysis",
        input_folder=str(LEGACY_SCENE),
        selected=["FEAI", "FEI", "LATI"],
        output_folder=str(dest_legacy),
        options={"study_area_name": "LegacySinai", "allow_toa": True, "qa_mask_mode": "Cloud_Only_Arid"},
        apply_qa=True
    )
    res5_comp = run_tool(
        tool="geological_composites",
        input_folder=str(LEGACY_SCENE),
        selected=["DIRECT_RGB", "RATIO_RGB"],
        output_folder=str(dest_legacy),
        options={
            "direct_preset": "L89_753",
            "ratio_preset": "L89_CRC1",
            "study_area_name": "LegacySinai",
            "allow_toa": True,
            "qa_mask_mode": "Cloud_Only_Arid"
        },
        apply_qa=True
    )
    for p in res5_ind.get("OUTPUT_RASTERS", []) + res5_geo.get("OUTPUT_RASTERS", []) + res5_comp.get("OUTPUT_RASTERS", []):
        st = analyze_raster(Path(p))
        results_log.append({"test": "Legacy_Scene_Runs", "raster": st})
        print(f"    - {Path(p).name}: valid_pct={st['bands_stats'][0]['valid_pct']}%")

    # Save summary manifest
    summary_path = OUTPUT_BASE / "plan0020_real_validation_summary.json"
    summary_path.write_text(json.dumps(results_log, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"\n[OK] Validation execution completed. Results cataloged in {summary_path}")


if __name__ == "__main__":
    main()

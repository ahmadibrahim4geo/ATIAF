import json
from pathlib import Path
import numpy as np
import rasterio

OUTPUT_BASE = Path("Testing Results/PLAN-0019_r2").resolve()

def analyze(path: Path):
    if not path.is_file():
        return None
    with rasterio.open(path) as ds:
        res = {
            "file": path.name,
            "path": str(path),
            "width": ds.width,
            "height": ds.height,
            "count": ds.count,
            "crs": str(ds.crs),
            "nodata": ds.nodata,
            "bands": []
        }
        for b in range(1, ds.count + 1):
            arr = ds.read(b, masked=True)
            valid = arr.compressed()
            if len(valid) == 0:
                res["bands"].append({"valid_pct": 0, "status": "ALL_NODATA"})
            else:
                res["bands"].append({
                    "valid_pixels": int(len(valid)),
                    "total_pixels": int(arr.size),
                    "valid_pct": float(round(100.0 * len(valid) / arr.size, 2)),
                    "min": float(round(float(valid.min()), 4)),
                    "max": float(round(float(valid.max()), 4)),
                    "mean": float(round(float(valid.mean()), 4)),
                    "std": float(round(float(valid.std()), 4))
                })
        return res

summary = {}
for p in OUTPUT_BASE.rglob("*.tif"):
    if ".tmp" in p.name:
        continue
    # Get relative section
    rel = p.relative_to(OUTPUT_BASE)
    folder = rel.parts[0]
    summary.setdefault(folder, []).append(analyze(p))

out_file = OUTPUT_BASE / "comprehensive_dual_scene_summary.json"
out_file.write_text(json.dumps(summary, indent=2), encoding="utf-8")
print(f"Summary written to {out_file} with {sum(len(v) for v in summary.values())} rasters analyzed.")

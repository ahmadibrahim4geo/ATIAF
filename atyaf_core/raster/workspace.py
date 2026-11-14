"""Additive, non-destructive Work/Results workspace and run manifest manager."""

from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
from typing import Any, Dict, List, Optional
import uuid


class WorkspaceManager:
    """Manages the non-destructive, append-only ATIAF workspace structure per
    Specification Section 4 and Decisions D-004, D-005, D-006.
    
    Layout:
      <ROOT>/Work/Preprocessing_Cache/...
      <ROOT>/Results/<Category>/<Method>/<Product>_<SCENE_ID>_FULL.tif
      <ROOT>/Results/<Category>/<Method>/<Product>_<SCENE_ID>_<AOI>_CLIP.tif
      <ROOT>/Results/Reports/Runs/<RUN_ID>/
    """

    @classmethod
    def resolve_workspace_roots(
        cls,
        scene_path: Path,
        custom_destination: Optional[Path] = None,
        is_multi_scene: bool = False,
    ) -> Tuple_Roots:
        """Determines the exact Work and Results directory roots based on input
        and destination settings, without ever generating 'Results_2'.
        """
        scene_path = Path(scene_path).resolve()

        if custom_destination is not None:
            dest_root = Path(custom_destination).resolve()
            if is_multi_scene:
                scene_root = dest_root / scene_path.name
            else:
                scene_root = dest_root / scene_path.name
        else:
            scene_root = scene_path

        work_dir = scene_root / "Work"
        cache_dir = work_dir / "Preprocessing_Cache"
        results_dir = scene_root / "Results"
        reports_dir = results_dir / "Reports"

        work_dir.mkdir(parents=True, exist_ok=True)
        cache_dir.mkdir(parents=True, exist_ok=True)
        results_dir.mkdir(parents=True, exist_ok=True)
        reports_dir.mkdir(parents=True, exist_ok=True)

        return scene_root, work_dir, cache_dir, results_dir, reports_dir

    @classmethod
    def compute_cache_fingerprint(
        cls,
        source_paths: List[Path],
        method_name: str,
        parameters: Dict[str, Any],
        target_crs_str: Optional[str] = None,
    ) -> str:
        """Generates a reproducible SHA-256 fingerprint for caching intermediate rasters."""
        hasher = hashlib.sha256()
        hasher.update(method_name.encode("utf-8"))

        if target_crs_str:
            hasher.update(target_crs_str.encode("utf-8"))

        param_str = json.dumps(parameters, sort_keys=True, default=str)
        hasher.update(param_str.encode("utf-8"))

        for p in sorted(source_paths):
            p = Path(p).resolve()
            hasher.update(p.name.encode("utf-8"))
            if p.is_file():
                stat = p.stat()
                hasher.update(str(stat.st_size).encode("utf-8"))
                hasher.update(str(stat.st_mtime_ns).encode("utf-8"))

        return hasher.hexdigest()[:16]

    @classmethod
    def get_output_raster_path(
        cls,
        results_dir: Path,
        category: str,
        method_name: str,
        scene_id: str,
        is_clip: bool = False,
        aoi_slug: Optional[str] = None,
    ) -> Path:
        """Determines the standard hierarchical output path for a calculated product."""
        cat_dir = results_dir / category / method_name
        cat_dir.mkdir(parents=True, exist_ok=True)

        if is_clip:
            slug = aoi_slug or "AOI"
            filename = f"{method_name}_{scene_id}_{slug}_CLIP.tif"
        else:
            filename = f"{method_name}_{scene_id}_FULL.tif"

        return cat_dir / filename

    @classmethod
    def create_run_manifest(
        cls,
        reports_dir: Path,
        scene_id: str,
        tool_name: str,
        parameters: Dict[str, Any],
        output_products: List[Dict[str, Any]],
        qa_summary: Optional[Dict[str, Any]] = None,
        log_messages: Optional[List[str]] = None,
        extra_metadata: Optional[Dict[str, Any]] = None,
    ) -> Path:
        """Writes the immutable run manifest, parameters, and log under Reports/Runs/<RUN_ID>/."""
        timestamp_str = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
        run_uuid = uuid.uuid4().hex[:8]
        run_id = f"RUN_{timestamp_str}_{run_uuid}"

        run_dir = reports_dir / "Runs" / run_id
        run_dir.mkdir(parents=True, exist_ok=True)

        def json_encoder(obj):
            if hasattr(obj, "item"):
                return obj.item()
            return str(obj)

        # 1. Processing_Manifest.json
        manifest_data = {
            "run_id": run_id,
            "scene_id": scene_id,
            "tool_name": tool_name,
            "timestamp_utc": datetime.now(timezone.utc).isoformat(),
            "output_products": output_products,
            "qa_summary": qa_summary or {},
        }
        if extra_metadata:
            manifest_data.update(extra_metadata)
        (run_dir / "Processing_Manifest.json").write_text(
            json.dumps(manifest_data, indent=2, ensure_ascii=False, default=json_encoder) + "\n",
            encoding="utf-8",
        )

        # 2. Parameters.json
        (run_dir / "Parameters.json").write_text(
            json.dumps(parameters, indent=2, ensure_ascii=False, default=json_encoder) + "\n",
            encoding="utf-8",
        )

        # 3. Quality_Assessment.csv
        csv_lines = ["Metric,Value\n"]
        if qa_summary:
            for k, v in qa_summary.items():
                csv_lines.append(f"{k},{v}\n")
        (run_dir / "Quality_Assessment.csv").write_text("".join(csv_lines), encoding="utf-8")

        # 4. Processing_Log.txt
        log_lines = log_messages or ["Processing completed successfully."]
        (run_dir / "Processing_Log.txt").write_text("\n".join(log_lines) + "\n", encoding="utf-8")

        return run_dir


# Helper type annotation
from typing import Tuple
Tuple_Roots = Tuple[Path, Path, Path, Path, Path]

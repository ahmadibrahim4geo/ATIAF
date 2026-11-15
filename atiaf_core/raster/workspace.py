"""Additive, non-destructive Work/Results workspace and run manifest manager."""

from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
from typing import Any, Dict, List, Optional
import uuid
from html import escape
from atiaf_core.execution_context import RUN_OPTIONS


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
    ) -> tuple[Path, Path, Path, Path, Path]:
        """Determines the exact Work and Results directory roots based on input
        and destination settings, without ever generating 'Results_2'.
        """
        scene_path = Path(scene_path).resolve()

        if custom_destination is not None and Path(custom_destination).resolve() != scene_path:
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

        return cls.unique_path(cat_dir / filename)

    @staticmethod
    def unique_path(path: Path) -> Path:
        """A separate immutable filename for every calculation, including concurrent runs."""
        path = Path(path)
        return path.with_name(f'{path.stem}_RUN-{uuid.uuid4().hex}{path.suffix}')

    @classmethod
    def _generate_run_html(
        cls,
        run_id: str,
        scene_id: str,
        tool_name: str,
        timestamp_iso: str,
        parameters: Dict[str, Any],
        output_products: List[Dict[str, Any]],
        qa_summary: Dict[str, Any],
        log_lines: List[str],
        extra_metadata: Optional[Dict[str, Any]] = None,
    ) -> str:
        """Renders a self-contained, responsive, styled bilingual HTML run report."""
        param_rows = []
        run_id, scene_id, tool_name, timestamp_iso = [escape(str(value)) for value in (run_id, scene_id, tool_name, timestamp_iso)]
        for k, v in parameters.items():
            param_rows.append(f"<tr><th>{escape(str(k))}</th><td><code>{escape(str(v))}</code></td></tr>")
        param_table = "".join(param_rows) if param_rows else "<tr><td colspan='2'>No parameters recorded</td></tr>"

        qa_rows = []
        for k, v in qa_summary.items():
            qa_rows.append(f"<tr><th>{escape(str(k))}</th><td><strong>{escape(str(v))}</strong></td></tr>")
        qa_table = "".join(qa_rows) if qa_rows else "<tr><td colspan='2'>No QA metrics recorded</td></tr>"

        prod_rows = []
        for p in output_products:
            name = escape(str(p.get("product_name") or p.get("acronym") or "Output Raster"))
            full_p = p.get("full_path") or ""
            clip_p = p.get("clipped_path") or "—"
            pixels = p.get("valid_pixels") or p.get("pixel_count") or "—"
            prod_rows.append(
                f"<tr><td><strong>{name}</strong></td>"
                f"<td><code>{Path(full_p).name if full_p else '—'}</code></td>"
                f"<td><code>{Path(clip_p).name if clip_p != '—' else '—'}</code></td>"
                f"<td>{pixels}</td></tr>"
            )
        prod_table = "".join(prod_rows) if prod_rows else "<tr><td colspan='4'>No outputs recorded</td></tr>"

        logs_escaped = "\n".join(escape(str(line)) for line in log_lines)

        html = f"""<!DOCTYPE html>
<html lang="en" dir="ltr">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>ATIAF Run Report — {run_id}</title>
  <style>
    :root {{
      --primary: #0284c7;
      --primary-dark: #0369a1;
      --bg: #f8fafc;
      --surface: #ffffff;
      --text: #0f172a;
      --muted: #64748b;
      --border: #e2e8f0;
      --success: #16a34a;
    }}
    * {{ box-sizing: border-box; margin: 0; padding: 0; font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; }}
    body {{ background: var(--bg); color: var(--text); line-height: 1.5; padding: 24px; }}
    .container {{ max-width: 960px; margin: 0 auto; background: var(--surface); border-radius: 12px; box-shadow: 0 4px 6px -1px rgba(0,0,0,0.1); border: 1px solid var(--border); overflow: hidden; }}
    header {{ background: linear-gradient(135deg, #0f172a 0%, #1e293b 100%); color: #fff; padding: 28px 32px; border-bottom: 3px solid var(--primary); }}
    .brand {{ font-size: 0.85rem; text-transform: uppercase; letter-spacing: 0.1em; color: #38bdf8; font-weight: 700; margin-bottom: 6px; }}
    h1 {{ font-size: 1.6rem; font-weight: 700; display: flex; justify-content: space-between; align-items: center; }}
    .badge {{ font-size: 0.75rem; background: var(--success); color: #fff; padding: 4px 10px; border-radius: 9999px; text-transform: uppercase; font-weight: 600; }}
    .content {{ padding: 32px; display: grid; gap: 28px; }}
    .meta-grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 16px; background: #f1f5f9; padding: 16px; border-radius: 8px; }}
    .meta-item label {{ display: block; font-size: 0.75rem; text-transform: uppercase; color: var(--muted); font-weight: 600; margin-bottom: 2px; }}
    .meta-item span {{ font-size: 0.95rem; font-weight: 600; }}
    h2 {{ font-size: 1.15rem; color: #1e293b; border-bottom: 2px solid var(--border); padding-bottom: 8px; margin-bottom: 12px; display: flex; justify-content: space-between; }}
    h2 span.ar {{ font-family: "Segoe UI", Tahoma, sans-serif; color: var(--muted); font-size: 0.95rem; font-weight: normal; }}
    table {{ width: 100%; border-collapse: collapse; font-size: 0.9rem; text-align: left; }}
    th, td {{ padding: 10px 14px; border-bottom: 1px solid var(--border); }}
    th {{ background: #f8fafc; color: #475569; font-weight: 600; width: 35%; }}
    code {{ background: #f1f5f9; padding: 2px 6px; border-radius: 4px; font-family: ui-monospace, SFMono-Regular, Menlo, monospace; font-size: 0.82rem; word-break: break-all; }}
    pre.log {{ background: #0f172a; color: #f8fafc; padding: 16px; border-radius: 8px; font-family: ui-monospace, SFMono-Regular, monospace; font-size: 0.8rem; overflow-x: auto; max-height: 280px; }}
    footer {{ background: #f8fafc; padding: 16px 32px; border-top: 1px solid var(--border); font-size: 0.8rem; color: var(--muted); text-align: center; }}
  </style>
</head>
<body>
  <div class="container">
    <header>
      <div class="brand">ATIAF • Advanced Thematic Imagery Analysis Framework | أطياف</div>
      <h1>Scientific Run Report <span class="badge">Completed | منجز</span></h1>
    </header>
    <div class="content">
      <div class="meta-grid">
        <div class="meta-item"><label>Run ID | معرف التشغيل</label><span>{run_id}</span></div>
        <div class="meta-item"><label>Scene ID | معرف المرئية</label><span>{scene_id}</span></div>
        <div class="meta-item"><label>Tool | الأداة</label><span>{tool_name}</span></div>
        <div class="meta-item"><label>Timestamp UTC | التاريخ</label><span>{timestamp_iso}</span></div>
      </div>

      <section>
        <h2>Execution Parameters <span class="ar">معاملات وبيانات التشغيل</span></h2>
        <table><tbody>{param_table}</tbody></table>
      </section>

      <section>
        <h2>Quality Assessment & Metrics <span class="ar">تقييم الجودة والمؤشرات العلمية</span></h2>
        <table><tbody>{qa_table}</tbody></table>
      </section>

      <section>
        <h2>Generated Products <span class="ar">المنتجات الناتجة</span></h2>
        <table>
          <thead>
            <tr>
              <th style="width:25%">Product | المنتج</th>
              <th style="width:35%">Full Raster | المسار الكامل</th>
              <th style="width:25%">AOI Clip | الاقتطاع</th>
              <th style="width:15%">Valid Pixels</th>
            </tr>
          </thead>
          <tbody>{prod_table}</tbody>
        </table>
      </section>

      <section>
        <h2>Execution Log <span class="ar">سجل العمليات والرسائل</span></h2>
        <pre class="log">{logs_escaped}</pre>
      </section>
    </div>
    <footer>
      ATIAF v1.0.0 — Open-Source Deterministic Scientific Remote Sensing Engine • MIT License
    </footer>
  </div>
</body>
</html>
"""
        return html

    @classmethod
    def _update_cumulative_index(cls, reports_dir: Path) -> Path:
        """Scans all existing runs in Reports/Runs/ and regenerates the cumulative Reports/index.html."""
        runs_dir = reports_dir / "Runs"
        runs = []

        if runs_dir.is_dir():
            for p in sorted(runs_dir.iterdir(), reverse=True):
                if p.is_dir():
                    manifest_file = p / "Processing_Manifest.json"
                    if manifest_file.is_file():
                        try:
                            data = json.loads(manifest_file.read_text(encoding="utf-8"))
                            runs.append({
                                "run_id": data.get("run_id", p.name),
                                "tool_name": data.get("tool_name", "Unknown"),
                                "scene_id": data.get("scene_id", "—"),
                                "timestamp_utc": data.get("timestamp_utc", "—"),
                                "products_count": len(data.get("output_products", [])),
                                "run_rel_html": f"Runs/{p.name}/report.html",
                                "run_rel_json": f"Runs/{p.name}/Processing_Manifest.json",
                            })
                        except Exception:
                            pass

        table_rows = []
        for r in runs:
            r = {key: escape(str(value)) for key, value in r.items()}
            table_rows.append(
                f"<tr>"
                f"<td><strong><a href='{r['run_rel_html']}'>{r['run_id']}</a></strong></td>"
                f"<td>{r['tool_name']}</td>"
                f"<td><code>{r['scene_id']}</code></td>"
                f"<td>{r['timestamp_utc']}</td>"
                f"<td><span class='badge-count'>{r['products_count']}</span></td>"
                f"<td><a class='btn' href='{r['run_rel_html']}'>HTML Report</a> <a href='{r['run_rel_html'].replace('report.html', 'report.en.html')}'>English</a> <a href='{r['run_rel_html'].replace('report.html', 'report.ar.html')}'>العربية</a> <a class='btn-ghost' href='{r['run_rel_json']}'>JSON</a></td>"
                f"</tr>"
            )
        tbody = "".join(table_rows) if table_rows else "<tr><td colspan='6'>No runs recorded yet.</td></tr>"

        index_html = f"""<!DOCTYPE html>
<html lang="en" dir="ltr">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>ATIAF — Cumulative Processing Reports Index | فهرس التقارير</title>
  <style>
    :root {{
      --primary: #0284c7;
      --bg: #f8fafc;
      --surface: #ffffff;
      --text: #0f172a;
      --muted: #64748b;
      --border: #e2e8f0;
      --success: #16a34a;
    }}
    * {{ box-sizing: border-box; margin: 0; padding: 0; font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; }}
    body {{ background: var(--bg); color: var(--text); line-height: 1.5; padding: 24px; }}
    .container {{ max-width: 1040px; margin: 0 auto; background: var(--surface); border-radius: 12px; box-shadow: 0 4px 6px -1px rgba(0,0,0,0.1); border: 1px solid var(--border); overflow: hidden; }}
    header {{ background: linear-gradient(135deg, #0f172a 0%, #1e293b 100%); color: #fff; padding: 28px 32px; border-bottom: 3px solid var(--primary); }}
    .brand {{ font-size: 0.85rem; text-transform: uppercase; letter-spacing: 0.1em; color: #38bdf8; font-weight: 700; margin-bottom: 6px; }}
    h1 {{ font-size: 1.6rem; font-weight: 700; }}
    .subtitle {{ color: #cbd5e1; font-size: 0.95rem; margin-top: 4px; }}
    .content {{ padding: 32px; }}
    .stats-bar {{ display: flex; gap: 24px; margin-bottom: 24px; padding: 16px; background: #f1f5f9; border-radius: 8px; }}
    .stat-box strong {{ font-size: 1.5rem; color: var(--primary); display: block; }}
    .stat-box span {{ font-size: 0.8rem; text-transform: uppercase; color: var(--muted); font-weight: 600; }}
    table {{ width: 100%; border-collapse: collapse; font-size: 0.9rem; text-align: left; }}
    th, td {{ padding: 12px 14px; border-bottom: 1px solid var(--border); }}
    th {{ background: #f8fafc; color: #475569; font-weight: 600; }}
    tr:hover {{ background: #f8fafc; }}
    a {{ color: var(--primary); text-decoration: none; }}
    a:hover {{ text-decoration: underline; }}
    code {{ background: #f1f5f9; padding: 2px 6px; border-radius: 4px; font-family: ui-monospace, SFMono-Regular, monospace; font-size: 0.82rem; }}
    .badge-count {{ background: #e0f2fe; color: #0369a1; padding: 2px 8px; border-radius: 9999px; font-weight: 700; font-size: 0.8rem; }}
    .btn {{ display: inline-block; background: var(--primary); color: #fff; padding: 4px 10px; border-radius: 6px; font-size: 0.78rem; font-weight: 600; }}
    .btn:hover {{ background: #0369a1; text-decoration: none; }}
    .btn-ghost {{ display: inline-block; background: #e2e8f0; color: #334155; padding: 4px 10px; border-radius: 6px; font-size: 0.78rem; font-weight: 600; margin-left: 4px; }}
    .btn-ghost:hover {{ background: #cbd5e1; text-decoration: none; }}
    footer {{ background: #f8fafc; padding: 16px 32px; border-top: 1px solid var(--border); font-size: 0.8rem; color: var(--muted); text-align: center; }}
  </style>
</head>
<body>
  <div class="container">
    <header>
      <div class="brand">ATIAF • Advanced Thematic Imagery Analysis Framework | أطياف</div>
      <h1>Cumulative Processing Reports Index</h1>
      <div class="subtitle">فهرس تقارير المعالجة التراكمي لجميع التشغيلات والنتائج</div>
    </header>
    <div class="content">
      <div class="stats-bar">
        <div class="stat-box"><strong>{len(runs)}</strong><span>Total Runs Recorded | إجمالي التشغيلات</span></div>
      </div>
      <table>
        <thead>
          <tr>
            <th>Run ID | المعرف</th>
            <th>Tool | الأداة</th>
            <th>Scene ID | المشهد</th>
            <th>Timestamp UTC | التاريخ</th>
            <th>Products | النواتج</th>
            <th>Actions | الإجراءات</th>
          </tr>
        </thead>
        <tbody>
          {tbody}
        </tbody>
      </table>
    </div>
    <footer>
      ATIAF v1.0.0 — Reports index automatically updated across tools without erasing prior reports.
    </footer>
  </div>
</body>
</html>
"""
        index_path = reports_dir / "index.html"
        index_path.write_text(index_html, encoding="utf-8")
        return index_path

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
        """Writes the immutable run manifest, parameters, log, and HTML report under Reports/Runs/<RUN_ID>/,
        and dynamically updates the cumulative Reports/index.html.
        """
        timestamp_str = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
        parameters = dict(parameters)
        options = RUN_OPTIONS.get()
        parameters['requested_output_crs'] = options.get('output_crs')
        parameters['user_options'] = options.get('user_options', {})
        parameters['grid_resampling'] = 'nearest; aligned to first required band, then projected if selected'
        extra_metadata = dict(extra_metadata or {})
        if options.get('source_scene'):
            extra_metadata['source_scene'] = options['source_scene']
        extra_metadata['requested_calculations'] = options.get('selected', [])
        extra_metadata['scientific_definitions'] = options.get('scientific_definitions', [])
        run_uuid = uuid.uuid4().hex[:8]
        run_id = f"RUN_{timestamp_str}_{run_uuid}"
        timestamp_iso = datetime.now(timezone.utc).isoformat()

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
            "timestamp_utc": timestamp_iso,
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

        # 5. report.html (Standalone styled bilingual run report)
        html_content = cls._generate_run_html(
            run_id=run_id,
            scene_id=scene_id,
            tool_name=tool_name,
            timestamp_iso=timestamp_iso,
            parameters=parameters,
            output_products=output_products,
            qa_summary=qa_summary or {},
            log_lines=log_lines,
            extra_metadata=extra_metadata,
        )
        (run_dir / "report.html").write_text(html_content, encoding="utf-8")
        from atiaf_core.reporting import localized_reports
        localized_reports(run_dir, manifest_data, parameters)

        # 6. Cumulative Reports/index.html update
        cls._update_cumulative_index(reports_dir)

        return run_dir


# Helper type annotation
from typing import Tuple
Tuple_Roots = Tuple[Path, Path, Path, Path, Path]

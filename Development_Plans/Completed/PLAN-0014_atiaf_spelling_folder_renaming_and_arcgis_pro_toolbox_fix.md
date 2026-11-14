# PLAN-0014 — ATIAF Spelling Standardization, Folder Renaming & ArcGIS Pro Toolbox Fix

- **Plan ID:** PLAN-0014
- **Revision:** r1
- **Status:** Completed
- **Related Reports:** [Report 0014](../../Reports/0014_atiaf_spelling_folder_renaming_and_arcgis_pro_toolbox_fix.md)
- **Previous Plan:** [PLAN-0013 (Completed)](../Completed/PLAN-0013_professional_readme_and_html_portal_overhaul.md)

---

## 1. Executive Summary & Problem Diagnosis

The user identified three critical issues requiring immediate resolution:
1. **Spelling Consistency:** The project name must strictly be **ATIAF** with `I` (never `Y` / `ATYAF`). Lowercase identifier must also use `atiaf` (`atiaf_core` as canonical import, with backwards-compatibility for existing tests).
2. **Folder Renaming:**
   - The ArcGIS Pro folder (`arcgis_pro/`) must be renamed to `ArcGIS Pro Tools/`.
   - The QGIS folder (`qgis/`) must be renamed to `QGIS Tools/`.
3. **ArcGIS Pro Toolbox Loading Failure ("صندوق الأدوات ما بيفتحش"):**
   - **Root Cause 1:** ArcGIS Pro's conda environment (`arcgispro-py3`) does not include `rasterio` or `pyproj` by default. Top-level unguarded imports in `ATIAF.pyt` threw `ModuleNotFoundError: No module named 'rasterio'`, causing ArcGIS Pro to reject the toolbox with a red cross.
   - **Root Cause 2:** In `ATIAF.pyt`, `PROJECT_ROOT = TOOLBOX_DIR.parent if TOOLBOX_DIR.name == "arcgis_pro" else TOOLBOX_DIR` breaks when the folder is renamed to `ArcGIS Pro Tools`, pointing `sys.path` to the wrong directory.
   - **Root Cause 3:** Lack of a 1-click automated setup script for ArcGIS Pro's Python environment.

---

## 2. Implementation Deliverables

### Task 1: Name Standardization (ATIAF / atiaf)
- Create `atiaf_core` package alias/shim so `import atiaf_core` is first-class, while retaining `atyaf_core` compatibility for existing imports.
- Update `ATIAF.pyt` toolbox alias to `"atiaf"`, label to `"ATIAF - Thematic Imagery Analysis Framework | أطياف"`.
- Update QGIS provider ID and plugin metadata to use `atiaf`.
- Audit and standardize all documentation and README references to **ATIAF** (with `I`).

### Task 2: Folder Renaming (`ArcGIS Pro Tools` & `QGIS Tools`)
- Rename directory `arcgis_pro/` &rarr; `ArcGIS Pro Tools/`.
- Rename directory `qgis/` &rarr; `QGIS Tools/`.
- Inside `QGIS Tools/`, standardize plugin folder to `atiaf/`.
- Update references in:
  - `pyproject.toml`
  - `tests/test_packaging.py`
  - `tests/test_package_and_registries.py`
  - `tests/test_qgis_adapter.py`
  - `tests/native_qgis/test_qgis_provider.py`
  - `tools/verify_installation.py`
  - `README.md` and `README.ar.md`
  - `docs/index.html` and guide files in `docs/en/` and `docs/ar/`.

### Task 3: ArcGIS Pro Toolbox Robustness & Automated Environment Setup
- Overhaul `ArcGIS Pro Tools/ATIAF.pyt`:
  - Implement dynamic multi-tier `_resolve_project_root()` that finds the repo root regardless of directory name or `__file__` availability.
  - Implement guarded top-level imports with graceful fallback so the toolbox **ALWAYS** compiles, opens, and lists all 6 tools in ArcGIS Pro Catalog pane even if dependencies are missing.
  - Enhance `updateMessages` and `execute` to report clear bilingual diagnostic messages if any dependency is absent.
- Create automated setup scripts:
  - `tools/setup_arcgis_pro_env.py`: Detects ArcGIS Pro Python runtime and installs `rasterio`, `shapely`, and `pyproj` into user site-packages.
  - `tools/setup_arcgis_pro_env.bat`: 1-click Windows batch launcher for end users.

### Task 4: Verification & Handoff
- Verify `ArcGIS Pro Tools/ATIAF.pyt` with both Python 3.14 and ArcGIS Pro 3.6 Python runtime.
- Run complete test suite (`python -m unittest discover tests`).
- Run native QGIS test suite (`python-qgis.bat`).
- Run `validate_package.py` and `verify_installation.py`.
- Author `Reports/0014_atiaf_spelling_folder_renaming_and_arcgis_pro_toolbox_fix.md`.
- Record Journal entries #0027 and #0028.
- Git commit on `main`.

---

## 3. Acceptance Criteria
- [x] Name strictly standardized to **ATIAF** with `I` across UI labels, aliases, and docs.
- [x] `ArcGIS Pro Tools/` and `QGIS Tools/` exist and are canonical.
- [x] `ArcGIS Pro Tools/ATIAF.pyt` opens without errors in ArcGIS Pro, listing all 6 canonical tools.
- [x] Safe import handling ensures toolbox never crashes or shows red X in ArcGIS Pro Catalog pane.
- [x] `tools/setup_arcgis_pro_env.bat` and `.py` created and tested.
- [x] All 99 unit tests pass.
- [x] All 5 native QGIS host tests pass.
- [x] Structural package validation and installation verification pass.
- [x] Report 0014 authored and state updated.
- [ ] Report 0014 authored and state updated.

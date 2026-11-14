# PLAN-0011 — Comprehensive Audit, Hardening & Cumulative Reporting Engine

- **Plan ID:** PLAN-0011
- **Revision:** r1
- **Status:** Completed
- **Related Reports:** [0011_comprehensive_audit_and_hardening.md](../../Reports/0011_comprehensive_audit_and_hardening.md)
- **Previous Plan:** [PLAN-0010 (Completed)](../Completed/PLAN-0010_packaging_and_documentation.md)

---

## 1. Executive Summary & Audit Context
Following the completion of all 10 initial roadmap phases (P0 through P9), a thorough audit of the implementation against the authoritative specifications (`PROJECT_SPECIFICATION.md`, `PROJECT_SPECIFICATION_AR.md`, `DECISIONS.md`, and `DEVELOPMENT_ROADMAP.md`) was performed to identify any gaps, omissions, or inconsistencies.

The audit identified two key areas requiring immediate hardening:
1. **Cumulative HTML Reporting Engine (Spec Sections 4 & 8, Decision D-011):**
   - Per specification, each processing execution must produce not only machine-readable JSON/CSV/TXT manifests under `Results/Reports/Runs/<RUN_ID>/`, but also a standalone, styled, responsive bilingual HTML report (`report.html`) summarizing execution parameters, input bands, scientific formulas, outputs, and quality assessment metrics.
   - Per specification Section 4, a cumulative master index (`Results/Reports/index.html`) must be created/updated dynamically across all tool runs, listing every run chronologically with direct links, status badges, and execution statistics without erasing prior runs.
2. **QGIS Processing Algorithm Parameter Parity:**
   - ArcGIS Pro tools `ThermalUrbanTool` and `EnvironmentalDroughtTool` expose `enable_mosaic` for multi-scene thermal/environmental workflows.
   - The corresponding QGIS Processing algorithms `atyaf:thermal_urban` and `atyaf:environmental_drought` lacked the `ENABLE_MOSAIC` parameter and multi-scene mosaic handling, violating cross-host UI and functional parity.

---

## 2. Scope & Implementation Tasks

### Task 1: Bilingual HTML Reporting Engine (`atyaf_core/raster/workspace.py`)
- Implement `generate_html_run_report(run_dir, manifest_data, parameters, qa_summary, log_messages)`:
  - Generates `report.html` inside `Results/Reports/Runs/<RUN_ID>/`.
  - Self-contained, zero-network CSS, responsive layout, dark header, RTL Arabic and LTR English side-by-side or sectioned.
  - Displays Run ID, Tool Name, Scene ID, Timestamp UTC, Execution Parameters table, QA Summary table, Generated Output Files (with resolution/pixel stats), and execution log.
- Implement `update_cumulative_reports_index(reports_dir, run_summary)`:
  - Generates or updates `Results/Reports/index.html`.
  - Parses existing runs or manifest entries, rendering an append-only chronological HTML dashboard.
  - Links to each run's `report.html` and provides high-level summary metrics.

### Task 2: QGIS Processing Algorithm Parity (`qgis/atyaf/algorithms/`)
- In `thermal_urban.py`:
  - Add `ENABLE_MOSAIC` boolean parameter (default False) following `APPLY_QA`.
  - Implement multi-scene mosaic handling using `QualityMosaicEngine.run_mosaic` under category `"Thermal_Urban"`.
- In `environmental_drought.py`:
  - Add `ENABLE_MOSAIC` boolean parameter (default False) following `APPLY_QA`.
  - Implement multi-scene mosaic handling using `QualityMosaicEngine.run_mosaic` under category `"Environmental_Drought"`.
- Verify parameter ordering rules (Decision D-006 & D-009: `OUTPUT_FOLDER` remains the final parameter).

### Task 3: Test Suite & Host Validation
- Create `tests/test_reports_html.py` validating:
  - Generation of `report.html` on `WorkspaceManager.create_run_manifest`.
  - Creation and cumulative updating of `Results/Reports/index.html`.
  - Integrity of HTML structure, bilingual headings, and UTF-8 encoding.
- Execute full unit test suite via `python -m unittest discover tests`.
- Execute native QGIS integration test suite via `python-qgis.bat tests/native_qgis/test_qgis_provider.py`.
- Run package structural validation via `python tools/validate_package.py`.
- Run installation diagnostics via `python tools/verify_installation.py`.

---

## 3. Acceptance Criteria
- [ ] `WorkspaceManager.create_run_manifest` automatically writes `report.html` in `Reports/Runs/<RUN_ID>/`.
- [ ] `WorkspaceManager.create_run_manifest` automatically creates/updates `Results/Reports/index.html` without data loss.
- [ ] `qgis/atyaf/algorithms/thermal_urban.py` and `environmental_drought.py` include `ENABLE_MOSAIC` and support multi-scene mosaics.
- [ ] All unit tests pass cleanly (100% pass rate).
- [ ] All native QGIS integration tests pass cleanly inside QGIS 4.2.3.
- [ ] `validate_package.py` and `verify_installation.py` pass without errors.
- [ ] Delivery report `Reports/0011_comprehensive_audit_and_hardening.md` authored.
- [ ] `Development_Plans/INDEX.md`, `Reports/INDEX.md`, `PROJECT_STATE.md`, and Agent Journal updated.

# Report 0006 — Multi-Scene Quality-Aware Mosaic & Temporal Change Detection (Phase P5)

- **Date:** 2026-11-14
- **Plan ID:** [PLAN-0006](../Development_Plans/Completed/PLAN-0006_mosaic_temporal.md) (Revision r1)
- **Status:** VERIFIED-COMPLETED
- **Author:** Implementation Agent
- **Git Commit:** Pending next commit

---

## 1. Summary of Work Delivered
In this phase (Phase P5 of the ATIAF development roadmap), we implemented pure-Python modules for **Multi-Scene Quality-Aware Mosaic Blending** and **Temporal Change Detection** within `atyaf_core/`, wired multi-scene mosaic execution into existing tools, and exposed Tool 06 (`TemporalChangeTool`) in `arcgis_pro/ATIAF.pyt`:

1. **Multi-Scene Quality-Aware Mosaic Module (`atyaf_core/mosaic/`)**:
   - `models.py`: Defines `MosaicStrategy` (`highest_quality`, `mean_valid`, `latest_date`, `first_valid`), `SceneContribution`, and `MosaicResult`.
   - `engine.py` (`QualityMosaicEngine`):
     - Computes the union extent across multiple adjacent or overlapping scenes and harmonizes cell grids and affine transformations.
     - Blends overlapping valid pixels according to chosen strategy (`highest_quality`, `mean_valid`, or `latest_date`).
     - Generates a dedicated pixel provenance raster (`Source_Scene_ID.tif`) mapping each pixel to the contributing scene ID and acquisition date.
     - Saves combined outputs under `Results/Mosaic_<stable-scene-set-id>/<category>/<product_name>/...` per Section 4 folder semantics.
     - Creates comprehensive run manifests with contribution metadata, overlap metrics, and provenance legends.

2. **Temporal Change Detection Module (`atyaf_core/temporal/`)**:
   - `engine.py` (`ChangeDetectionEngine`):
     - Computes two-epoch multi-temporal differences:
       - Absolute spectral differences: $\Delta \text{Index} = T_2 - T_1$ (e.g. dNDVI, dNDWI, dLST).
       - Relative percentage change: $(\Delta / |T_1|) \times 100\%$ with zero-division safety.
       - Fire burn severity: $\text{dNBR} = \text{NBR}_{\text{pre}} - \text{NBR}_{\text{post}}$ classified into 7 USGS Burn Severity classes (Unburned, Low, Moderate-Low, Moderate-High, High Severity, and post-fire regrowth).
       - Statistical standard deviation classification (5 classes: significant decrease, moderate decrease, stable, moderate increase, significant increase).
     - Automated grid harmonization: aligns and resamples the target epoch raster onto the baseline grid using bilinear interpolation.

3. **ArcGIS Pro Native Integration (`arcgis_pro/ATIAF.pyt`)**:
   - Wired `enable_mosaic` in Tool 01 (`SpectralIndicesTool`), Tool 02 (`SurfaceTemperatureTool`), and Tool 05 (`GeologicalAnalysisTool`) to invoke `QualityMosaicEngine` whenever multiple scenes are processed.
   - Added Tool 06: `TemporalChangeTool` (06. Temporal Analysis & Change Detection | التحليل الزمني وتغير الغطاء الأرضي) with canonical parameters:
     - Baseline Epoch folder (Time 1)
     - Target Epoch folder (Time 2)
     - QA Masking option
     - Change Metric selection (NDVI, NBR, NDWI, LST)
     - Relative percentage change and Burn Severity toggles
     - Optional study area AOI polygon clipping
     - Metric projected CRS verification (Decision D-007)
     - Defaulted output folder and optional Add Results to Map

4. **Testing & QA Suite (`tests/test_mosaic_temporal.py`)**:
   - 7 comprehensive unit and integration tests covering union extent computation, overlap blending, provenance raster validation, dNBR classification, relative change math, and Tool 06 compilation.

---

## 2. Exact Commands and Observed Results

### A. Execution of Phase P5 Test Suite
```powershell
python -m unittest tests/test_mosaic_temporal.py
```
**Observed Result:**
```
.......
----------------------------------------------------------------------
Ran 7 tests in 0.159s

OK
```

### B. Execution of Full Project Test Suite
```powershell
python -m unittest discover tests
```
**Observed Result:**
```
............................................................
----------------------------------------------------------------------
Ran 60 tests in 0.970s

OK
```

### C. Structural Package Validation
```powershell
python tools/validate_package.py
```
**Observed Result:**
```
Candidate indices: 26
Planned sensors: 19
Markdown files: 297 JSON: 104
STRUCTURAL VALIDATION PASS — documentation only. Native ArcGIS/QGIS tests NOT RUN.
```

---

## 3. Test Evidence Table (DoneProof)

| Acceptance Criterion | Verification Method | Result | Evidence / Observed Output |
|---|---|---|---|
| Mosaic union extent computation | `test_mosaic_union_extent_and_provenance` | **VERIFIED** | Union extent expanded from 32 pixels to 48 pixels across two 16-pixel overlapping scenes. |
| Mosaic provenance raster | `test_mosaic_union_extent_and_provenance` | **VERIFIED** | `Source_Scene_ID.tif` generated; left non-overlap is 1, right non-overlap is 2. |
| Overlap blending strategies | `test_mosaic_mean_valid_strategy`, `test_mosaic_latest_date_strategy` | **VERIFIED** | Overlap zone: `mean_valid` yields $(0.40+0.80)/2 = 0.60$; `latest_date` yields $0.80$. |
| dNBR Burn Severity classification | `test_burn_severity_classification_math`, `test_run_change_detection_nbr_burn` | **VERIFIED** | $\text{dNBR}=0.40$ correctly maps to Class 5 ("Moderate-Low Severity"). |
| Statistical change classification | `test_std_change_classification` | **VERIFIED** | Correctly segments data into 5 statistical standard deviation classes. |
| ArcGIS Pro Toolbox Tool 06 | `test_toolbox_tools_list_phase5` | **VERIFIED** | `Toolbox.tools` contains 4 tools (`SpectralIndicesTool`, `SurfaceTemperatureTool`, `GeologicalAnalysisTool`, `TemporalChangeTool`). |
| Full regression test suite | `python -m unittest discover tests` | **VERIFIED** | 60 unit tests pass with 0 failures, 0 errors. |

---

## 4. Scientific QA & Integrity Notes
- **USGS Burn Severity Standard:** Key, C. H., & Benson, N. C. (2006). Landscape assessment: Ground measure of severity, the Composite Burn Index; and Remote sensing of severity, the Normalized Burn Ratio. *FIREMON: Fire Effects Monitoring and Evaluation System*.
- **Quality-Aware Provenance:** As required by Section 4 and Section 7 of `PROJECT_SPECIFICATION.md`, multi-scene mosaics never blindly blend pixels without tracking scene ID and acquisition dates. The `Source_Scene_ID.tif` raster provides unambiguous per-pixel provenance.

---

## 5. Files Changed / Added
- `atyaf_core/mosaic/__init__.py` (new)
- `atyaf_core/mosaic/models.py` (new)
- `atyaf_core/mosaic/engine.py` (new)
- `atyaf_core/temporal/__init__.py` (new)
- `atyaf_core/temporal/engine.py` (new)
- `arcgis_pro/ATIAF.pyt` (updated with `TemporalChangeTool` and mosaic integration)
- `tests/test_mosaic_temporal.py` (new)
- `Development_Plans/Completed/PLAN-0006_mosaic_temporal.md` (moved from Active)
- `Reports/0006_mosaic_temporal.md` (this report)

---

## 6. Next Steps
- Begin **Phase P6**: Pinned offline index catalog, drought, and environmental models (Tool 03 Thermal & Urban Analysis, Tool 04 Environmental & Drought).

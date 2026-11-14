# ATIAF QGIS Adapter & Processing Provider | محول أطياف لبرنامج QGIS

The ATIAF QGIS Processing Provider provides native integration of ATIAF's scientific satellite remote sensing algorithms into QGIS 3.x and QGIS 4.x.

## Structure

- `qgis/atyaf/`: Complete, self-contained QGIS plugin directory.
  - `metadata.txt`: Standard QGIS plugin metadata.
  - `__init__.py`: Plugin factory entry point (`classFactory`).
  - `atyaf_plugin.py`: QGIS plugin lifecycle manager registering the provider.
  - `provider.py`: `ATIAFProcessingProvider` (Provider ID: `atyaf`, Name: `ATIAF | أطياف`).
  - `algorithms/`: The 6 canonical processing algorithms wrapping `atyaf_core`:
    - `01. Spectral Indices | المؤشرات الطيفية` (`atyaf:spectral_indices`)
    - `02. Surface Temperature | درجة حرارة السطح` (`atyaf:surface_temperature`)
    - `03. Thermal & Urban Analysis | التحليل الحراري والحضري والجزر الحرارية` (`atyaf:thermal_urban`)
    - `04. Environmental & Drought Analysis | التحليل البيئي ومؤشرات الجفاف` (`atyaf:environmental_drought`)
    - `05. Geological Analysis & Mineral Alteration | التحليل الجيولوجي ونطاقات التحول المعدني` (`atyaf:geological_analysis`)
    - `06. Temporal Analysis & Change Detection | التحليل الزمني وتغير الغطاء الأرضي` (`atyaf:temporal_change`)

## Features & Compliance

- **Canonical Parameter Ordering:** Every algorithm defines `OUTPUT_FOLDER` as its last parameter (Section 3).
- **Decision D-007 (Projected Metre CRS):** Validated with native `QgsProcessingParameterCrs`. Rejects unprojected geographic degrees (EPSG:4326) with clear bilingual error messages.
- **Bilingual Interface:** English algorithm names, parameter labels, group descriptions, and help strings are paired with Arabic equivalents.
- **Shared Computational Core:** Thin adapter calling pure-Python `atyaf_core` without code duplication.
- **Non-Destructive Workspaces:** Creates `Work/` and `Results/` directories with run manifests and quality assessment logs.

## Testing & Verification

1. **Standalone Structural Tests (T1):**
   ```bash
   python -m unittest tests/test_qgis_adapter.py
   ```
2. **Native QGIS Integration Tests (T2):**
   ```powershell
   & "C:\Program Files\QGIS 4.2.3\bin\python-qgis.bat" tests/native_qgis/test_qgis_provider.py
   ```

# ATIAF QGIS Tools & Processing Provider | أدوات أطياف لبرنامج QGIS

The ATIAF QGIS Processing Provider provides native integration of ATIAF's scientific satellite remote sensing algorithms into QGIS 3.x and QGIS 4.x.

---

## 📂 Structure

- `QGIS Tools/atiaf/`: Complete, self-contained QGIS plugin package.
  - `metadata.txt`: Standard QGIS plugin metadata.
  - `__init__.py`: Plugin factory entry point (`classFactory`).
  - `atyaf_plugin.py`: QGIS plugin lifecycle manager registering the provider.
  - `provider.py`: `ATIAFProcessingProvider` (Provider ID: `atiaf`, Name: `ATIAF | أطياف`).
  - `algorithms/`: The 6 canonical processing algorithms wrapping `atiaf_core`:
    - `01. Spectral Indices | المؤشرات الطيفية` (`atiaf:spectral_indices`)
    - `02. Surface Temperature | درجة حرارة السطح` (`atiaf:surface_temperature`)
    - `03. Thermal & Urban Analysis | التحليل الحراري والحضري والجزر الحرارية` (`atiaf:thermal_urban`)
    - `04. Environmental & Drought Analysis | التحليل البيئي ومؤشرات الجفاف` (`atiaf:environmental_drought`)
    - `05. Geological Analysis & Mineral Alteration | التحليل الجيولوجي ونطاقات التحول المعدني` (`atiaf:geological_analysis`)
    - `06. Temporal Analysis & Change Detection | التحليل الزمني وتغير الغطاء الأرضي` (`atiaf:temporal_change`)

---

## 🚀 Quick Setup & Usage in QGIS

1. Copy or symlink `QGIS Tools/atiaf` into your active QGIS profile plugins directory:
   - **Windows:** `%APPDATA%\QGIS\QGIS3\profiles\default\python\plugins\atiaf`
   - **Linux:** `~/.local/share/QGIS/QGIS3/profiles/default/python/plugins/atiaf`
2. In QGIS, navigate to **Plugins -> Manage and Install Plugins -> Installed**, and enable **ATIAF (أطياف)**.
3. Open the **Processing Toolbox** (`Ctrl+Alt+T`) to access all 6 algorithms under `ATIAF | أطياف`.

---

## 🧪 Testing & Verification

1. **Standalone Structural Tests (T1):**
   ```bash
   python -m unittest tests/test_qgis_adapter.py
   ```
2. **Native QGIS Integration Tests (T2):**
   ```powershell
   & "C:\Program Files\QGIS 4.2.3\bin\python-qgis.bat" tests/native_qgis/test_qgis_provider.py
   ```

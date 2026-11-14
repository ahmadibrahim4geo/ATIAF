# Native QGIS Integration Tests | اختبارات بيئة QGIS الحقيقية

Contains integration tests executed directly inside a real QGIS host environment using `python-qgis.bat`.

## Test Suites

- `test_qgis_provider.py`: Validates headless `QgsApplication` initialization, provider registration with `QgsProcessingRegistry`, availability of all 6 algorithms, end-to-end processing of Landsat 8 Level-2 data, GeoTIFF layer validation via `QgsRasterLayer`, and strict enforcement of Decision D-007 (projected metre CRS).

## Execution

```powershell
& "C:\Program Files\QGIS 4.2.3\bin\python-qgis.bat" tests/native_qgis/test_qgis_provider.py
```

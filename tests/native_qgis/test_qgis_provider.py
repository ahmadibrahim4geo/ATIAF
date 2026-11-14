# -*- coding: utf-8 -*-
"""Native QGIS Integration Tests for ATIAF Processing Provider (Phase P7).

Executed inside QGIS 4.2.3 Python environment via python-qgis.bat.
Validates:
1. Headless QgsApplication initialization.
2. ATIAF Processing Provider registration in QgsProcessingRegistry.
3. Availability of all 6 algorithms with correct IDs, parameters, and metadata.
4. Native execution of Tool 01 (Spectral Indices) producing valid GeoTIFF and manifest.
5. Layer validity and CRS verification via QgsRasterLayer.
6. Decision D-007 strict enforcement: rejection of unprojected geographic CRS (EPSG:4326).
"""

from pathlib import Path
import shutil
import sys
import tempfile
import unittest

PROJECT_ROOT = Path(__file__).resolve().parents[2]
QGIS_DIR = PROJECT_ROOT / "qgis"

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))
if str(QGIS_DIR) not in sys.path:
    sys.path.insert(0, str(QGIS_DIR))

import numpy as np
import rasterio

from qgis.core import (
    QgsApplication,
    QgsCoordinateReferenceSystem,
    QgsProcessingContext,
    QgsProcessingException,
    QgsProcessingFeedback,
    QgsRasterLayer,
)

from atyaf.provider import ATIAFProcessingProvider
from atyaf.algorithms.spectral_indices import SpectralIndicesAlgorithm


class TestNativeQGISProvider(unittest.TestCase):
    """Integration test suite executing inside QGIS 4.2.3 runtime."""

    @classmethod
    def setUpClass(cls):
        cls.app = QgsApplication([], False)
        cls.app.initQgis()

        cls.provider = ATIAFProcessingProvider()
        QgsApplication.processingRegistry().addProvider(cls.provider)

    @classmethod
    def tearDownClass(cls):
        if cls.provider:
            QgsApplication.processingRegistry().removeProvider(cls.provider)
        cls.app.exitQgis()

    def setUp(self):
        self.temp_dir = Path(tempfile.mkdtemp(prefix="atyaf_native_qgis_"))
        self.output_dir = Path(tempfile.mkdtemp(prefix="atyaf_native_qgis_out_"))

        # Build real synthetic 16x16 Landsat 8 L2 scene
        self.scene_dir = self.temp_dir / "LC08_L2SP_176039_20230520_20230527_02_T1"
        self.scene_dir.mkdir(parents=True, exist_ok=True)
        prefix = "LC08_L2SP_176039_20230520_20230527_02_T1"

        mtl = f"""GROUP = L1_METADATA_FILE
  GROUP = METADATA_FILE_INFO
    LANDSAT_PRODUCT_ID = "{prefix}"
    PROCESSING_LEVEL = "L2SP"
    COLLECTION_NUMBER = 02
  END_GROUP = METADATA_FILE_INFO
  GROUP = IMAGE_ATTRIBUTES
    SPACECRAFT_ID = "LANDSAT_8"
    SENSOR_ID = "OLI_TIRS"
    DATE_ACQUIRED = "2023-05-20"
    SCENE_CENTER_TIME = "08:15:23.123456Z"
    SUN_ELEVATION = 62.45
    SUN_AZIMUTH = 135.21
    CLOUD_COVER = 1.25
  END_GROUP = IMAGE_ATTRIBUTES
END_GROUP = L1_METADATA_FILE
"""
        (self.scene_dir / f"{prefix}_MTL.txt").write_text(mtl, encoding="utf-8")

        transform = rasterio.transform.from_origin(300000, 3300000, 30, 30)
        profile = {
            "driver": "GTiff",
            "width": 16,
            "height": 16,
            "count": 1,
            "dtype": "uint16",
            "crs": "EPSG:32636",
            "transform": transform,
            "nodata": 0,
        }

        # Red SR = 0.10 -> DN ≈ 10909
        # NIR SR = 0.50 -> DN ≈ 25455
        red_dn = np.full((16, 16), 10909, dtype=np.uint16)
        nir_dn = np.full((16, 16), 25455, dtype=np.uint16)
        qa_dn = np.full((16, 16), 1 << 6, dtype=np.uint16)

        with rasterio.open(self.scene_dir / f"{prefix}_SR_B4.TIF", "w", **profile) as ds:
            ds.write(red_dn, 1)
        with rasterio.open(self.scene_dir / f"{prefix}_SR_B5.TIF", "w", **profile) as ds:
            ds.write(nir_dn, 1)
        with rasterio.open(self.scene_dir / f"{prefix}_QA_PIXEL.TIF", "w", **profile) as ds:
            ds.write(qa_dn, 1)

    def tearDown(self):
        shutil.rmtree(self.temp_dir, ignore_errors=True)
        shutil.rmtree(self.output_dir, ignore_errors=True)

    def test_01_provider_registration(self):
        """Verifies ATIAF provider registered with ID 'atyaf' in Processing Registry."""
        registered_prov = QgsApplication.processingRegistry().providerById("atyaf")
        self.assertIsNotNone(registered_prov, "Provider 'atyaf' not found in processingRegistry")
        self.assertEqual(registered_prov.id(), "atyaf")
        self.assertIn("ATIAF", registered_prov.name())
        self.assertIn("أطياف", registered_prov.name())

    def test_02_all_six_algorithms_registered(self):
        """Verifies that all 6 canonical algorithms are registered with unique IDs."""
        expected_ids = [
            "atyaf:spectral_indices",
            "atyaf:surface_temperature",
            "atyaf:thermal_urban",
            "atyaf:environmental_drought",
            "atyaf:geological_analysis",
            "atyaf:temporal_change",
        ]
        registered_prov = QgsApplication.processingRegistry().providerById("atyaf")
        prov_alg_ids = [a.id() for a in registered_prov.algorithms()]

        for exp_id in expected_ids:
            self.assertIn(exp_id, prov_alg_ids, f"Missing algorithm {exp_id} in provider")
            alg_from_reg = QgsApplication.processingRegistry().algorithmById(exp_id)
            self.assertIsNotNone(alg_from_reg, f"Algorithm {exp_id} not retrievable by ID")

    def test_03_native_spectral_indices_execution(self):
        """Executes atyaf:spectral_indices natively, verifying raster output and manifest."""
        alg = SpectralIndicesAlgorithm()
        alg.initAlgorithm()

        context = QgsProcessingContext()
        feedback = QgsProcessingFeedback()

        params = {
            "INPUT_FOLDER": str(self.scene_dir),
            "APPLY_QA": True,
            "ENABLE_MOSAIC": False,
            "INDICES": [0],  # NDVI
            "OUTPUT_FOLDER": str(self.output_dir),
        }

        result = alg.processAlgorithm(params, context, feedback)
        self.assertIn("OUTPUT_RASTERS", result)
        output_rasters = result["OUTPUT_RASTERS"]
        self.assertTrue(len(output_rasters) > 0, "No output rasters returned by algorithm")

        ndvi_path = Path(output_rasters[0])
        self.assertTrue(ndvi_path.is_file(), f"Output raster does not exist on disk: {ndvi_path}")
        self.assertEqual(ndvi_path.suffix.lower(), ".tif")

        # Verify output with QgsRasterLayer
        layer = QgsRasterLayer(str(ndvi_path), "NDVI_Test_Layer")
        self.assertTrue(layer.isValid(), "Generated raster could not be opened as valid QgsRasterLayer")
        self.assertEqual(layer.width(), 16)
        self.assertEqual(layer.height(), 16)
        self.assertTrue(layer.crs().isValid(), "Layer CRS must be valid")
        self.assertFalse(layer.crs().isGeographic(), "Layer CRS must not be geographic (Decision D-007)")

        # Verify pixel value accuracy (expected (0.50 - 0.10) / (0.50 + 0.10) ≈ 0.6667)
        with rasterio.open(ndvi_path) as ds:
            arr = ds.read(1)
            self.assertAlmostEqual(float(arr[0, 0]), 0.6667, places=3)

        # Verify manifest creation in Results/Reports/Runs/
        manifests = list(self.output_dir.rglob("Processing_Manifest.json"))
        self.assertTrue(len(manifests) > 0, "Processing_Manifest.json was not created")

        # Verify standalone report.html and cumulative Reports/index.html
        html_reports = list(self.output_dir.rglob("report.html"))
        self.assertTrue(len(html_reports) > 0, "report.html was not created")
        index_reports = list(self.output_dir.rglob("index.html"))
        self.assertTrue(len(index_reports) > 0, "Results/Reports/index.html was not created")

    def test_04_enforce_decision_d007_crs_rejection(self):
        """Verifies that passing unprojected geographic CRS (EPSG:4326) raises QgsProcessingException."""
        alg = SpectralIndicesAlgorithm()
        alg.initAlgorithm()

        context = QgsProcessingContext()
        feedback = QgsProcessingFeedback()

        geo_crs = QgsCoordinateReferenceSystem("EPSG:4326")
        self.assertTrue(geo_crs.isValid())
        self.assertTrue(geo_crs.isGeographic())

        params = {
            "INPUT_FOLDER": str(self.scene_dir),
            "APPLY_QA": True,
            "ENABLE_MOSAIC": False,
            "INDICES": [0],
            "CRS": geo_crs,
            "OUTPUT_FOLDER": str(self.output_dir),
        }

        with self.assertRaises(QgsProcessingException) as cm:
            alg.processAlgorithm(params, context, feedback)

        err_msg = str(cm.exception)
        self.assertIn("Decision D-007", err_msg)
        self.assertIn("EPSG:4326", err_msg)

    def test_05_all_six_algorithms_parameter_definitions(self):
        """Audits all 6 algorithms for canonical parameter definitions and ordering."""
        registered_prov = QgsApplication.processingRegistry().providerById("atyaf")
        for alg in registered_prov.algorithms():
            alg_inst = alg.createInstance()
            alg_inst.initAlgorithm()
            defs = alg_inst.parameterDefinitions()
            self.assertTrue(len(defs) >= 4, f"{alg.id()} has fewer than 4 parameters")

            param_names = [p.name() for p in defs]

            # Canonical Rule: OUTPUT_FOLDER must be the last parameter
            self.assertEqual(
                param_names[-1],
                "OUTPUT_FOLDER",
                f"Canonical rule violated: OUTPUT_FOLDER is not the last parameter in {alg.id()}",
            )

            # Decision D-007: CRS parameter must be present
            self.assertIn("CRS", param_names, f"CRS parameter missing in {alg.id()}")

            # Bilingual description check: name, group, and help must have Arabic
            self.assertTrue(any("\u0600" <= c <= "\u06FF" for c in alg.displayName()))
            self.assertTrue(any("\u0600" <= c <= "\u06FF" for c in alg.shortHelpString()))


if __name__ == "__main__":
    unittest.main()

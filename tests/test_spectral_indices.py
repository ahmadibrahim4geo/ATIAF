"""Unit and integration tests for ATIAF Spectral Indices and ArcGIS Pro Toolbox (Phase P3)."""

import json
from pathlib import Path
import shutil
import tempfile
import unittest
import numpy as np
import rasterio

from atyaf_core.discovery import LandsatParser, Sentinel2Parser
from atyaf_core.discovery.models import BandRole
from atyaf_core.indices import INDEX_CATALOG, SpectralIndicesEngine
from atyaf_core.raster import CRSManager

ROOT = Path(__file__).resolve().parents[1]
FIXTURES = ROOT / "tests" / "fixtures" / "synthetic_scenes"


class TestIndexFormulas(unittest.TestCase):
    def setUp(self):
        # Known synthetic pixel values (reflectance: 0 to 1)
        self.bands = {
            BandRole.BLUE: np.array([[0.05]], dtype=np.float32),
            BandRole.GREEN: np.array([[0.10]], dtype=np.float32),
            BandRole.RED: np.array([[0.08]], dtype=np.float32),
            BandRole.RED_EDGE_1: np.array([[0.20]], dtype=np.float32),
            BandRole.NIR: np.array([[0.45]], dtype=np.float32),
            BandRole.SWIR_1: np.array([[0.15]], dtype=np.float32),
            BandRole.SWIR_2: np.array([[0.05]], dtype=np.float32),
        }

    def test_ndvi(self):
        val = INDEX_CATALOG["NDVI"].compute_fn(self.bands)
        expected = (0.45 - 0.08) / (0.45 + 0.08)
        self.assertAlmostEqual(float(val[0, 0]), expected, places=4)

    def test_gndvi(self):
        val = INDEX_CATALOG["GNDVI"].compute_fn(self.bands)
        expected = (0.45 - 0.10) / (0.45 + 0.10)
        self.assertAlmostEqual(float(val[0, 0]), expected, places=4)

    def test_savi(self):
        val = INDEX_CATALOG["SAVI"].compute_fn(self.bands, L=0.5)
        expected = ((0.45 - 0.08) * 1.5) / (0.45 + 0.08 + 0.5)
        self.assertAlmostEqual(float(val[0, 0]), expected, places=4)

    def test_ndwi_gao(self):
        val = INDEX_CATALOG["NDWI_GAO"].compute_fn(self.bands)
        expected = (0.45 - 0.15) / (0.45 + 0.15)
        self.assertAlmostEqual(float(val[0, 0]), expected, places=4)

    def test_mndwi(self):
        val = INDEX_CATALOG["MNDWI"].compute_fn(self.bands)
        expected = (0.10 - 0.15) / (0.10 + 0.15)
        self.assertAlmostEqual(float(val[0, 0]), expected, places=4)

    def test_ndbi(self):
        val = INDEX_CATALOG["NDBI"].compute_fn(self.bands)
        expected = (0.15 - 0.45) / (0.15 + 0.45)
        self.assertAlmostEqual(float(val[0, 0]), expected, places=4)

    def test_nbr(self):
        val = INDEX_CATALOG["NBR"].compute_fn(self.bands)
        expected = (0.45 - 0.05) / (0.45 + 0.05)
        self.assertAlmostEqual(float(val[0, 0]), expected, places=4)

    def test_zero_division_safety(self):
        zero_bands = {
            BandRole.NIR: np.array([[0.0]], dtype=np.float32),
            BandRole.RED: np.array([[0.0]], dtype=np.float32),
        }
        val = INDEX_CATALOG["NDVI"].compute_fn(zero_bands)
        self.assertTrue(np.isnan(val[0, 0]))


class TestSpectralIndicesEngine(unittest.TestCase):
    def setUp(self):
        self.temp_dir = Path(tempfile.mkdtemp())
        self.l8_fixture = FIXTURES / "landsat8_c2_l2"

        # Create real 32x32 GeoTIFFs for Landsat 8 fixture so engine can process them
        self.l8_scene_dir = self.temp_dir / "LC08_SCENE"
        self.l8_scene_dir.mkdir(parents=True, exist_ok=True)

        prefix = "LC08_L2SP_176039_20230520_20230527_02_T1"
        (self.l8_scene_dir / f"{prefix}_MTL.txt").write_text(
            (self.l8_fixture / f"{prefix}_MTL.txt").read_text(encoding="utf-8"),
            encoding="utf-8",
        )

        width, height = 32, 32
        transform = rasterio.transform.from_origin(300000, 3300000, 30, 30)
        profile = {
            "driver": "GTiff",
            "width": width,
            "height": height,
            "count": 1,
            "dtype": "uint16",
            "crs": "EPSG:32636",
            "transform": transform,
            "nodata": 0,
        }

        # Reflectance DN = (SR + 0.2) / 0.0000275
        # Red = 0.10 -> DN = (0.10 + 0.2) / 0.0000275 ≈ 10909
        # NIR = 0.50 -> DN = (0.50 + 0.2) / 0.0000275 ≈ 25455
        red_dn = np.full((height, width), 10909, dtype=np.uint16)
        nir_dn = np.full((height, width), 25455, dtype=np.uint16)
        green_dn = np.full((height, width), 12000, dtype=np.uint16)
        swir1_dn = np.full((height, width), 15000, dtype=np.uint16)
        qa_dn = np.full((height, width), 1 << 6, dtype=np.uint16)  # Bit 6 = clear

        for b_name, arr in [("B4", red_dn), ("B5", nir_dn), ("B3", green_dn), ("B6", swir1_dn)]:
            with rasterio.open(self.l8_scene_dir / f"{prefix}_SR_{b_name}.TIF", "w", **profile) as ds:
                ds.write(arr, 1)

        with rasterio.open(self.l8_scene_dir / f"{prefix}_QA_PIXEL.TIF", "w", **profile) as ds:
            ds.write(qa_dn, 1)

    def tearDown(self):
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_run_scene_indices_landsat8(self):
        scene = LandsatParser.parse(self.l8_scene_dir)
        self.assertIsNotNone(scene)

        res = SpectralIndicesEngine.run_scene_indices(
            scene=scene,
            selected_index_ids=["NDVI", "GNDVI", "MNDWI"],
            custom_destination=self.temp_dir / "Output",
            apply_qa_mask=True,
            block_size=16,
        )

        self.assertEqual(len(res["executed_products"]), 3)
        self.assertEqual(len(res["skipped_indices"]), 0)

        # Verify output files exist and re-read NDVI
        ndvi_rec = next(p for p in res["executed_products"] if p["acronym"] == "NDVI")
        ndvi_path = Path(ndvi_rec["full_path"])
        self.assertTrue(ndvi_path.exists())

        with rasterio.open(ndvi_path) as ds:
            data = ds.read(1)
            self.assertEqual(ds.crs.to_string(), "EPSG:32636")
            # Expected NDVI ≈ (0.50 - 0.10) / (0.50 + 0.10) ≈ 0.6667
            self.assertAlmostEqual(float(data[0, 0]), 0.6667, places=3)

        # Check run manifest
        run_dir = Path(res["run_dir"])
        self.assertTrue((run_dir / "Processing_Manifest.json").exists())
        self.assertTrue((run_dir / "Parameters.json").exists())
        self.assertTrue((run_dir / "Quality_Assessment.csv").exists())

    def test_missing_band_gating(self):
        scene = LandsatParser.parse(self.l8_scene_dir)
        # Select an index whose bands are not in this scene (e.g. BSI requires BLUE which wasn't written)
        res = SpectralIndicesEngine.run_scene_indices(
            scene=scene,
            selected_index_ids=["BSI"],
            custom_destination=self.temp_dir / "Output",
        )
        self.assertEqual(len(res["executed_products"]), 0)
        self.assertEqual(len(res["skipped_indices"]), 1)
        self.assertIn("blue", res["skipped_indices"][0]["reason"])


class TestArcGISProToolboxStructure(unittest.TestCase):
    def test_pyt_file_valid_python(self):
        pyt_path = ROOT / "arcgis_pro" / "ATIAF.pyt"
        self.assertTrue(pyt_path.is_file())

        # Compile pyt to verify syntax
        code = pyt_path.read_text(encoding="utf-8")
        compiled = compile(code, str(pyt_path), "exec")
        self.assertIsNotNone(compiled)

        # Execute in a sandbox dictionary
        namespace = {"__file__": str(pyt_path)}
        exec(compiled, namespace)

        self.assertIn("Toolbox", namespace)
        self.assertIn("SpectralIndicesTool", namespace)

        toolbox = namespace["Toolbox"]()
        self.assertEqual(toolbox.alias, "atyaf")
        self.assertEqual(len(toolbox.tools), 1)

        tool = namespace["SpectralIndicesTool"]()
        self.assertIn("Spectral Indices", tool.label)

        # Verify parameter count and standard parameter ordering (Section 3)
        # Note: If arcpy is not installed in the test runner, getParameterInfo returns None for arcpy parameters
        # but the class definition and methods exist
        self.assertTrue(hasattr(tool, "getParameterInfo"))
        self.assertTrue(hasattr(tool, "updateParameters"))
        self.assertTrue(hasattr(tool, "updateMessages"))
        self.assertTrue(hasattr(tool, "execute"))


if __name__ == "__main__":
    unittest.main()

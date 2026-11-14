"""Unit and integration tests for ATIAF Surface Temperature and Geological Analysis (Phase P4)."""

import json
from pathlib import Path
import shutil
import tempfile
import unittest
import numpy as np
import rasterio

from atyaf_core.discovery import AsterParser, LandsatParser, Sentinel2Parser
from atyaf_core.discovery.models import BandRole
from atyaf_core.geology import GEOLOGICAL_CATALOG, GeologicalAnalysisEngine
from atyaf_core.temperature import EmissivityEngine, SurfaceTemperatureEngine

ROOT = Path(__file__).resolve().parents[1]
FIXTURES = ROOT / "tests" / "fixtures" / "synthetic_scenes"


class TestEmissivityFormulas(unittest.TestCase):
    """Verifies Sobrino et al. (2004) NDVI threshold emissivity calculation."""

    def test_water_emissivity(self):
        ndvi = np.array([[-0.2, -0.05]], dtype=np.float32)
        emissivity = EmissivityEngine.calc_land_surface_emissivity(ndvi)
        np.testing.assert_allclose(emissivity, 0.992, atol=1e-4)

    def test_bare_soil_emissivity(self):
        ndvi = np.array([[0.05, 0.15, 0.19]], dtype=np.float32)
        emissivity = EmissivityEngine.calc_land_surface_emissivity(ndvi)
        np.testing.assert_allclose(emissivity, 0.970, atol=1e-4)

    def test_dense_vegetation_emissivity(self):
        ndvi = np.array([[0.55, 0.75, 0.90]], dtype=np.float32)
        emissivity = EmissivityEngine.calc_land_surface_emissivity(ndvi)
        np.testing.assert_allclose(emissivity, 0.985, atol=1e-4)

    def test_mixed_pixel_emissivity(self):
        # When NDVI = 0.35:
        # Pv = ((0.35 - 0.2) / 0.3)^2 = 0.5^2 = 0.25
        # Emissivity = 0.985 * 0.25 + 0.970 * 0.75 + 0.005 = 0.97875
        ndvi = np.array([[0.35]], dtype=np.float32)
        emissivity = EmissivityEngine.calc_land_surface_emissivity(ndvi)
        self.assertAlmostEqual(float(emissivity[0, 0]), 0.97875, places=4)

    def test_nan_ndvi_handling(self):
        ndvi = np.array([[np.nan, 0.4]], dtype=np.float32)
        emissivity = EmissivityEngine.calc_land_surface_emissivity(ndvi)
        self.assertTrue(np.isnan(emissivity[0, 0]))
        self.assertFalse(np.isnan(emissivity[0, 1]))


class TestSurfaceTemperatureEngine(unittest.TestCase):
    """Tests LST calculation, thermal gating, unit conversion, and manifest output."""

    def setUp(self):
        self.temp_dir = Path(tempfile.mkdtemp())
        self.custom_dest = self.temp_dir / "custom_output"

        # Create a valid synthetic Landsat 8 scene with real GeoTIFF rasters
        self.l8_scene_dir = self.temp_dir / "LC08_SCENE"
        self.l8_scene_dir.mkdir(parents=True, exist_ok=True)

        prefix = "LC08_L2SP_176039_20230520_20230527_02_T1"
        mtl_src = FIXTURES / "landsat8_c2_l2" / f"{prefix}_MTL.txt"
        (self.l8_scene_dir / f"{prefix}_MTL.txt").write_text(
            mtl_src.read_text(encoding="utf-8"), encoding="utf-8"
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

        # Reflectance and Temperature DN values
        # Red: SR=0.10 -> DN = (0.10 + 0.2) / 0.0000275 ≈ 10909
        # NIR: SR=0.50 -> DN = (0.50 + 0.2) / 0.0000275 ≈ 25455
        # ST: ST_K ≈ 299.39 K (~26.24 °C) -> DN = (299.39288 - 149.0) / 0.00341802 ≈ 44000
        red_dn = np.full((height, width), 10909, dtype=np.uint16)
        nir_dn = np.full((height, width), 25455, dtype=np.uint16)
        st_dn = np.full((height, width), 44000, dtype=np.uint16)
        qa_dn = np.full((height, width), 1 << 6, dtype=np.uint16)  # Bit 6 = clear

        with rasterio.open(self.l8_scene_dir / f"{prefix}_SR_B4.TIF", "w", **profile) as ds:
            ds.write(red_dn, 1)
        with rasterio.open(self.l8_scene_dir / f"{prefix}_SR_B5.TIF", "w", **profile) as ds:
            ds.write(nir_dn, 1)
        with rasterio.open(self.l8_scene_dir / f"{prefix}_ST_B10.TIF", "w", **profile) as ds:
            ds.write(st_dn, 1)
        with rasterio.open(self.l8_scene_dir / f"{prefix}_QA_PIXEL.TIF", "w", **profile) as ds:
            ds.write(qa_dn, 1)

    def tearDown(self):
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_sentinel2_thermal_rejection(self):
        s2_path = FIXTURES / "S2A_MSIL2A_20230615T082611_N0509_R121_T36RUU_20230615T121345.SAFE"
        scene = Sentinel2Parser.parse(s2_path)
        self.assertIsNotNone(scene)
        self.assertFalse(scene.has_thermal())

        with self.assertRaises(ValueError) as ctx:
            SurfaceTemperatureEngine.run_surface_temperature(scene)
        self.assertIn("lacks thermal infrared", str(ctx.exception))

    def test_landsat8_c2_l2_st_celsius(self):
        scene = LandsatParser.parse(self.l8_scene_dir)
        self.assertIsNotNone(scene)
        self.assertTrue(scene.has_thermal())

        res = SurfaceTemperatureEngine.run_surface_temperature(
            scene=scene,
            method="Official_L2_ST",
            output_unit="Celsius",
            custom_destination=self.custom_dest,
            apply_qa_mask=True,
            block_size=16,
        )

        self.assertEqual(len(res["executed_products"]), 1)
        prod = res["executed_products"][0]
        self.assertEqual(prod["product_name"], "LST_CELSIUS")
        out_file = Path(prod["full_path"])
        self.assertTrue(out_file.exists())

        # Inspect values: 44000 * 0.00341802 + 149 - 273.15 ~= 26.24 C
        with rasterio.open(out_file) as ds:
            arr = ds.read(1)
            valid = arr[~np.isnan(arr)]
            self.assertGreater(len(valid), 0)
            self.assertTrue(np.all((valid >= 20.0) & (valid <= 35.0)))

        # Verify manifests
        run_dir = Path(res["run_dir"])
        self.assertTrue((run_dir / "Processing_Manifest.json").exists())
        self.assertTrue((run_dir / "Parameters.json").exists())
        with open(run_dir / "Processing_Manifest.json", "r", encoding="utf-8") as f:
            manifest = json.load(f)
            self.assertEqual(manifest["tool_name"], "02_Surface_Temperature")
            self.assertEqual(len(manifest["output_products"]), 1)
            self.assertEqual(manifest["output_products"][0]["product_name"], "LST_CELSIUS")

    def test_landsat8_c2_l2_st_kelvin(self):
        scene = LandsatParser.parse(self.l8_scene_dir)
        res_c = SurfaceTemperatureEngine.run_surface_temperature(
            scene=scene,
            method="Official_L2_ST",
            output_unit="Celsius",
            custom_destination=self.custom_dest,
            block_size=16,
        )
        res_k = SurfaceTemperatureEngine.run_surface_temperature(
            scene=scene,
            method="Official_L2_ST",
            output_unit="Kelvin",
            custom_destination=self.custom_dest,
            block_size=16,
        )

        c_file = Path(res_c["executed_products"][0]["full_path"])
        k_file = Path(res_k["executed_products"][0]["full_path"])

        with rasterio.open(c_file) as ds_c, rasterio.open(k_file) as ds_k:
            arr_c = ds_c.read(1)
            arr_k = ds_k.read(1)
            valid_mask = ~np.isnan(arr_c) & ~np.isnan(arr_k)
            diff = arr_k[valid_mask] - arr_c[valid_mask]
            np.testing.assert_allclose(diff, 273.15, atol=1e-3)

    def test_emissivity_from_ndvi(self):
        scene = LandsatParser.parse(self.l8_scene_dir)
        res = SurfaceTemperatureEngine.run_surface_temperature(
            scene=scene,
            method="Emissivity_NDVI",
            custom_destination=self.custom_dest,
            apply_qa_mask=True,
            block_size=16,
        )
        self.assertEqual(len(res["executed_products"]), 1)
        prod = res["executed_products"][0]
        self.assertEqual(prod["product_name"], "EMISSIVITY_NDVI")
        out_file = Path(prod["full_path"])
        with rasterio.open(out_file) as ds:
            arr = ds.read(1)
            valid = arr[~np.isnan(arr)]
            self.assertGreater(len(valid), 0)
            self.assertTrue(np.all((valid >= 0.90) & (valid <= 1.0)))


class TestGeologicalAnalysisEngine(unittest.TestCase):
    """Tests geological alteration ratios, ASTER post-2008 SWIR gating, and execution."""

    def setUp(self):
        self.temp_dir = Path(tempfile.mkdtemp())
        self.custom_dest = self.temp_dir / "custom_geology"

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

        # 1. Landsat 8 scene with full optical suite
        self.l8_dir = self.temp_dir / "L8_GEO"
        self.l8_dir.mkdir(parents=True, exist_ok=True)
        prefix = "LC08_L2SP_176039_20230520_20230527_02_T1"
        (self.l8_dir / f"{prefix}_MTL.txt").write_text(
            (FIXTURES / "landsat8_c2_l2" / f"{prefix}_MTL.txt").read_text(encoding="utf-8"),
            encoding="utf-8",
        )
        # Scaled values: Blue=0.05, Green=0.10, Red=0.20, NIR=0.30, SWIR1=0.40, SWIR2=0.20
        # DN = (SR + 0.2) / 0.0000275
        bands = [
            ("SR_B2", int((0.05 + 0.2) / 0.0000275)),
            ("SR_B3", int((0.10 + 0.2) / 0.0000275)),
            ("SR_B4", int((0.20 + 0.2) / 0.0000275)),
            ("SR_B5", int((0.30 + 0.2) / 0.0000275)),
            ("SR_B6", int((0.40 + 0.2) / 0.0000275)),
            ("SR_B7", int((0.20 + 0.2) / 0.0000275)),
        ]
        for b_name, dn_val in bands:
            with rasterio.open(self.l8_dir / f"{prefix}_{b_name}.TIF", "w", **profile) as ds:
                ds.write(np.full((height, width), dn_val, dtype=np.uint16), 1)

        with rasterio.open(self.l8_dir / f"{prefix}_QA_PIXEL.TIF", "w", **profile) as ds:
            ds.write(np.full((height, width), 1 << 6, dtype=np.uint16), 1)

        # 2. ASTER pre-2008 and post-2008 scenes
        self.pre_aster_dir = self.temp_dir / "AST_PRE"
        self.post_aster_dir = self.temp_dir / "AST_POST"
        self.pre_aster_dir.mkdir(parents=True, exist_ok=True)
        self.post_aster_dir.mkdir(parents=True, exist_ok=True)

        (self.pre_aster_dir / "AST_07.met").write_text(
            (FIXTURES / "AST_07_00305202005123456" / "AST_07.met").read_text(encoding="utf-8"),
            encoding="utf-8",
        )
        (self.post_aster_dir / "AST_07.met").write_text(
            (FIXTURES / "AST_07_00305202012123456" / "AST_07.met").read_text(encoding="utf-8"),
            encoding="utf-8",
        )

        for ast_dir in [self.pre_aster_dir, self.post_aster_dir]:
            for b in ["B01", "B02", "B3N", "B04", "B05"]:
                with rasterio.open(ast_dir / f"{b}.tif", "w", **profile) as ds:
                    ds.write(np.full((height, width), 200, dtype=np.uint16), 1)

    def tearDown(self):
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_geological_formulas(self):
        bands = {
            BandRole.BLUE: np.array([[0.05]], dtype=np.float32),
            BandRole.GREEN: np.array([[0.10]], dtype=np.float32),
            BandRole.RED: np.array([[0.20]], dtype=np.float32),
            BandRole.NIR: np.array([[0.30]], dtype=np.float32),
            BandRole.SWIR_1: np.array([[0.40]], dtype=np.float32),
            BandRole.SWIR_2: np.array([[0.20]], dtype=np.float32),
        }

        # Iron Oxide = Red / Blue = 0.20 / 0.05 = 4.0
        val_io = GEOLOGICAL_CATALOG["IRON_OXIDE"].compute_fn(bands)
        self.assertAlmostEqual(float(val_io[0, 0]), 4.0, places=4)

        # Ferric Iron = Red / Green = 0.20 / 0.10 = 2.0
        val_fe3 = GEOLOGICAL_CATALOG["FERRIC_IRON"].compute_fn(bands)
        self.assertAlmostEqual(float(val_fe3[0, 0]), 2.0, places=4)

        # Ferrous Iron = SWIR1 / NIR = 0.40 / 0.30 = 1.3333
        val_fe2 = GEOLOGICAL_CATALOG["FERROUS_IRON"].compute_fn(bands)
        self.assertAlmostEqual(float(val_fe2[0, 0]), 4.0 / 3.0, places=4)

        # Clay Alteration = SWIR1 / SWIR2 = 0.40 / 0.20 = 2.0
        val_clay = GEOLOGICAL_CATALOG["CLAY_ALTERATION"].compute_fn(bands)
        self.assertAlmostEqual(float(val_clay[0, 0]), 2.0, places=4)

        # Gossan = SWIR1 / Red = 0.40 / 0.20 = 2.0
        val_gossan = GEOLOGICAL_CATALOG["GOSSAN"].compute_fn(bands)
        self.assertAlmostEqual(float(val_gossan[0, 0]), 2.0, places=4)

    def test_aster_post_2008_swir_gating(self):
        pre_scene = AsterParser.parse(self.pre_aster_dir)
        post_scene = AsterParser.parse(self.post_aster_dir)

        self.assertIsNotNone(pre_scene)
        self.assertIsNotNone(post_scene)

        self.assertNotIn("ASTER_SWIR_INVALID_POST_2008", pre_scene.metadata.restrictions)
        self.assertIn("ASTER_SWIR_INVALID_POST_2008", post_scene.metadata.restrictions)

        # Post-2008 scene must not support SWIR indices
        post_supported = GeologicalAnalysisEngine.get_supported_indices_for_scene(post_scene)
        for s in post_supported:
            self.assertFalse(s.requires_swir, f"Post-2008 ASTER should not support SWIR index: {s.id}")

        # Attempt to run SWIR index on post-2008 scene -> must be skipped
        res = GeologicalAnalysisEngine.run_geological_analysis(
            scene=post_scene,
            selected_index_ids=["CLAY_ALTERATION", "IRON_OXIDE"],
            custom_destination=self.custom_dest,
        )
        skipped_ids = [sk["id"] for sk in res["skipped_indices"]]
        self.assertIn("CLAY_ALTERATION", skipped_ids)

    def test_landsat8_geological_execution(self):
        scene = LandsatParser.parse(self.l8_dir)
        res = GeologicalAnalysisEngine.run_geological_analysis(
            scene=scene,
            selected_index_ids=["IRON_OXIDE", "FERRIC_IRON", "CLAY_ALTERATION"],
            custom_destination=self.custom_dest,
            apply_qa_mask=True,
            block_size=16,
        )

        self.assertEqual(len(res["executed_products"]), 3)
        for p in res["executed_products"]:
            out_file = Path(p["full_path"])
            self.assertTrue(out_file.exists())
            with rasterio.open(out_file) as ds:
                arr = ds.read(1)
                valid = arr[~np.isnan(arr)]
                self.assertGreater(len(valid), 0)

        # Verify run manifest contains scientific disclaimer
        run_dir = Path(res["run_dir"])
        with open(run_dir / "Processing_Manifest.json", "r", encoding="utf-8") as f:
            manifest = json.load(f)
            self.assertIn("scientific_disclaimer", manifest)
            self.assertIn("probabilistic", manifest["scientific_disclaimer"])


class TestArcGISProToolboxPhase4(unittest.TestCase):
    """Verifies that arcgis_pro/ATIAF.pyt exposes Tools 01, 02, and 05."""

    def test_toolbox_tools_list(self):
        pyt_path = ROOT / "arcgis_pro" / "ATIAF.pyt"
        self.assertTrue(pyt_path.exists())

        code = pyt_path.read_text(encoding="utf-8")
        compiled = compile(code, str(pyt_path), "exec")
        namespace = {"__file__": str(pyt_path)}
        exec(compiled, namespace)

        self.assertIn("Toolbox", namespace)
        self.assertIn("SpectralIndicesTool", namespace)
        self.assertIn("SurfaceTemperatureTool", namespace)
        self.assertIn("GeologicalAnalysisTool", namespace)

        tb = namespace["Toolbox"]()
        tool_names = [t.__name__ for t in tb.tools]
        self.assertIn("SpectralIndicesTool", tool_names)
        self.assertIn("SurfaceTemperatureTool", tool_names)
        self.assertIn("GeologicalAnalysisTool", tool_names)

        st_tool = namespace["SurfaceTemperatureTool"]()
        self.assertIn("Surface Temperature", st_tool.label)
        self.assertTrue(st_tool.isLicensed())
        self.assertTrue(hasattr(st_tool, "getParameterInfo"))
        self.assertTrue(hasattr(st_tool, "updateParameters"))
        self.assertTrue(hasattr(st_tool, "updateMessages"))
        self.assertTrue(hasattr(st_tool, "execute"))

        geo_tool = namespace["GeologicalAnalysisTool"]()
        self.assertIn("Geological Analysis", geo_tool.label)
        self.assertTrue(geo_tool.isLicensed())
        self.assertTrue(hasattr(geo_tool, "getParameterInfo"))
        self.assertTrue(hasattr(geo_tool, "updateParameters"))
        self.assertTrue(hasattr(geo_tool, "updateMessages"))
        self.assertTrue(hasattr(geo_tool, "execute"))


if __name__ == "__main__":
    unittest.main()

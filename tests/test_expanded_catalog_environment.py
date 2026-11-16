"""Unit and integration tests for ATIAF Expanded Catalog, Thermal Urban, and Environmental Drought (Phase P6)."""

from pathlib import Path
import unittest
import numpy as np

from atiaf_core.discovery.models import BandRole
from atiaf_core.environment import EnvironmentalDroughtEngine
from atiaf_core.indices import INDEX_CATALOG
from atiaf_core.urban import ThermalUrbanEngine

ROOT = Path(__file__).resolve().parents[1]


class TestExpandedCatalog(unittest.TestCase):
    """Verifies formula calculations for newly expanded optical indices."""

    def setUp(self):
        # Known synthetic pixel values
        self.bands = {
            BandRole.BLUE: np.array([[0.05]], dtype=np.float32),
            BandRole.GREEN: np.array([[0.10]], dtype=np.float32),
            BandRole.RED: np.array([[0.08]], dtype=np.float32),
            BandRole.NIR: np.array([[0.45]], dtype=np.float32),
            BandRole.SWIR_1: np.array([[0.15]], dtype=np.float32),
            BandRole.SWIR_2: np.array([[0.05]], dtype=np.float32),
        }

    def test_ndmi(self):
        # (NIR - SWIR1) / (NIR + SWIR1) = (0.45 - 0.15) / (0.45 + 0.15) = 0.30 / 0.60 = 0.50
        val = INDEX_CATALOG["NDMI"].compute_fn(self.bands)
        self.assertAlmostEqual(float(val[0, 0]), 0.50, places=4)

    def test_msavi(self):
        # (2 * 0.45 + 1 - sqrt((2 * 0.45 + 1)^2 - 8 * (0.45 - 0.08))) / 2
        # (1.9 - sqrt(1.9^2 - 8 * 0.37)) / 2 = (1.9 - sqrt(3.61 - 2.96)) / 2
        # (1.9 - sqrt(0.65)) / 2 = (1.9 - 0.80622577) / 2 = 1.093774 / 2 = 0.546887
        val = INDEX_CATALOG["MSAVI"].compute_fn(self.bands)
        expected = (1.9 - np.sqrt(3.61 - 8.0 * 0.37)) / 2.0
        self.assertAlmostEqual(float(val[0, 0]), expected, places=4)

    def test_osavi(self):
        # (0.45 - 0.08) / (0.45 + 0.08 + 0.16) = 0.37 / 0.69 = 0.53623
        val = INDEX_CATALOG["OSAVI"].compute_fn(self.bands)
        expected = 0.37 / 0.69
        self.assertAlmostEqual(float(val[0, 0]), expected, places=4)

    def test_vari(self):
        # (Green - Red) / (Green + Red - Blue) = (0.10 - 0.08) / (0.10 + 0.08 - 0.05) = 0.02 / 0.13 = 0.1538
        val = INDEX_CATALOG["VARI"].compute_fn(self.bands)
        expected = 0.02 / 0.13
        self.assertAlmostEqual(float(val[0, 0]), expected, places=4)

    def test_gli(self):
        # (2 * Green - Red - Blue) / (2 * Green + Red + Blue)
        # (0.20 - 0.08 - 0.05) / (0.20 + 0.08 + 0.05) = 0.07 / 0.33 = 0.2121
        val = INDEX_CATALOG["GLI"].compute_fn(self.bands)
        expected = 0.07 / 0.33
        self.assertAlmostEqual(float(val[0, 0]), expected, places=4)

    def test_tasseled_cap_transformations(self):
        # Baig et al. (2014) Landsat 8/9
        tcb = INDEX_CATALOG["TCB"].compute_fn(self.bands)
        tcg = INDEX_CATALOG["TCG"].compute_fn(self.bands)
        tcw = INDEX_CATALOG["TCW"].compute_fn(self.bands)

        exp_tcb = (
            0.3029 * 0.05 + 0.2786 * 0.10 + 0.4733 * 0.08
            + 0.5599 * 0.45 + 0.5080 * 0.15 + 0.1872 * 0.05
        )
        self.assertAlmostEqual(float(tcb[0, 0]), exp_tcb, places=4)

        exp_tcg = (
            -0.2941 * 0.05 - 0.2430 * 0.10 - 0.5424 * 0.08
            + 0.7276 * 0.45 + 0.0713 * 0.15 - 0.1608 * 0.05
        )
        self.assertAlmostEqual(float(tcg[0, 0]), exp_tcg, places=4)

        exp_tcw = (
            0.1511 * 0.05 + 0.1973 * 0.10 + 0.3283 * 0.08
            + 0.3407 * 0.45 - 0.7117 * 0.15 - 0.4572 * 0.05
        )
        self.assertAlmostEqual(float(tcw[0, 0]), exp_tcw, places=4)


class TestThermalUrbanFormulas(unittest.TestCase):
    """Verifies Urban Thermal Field Variance Index (UTFVI) and Hotspot functions."""

    def test_utfvi_math_and_classes(self):
        # LST array in Kelvin: mean is 300.0 K
        # Values: 295.0, 300.0, 301.8, 303.6, 305.4, 309.0
        # UTFVI = (LST - 300) / 300:
        # 295 -> -5/300 = -0.0167 -> Class 1 (None)
        # 300 -> 0.0000 -> Class 2 (Weak: 0 to 0.005)
        # 301.8 -> 1.8/300 = 0.006 -> Class 3 (Middle: 0.005 to 0.010)
        # 303.6 -> 3.6/300 = 0.012 -> Class 4 (Strong: 0.010 to 0.015)
        # 305.4 -> 5.4/300 = 0.018 -> Class 5 (Stronger: 0.015 to 0.020)
        # 309.0 -> 9.0/300 = 0.030 -> Class 6 (Strongest: >= 0.020)
        # We construct an array symmetric around 300 so mean is exactly 300
        # Let's test with a given mean
        lst_arr = np.array([[294.0, 306.0]], dtype=np.float32)  # mean = 300.0
        utfvi, classes = ThermalUrbanEngine.calc_utfvi(lst_arr)
        # (294 - 300)/300 = -0.02 -> Class 1
        # (306 - 300)/300 = +0.02 -> Class 6
        self.assertAlmostEqual(float(utfvi[0, 0]), -0.02, places=4)
        self.assertAlmostEqual(float(utfvi[0, 1]), +0.02, places=4)
        self.assertEqual(classes[0, 0], 1)
        self.assertEqual(classes[0, 1], 6)

    def test_thermal_hotspots(self):
        lst = np.array([[20.0, 21.0, 20.0, 20.5, 35.0]], dtype=np.float32)
        hotspots = ThermalUrbanEngine.calc_thermal_hotspots(lst, z_threshold=1.5)
        self.assertEqual(hotspots[0, 4], 1)
        self.assertEqual(hotspots[0, 0], 0)


class TestEnvironmentalDroughtFormulas(unittest.TestCase):
    """Verifies Liang (2001) Broadband Albedo and TVDI formulas."""

    def test_liang_broadband_albedo(self):
        bands = {
            "blue": np.array([[0.05]], dtype=np.float32),
            "red": np.array([[0.08]], dtype=np.float32),
            "nir": np.array([[0.45]], dtype=np.float32),
            "swir1": np.array([[0.15]], dtype=np.float32),
            "swir2": np.array([[0.05]], dtype=np.float32),
        }
        albedo = EnvironmentalDroughtEngine.calc_broadband_albedo(bands)
        expected = (
            0.356 * 0.05 + 0.130 * 0.08 + 0.373 * 0.45
            + 0.085 * 0.15 + 0.072 * 0.05 - 0.0018
        )
        self.assertAlmostEqual(float(albedo[0, 0]), expected, places=4)
        self.assertTrue(0.0 <= float(albedo[0, 0]) <= 1.0)

    def test_tvdi_normalization(self):
        lst = np.array([[20.0, 30.0, 40.0]], dtype=np.float32)
        ndvi = np.array([[0.5, 0.5, 0.5]], dtype=np.float32)
        tvdi = EnvironmentalDroughtEngine.calc_tvdi(lst, ndvi)
        self.assertAlmostEqual(float(tvdi[0, 0]), 0.0, places=4)
        self.assertAlmostEqual(float(tvdi[0, 1]), 0.5, places=4)
        self.assertAlmostEqual(float(tvdi[0, 2]), 1.0, places=4)


class TestArcGISProAllSixTools(unittest.TestCase):
    """Verifies that arcgis_pro/ATIAF.pyt exposes all 6 canonical tools."""

    def test_toolbox_all_six_tools(self):
        pyt_path = (ROOT / "ArcGIS Pro Tools" / "ATIAF.pyt") if (ROOT / "ArcGIS Pro Tools" / "ATIAF.pyt").exists() else (ROOT / "arcgis_pro" / "ATIAF.pyt")
        self.assertTrue(pyt_path.exists())

        code = pyt_path.read_text(encoding="utf-8")
        compiled = compile(code, str(pyt_path), "exec")
        namespace = {"__file__": str(pyt_path)}
        exec(compiled, namespace)

        self.assertIn("Toolbox", namespace)
        tb = namespace["Toolbox"]()
        tool_names = [t.__name__ for t in tb.tools]

        self.assertEqual(len(tool_names), 7)
        self.assertIn("GeologicalColorCompositesTool", tool_names)
        self.assertIn("SpectralIndicesTool", tool_names)
        self.assertIn("SurfaceTemperatureTool", tool_names)
        self.assertIn("ThermalUrbanTool", tool_names)
        self.assertIn("EnvironmentalDroughtTool", tool_names)
        self.assertIn("GeologicalAnalysisTool", tool_names)
        self.assertIn("TemporalChangeTool", tool_names)

        # Check Tools 03 & 04 instances
        u_tool = namespace["ThermalUrbanTool"]()
        self.assertIn("Thermal & Urban", u_tool.label)
        self.assertTrue(u_tool.isLicensed())

        e_tool = namespace["EnvironmentalDroughtTool"]()
        self.assertIn("Environmental & Drought", e_tool.label)
        self.assertTrue(e_tool.isLicensed())


if __name__ == "__main__":
    unittest.main()

"""Comprehensive unit and integration tests for ATIAF Product Recognition & Scene Discovery (Phase P1)."""

from datetime import datetime
from pathlib import Path
import unittest

from atyaf_core.discovery import (
    BandRole,
    ProductLevel,
    SensorFamily,
    SceneScanner,
    LandsatParser,
    Sentinel2Parser,
    AsterParser,
    ManualBandMapper,
)

ROOT = Path(__file__).resolve().parents[1]
FIXTURES = ROOT / "tests" / "fixtures" / "synthetic_scenes"


class TestLandsatRecognition(unittest.TestCase):
    def setUp(self):
        self.l8_folder = FIXTURES / "landsat8_c2_l2"
        self.l7_folder = FIXTURES / "landsat7_c2_l2"

    def test_landsat8_c2_l2_discovery(self):
        self.assertTrue(LandsatParser.can_parse(self.l8_folder))
        scene = LandsatParser.parse(self.l8_folder)
        self.assertIsNotNone(scene)

        # Identity
        self.assertEqual(scene.metadata.sensor_family, SensorFamily.LANDSAT)
        self.assertEqual(scene.metadata.platform, "Landsat 8")
        self.assertEqual(scene.metadata.instrument, "OLI_TIRS")
        self.assertEqual(scene.metadata.product_level, ProductLevel.L2_SR)
        self.assertEqual(scene.metadata.scene_id, "LC08_L2SP_176039_20230520_20230527_02_T1")

        # Acquisition & Angles
        self.assertEqual(scene.metadata.acquisition_date, datetime(2023, 5, 20, 8, 15, 23))
        self.assertAlmostEqual(scene.metadata.sun_elevation_deg, 62.45)
        self.assertAlmostEqual(scene.metadata.sun_azimuth_deg, 135.21)
        self.assertAlmostEqual(scene.metadata.cloud_cover_percent, 1.25)

        # Reflectance Bands
        for role in [BandRole.BLUE, BandRole.GREEN, BandRole.RED, BandRole.NIR, BandRole.SWIR_1, BandRole.SWIR_2]:
            self.assertTrue(scene.has_role(role), f"Missing expected role: {role}")
            b = scene.get_band(role)
            self.assertEqual(b.scale_factor, 0.0000275)
            self.assertEqual(b.offset, -0.2)
            self.assertEqual(b.unit, "reflectance")
            self.assertFalse(b.is_thermal)

        # Thermal Band
        self.assertTrue(scene.has_role(BandRole.THERMAL_1))
        therm = scene.get_band(BandRole.THERMAL_1)
        self.assertTrue(therm.is_thermal)
        self.assertEqual(therm.scale_factor, 0.00341802)
        self.assertEqual(therm.offset, 149.0)
        self.assertEqual(therm.unit, "Kelvin")
        self.assertTrue(scene.has_thermal())

        # Quality masks
        self.assertIn("QA_PIXEL", scene.quality_masks)
        self.assertIn("QA_RADSAT", scene.quality_masks)
        self.assertIn("cloud_bit", scene.quality_masks["QA_PIXEL"].flags_info)

    def test_landsat7_slc_off_warning(self):
        scene = LandsatParser.parse(self.l7_folder)
        self.assertIsNotNone(scene)
        self.assertEqual(scene.metadata.platform, "Landsat 7")
        self.assertEqual(scene.metadata.instrument, "ETM")
        self.assertTrue(any("SLC-off" in w for w in scene.metadata.warnings))
        self.assertTrue(scene.has_role(BandRole.RED))
        self.assertTrue(scene.has_role(BandRole.NIR))
        self.assertTrue(scene.has_role(BandRole.THERMAL_1))


class TestSentinel2Recognition(unittest.TestCase):
    def setUp(self):
        self.l2a_folder = FIXTURES / "S2A_MSIL2A_20230615T082611_N0509_R121_T36RUU_20230615T121345.SAFE"
        self.l1c_folder = FIXTURES / "S2B_MSIL1C_20230710T082609_N0509_R121_T36RUU_20230710T121345.SAFE"

    def test_sentinel2_l2a_safe(self):
        self.assertTrue(Sentinel2Parser.can_parse(self.l2a_folder))
        scene = Sentinel2Parser.parse(self.l2a_folder)
        self.assertIsNotNone(scene)

        # Identity
        self.assertEqual(scene.metadata.sensor_family, SensorFamily.SENTINEL_2)
        self.assertEqual(scene.metadata.platform, "Sentinel-2A")
        self.assertEqual(scene.metadata.instrument, "MSI")
        self.assertEqual(scene.metadata.product_level, ProductLevel.L2A_BOA)

        # Sun angle and cloud cover
        self.assertAlmostEqual(scene.metadata.sun_elevation_deg, 65.5)  # 90 - 24.5
        self.assertAlmostEqual(scene.metadata.sun_azimuth_deg, 128.2)
        self.assertAlmostEqual(scene.metadata.cloud_cover_percent, 2.41)

        # 10m bands
        for role in [BandRole.BLUE, BandRole.GREEN, BandRole.RED, BandRole.NIR]:
            self.assertTrue(scene.has_role(role))
            b = scene.get_band(role)
            self.assertEqual(b.resolution_m, 10.0)
            self.assertEqual(b.scale_factor, 0.0001)

        # 20m bands
        for role in [BandRole.RED_EDGE_1, BandRole.RED_EDGE_2, BandRole.RED_EDGE_3, BandRole.NARROW_NIR, BandRole.SWIR_1, BandRole.SWIR_2]:
            self.assertTrue(scene.has_role(role))
            b = scene.get_band(role)
            self.assertEqual(b.resolution_m, 20.0)

        # SCL Mask
        self.assertIn("SCL", scene.quality_masks)

        # Strict scientific rule: NO THERMAL
        self.assertFalse(scene.has_thermal())
        self.assertIn("NO_THERMAL", scene.metadata.restrictions)
        self.assertTrue(any("NO thermal bands" in w for w in scene.metadata.warnings))

    def test_sentinel2_l1c_toa_warning(self):
        scene = Sentinel2Parser.parse(self.l1c_folder)
        self.assertIsNotNone(scene)
        self.assertEqual(scene.metadata.product_level, ProductLevel.L1C_TOA)
        self.assertIn("TOA_ONLY_WARNING", scene.metadata.restrictions)
        self.assertTrue(any("Level-1C" in w for w in scene.metadata.warnings))


class TestAsterRecognition(unittest.TestCase):
    def setUp(self):
        self.ast_pre = FIXTURES / "AST_07_00305202005123456"
        self.ast_post = FIXTURES / "AST_07_00305202012123456"

    def test_aster_pre_2008_valid_swir(self):
        scene = AsterParser.parse(self.ast_pre)
        self.assertIsNotNone(scene)
        self.assertEqual(scene.metadata.sensor_family, SensorFamily.ASTER)
        self.assertEqual(scene.metadata.acquisition_date, datetime(2005, 5, 20))
        self.assertTrue(scene.has_role(BandRole.GREEN))
        self.assertTrue(scene.has_role(BandRole.RED))
        self.assertTrue(scene.has_role(BandRole.NIR))
        # SWIR is valid pre-2008
        self.assertTrue(scene.has_role(BandRole.SWIR_1))
        self.assertTrue(scene.has_role(BandRole.SWIR_2))
        self.assertNotIn("ASTER_SWIR_INVALID_POST_2008", scene.metadata.restrictions)

    def test_aster_post_2008_swir_degradation(self):
        scene = AsterParser.parse(self.ast_post)
        self.assertIsNotNone(scene)
        self.assertEqual(scene.metadata.acquisition_date, datetime(2012, 5, 20))
        # VNIR is still valid
        self.assertTrue(scene.has_role(BandRole.GREEN))
        self.assertTrue(scene.has_role(BandRole.RED))
        self.assertTrue(scene.has_role(BandRole.NIR))
        # SWIR must be DISABLED and flagged
        self.assertFalse(scene.has_role(BandRole.SWIR_1))
        self.assertFalse(scene.has_role(BandRole.SWIR_2))
        self.assertIn("ASTER_SWIR_INVALID_POST_2008", scene.metadata.restrictions)
        self.assertTrue(any("SWIR subsystem degraded" in w for w in scene.metadata.warnings))


class TestSceneScanner(unittest.TestCase):
    def setUp(self):
        self.single_scene = FIXTURES / "landsat8_c2_l2"
        self.parent_area = FIXTURES / "parent_study_area"

    def test_single_scene_scan(self):
        res = SceneScanner.scan(self.single_scene)
        self.assertTrue(res.is_single_scene)
        self.assertEqual(len(res.scenes), 1)
        self.assertEqual(res.scenes[0].metadata.platform, "Landsat 8")

    def test_parent_directory_scan_ignores_work_results(self):
        res = SceneScanner.scan(self.parent_area)
        self.assertFalse(res.is_single_scene)
        # Should discover Scene1_Landsat and Scene2_ASTER
        self.assertEqual(len(res.scenes), 2)
        discovered_names = {s.scene_path.name for s in res.scenes}
        self.assertIn("Scene1_Landsat", discovered_names)
        self.assertIn("Scene2_ASTER_20050520", discovered_names)

        # Work, Results, Reports, unrelated_notes MUST NOT be in scenes
        for s in res.scenes:
            self.assertNotIn(s.scene_path.name.upper(), ["WORK", "RESULTS", "REPORTS", "UNRELATED_NOTES"])

        ignored_names = {p.name for p in res.ignored_paths}
        self.assertIn("Work", ignored_names)
        self.assertIn("Results", ignored_names)
        self.assertIn("Reports", ignored_names)
        self.assertIn("unrelated_notes", ignored_names)


class TestManualBandMapping(unittest.TestCase):
    def test_manual_band_mapper(self):
        dummy_red = FIXTURES / "landsat8_c2_l2" / "LC08_L2SP_176039_20230520_20230527_02_T1_SR_B4.TIF"
        dummy_nir = FIXTURES / "landsat8_c2_l2" / "LC08_L2SP_176039_20230520_20230527_02_T1_SR_B5.TIF"

        mappings = {
            BandRole.RED: dummy_red,
            BandRole.NIR: dummy_nir,
        }
        scene = ManualBandMapper.create_custom_scene(
            scene_path=FIXTURES / "landsat8_c2_l2",
            scene_id="CUSTOM_EXPERT_SCENE",
            platform_name="UAV_Multispectral",
            instrument_name="MicaSense",
            product_level=ProductLevel.L2_SR,
            mappings=mappings,
            scale_factors={BandRole.RED: 0.0001, BandRole.NIR: 0.0001},
        )
        self.assertTrue(scene.expert_mapped)
        self.assertEqual(scene.metadata.platform, "UAV_Multispectral")
        self.assertEqual(scene.metadata.instrument, "MicaSense")
        self.assertTrue(scene.has_role(BandRole.RED))
        self.assertTrue(scene.has_role(BandRole.NIR))
        self.assertFalse(scene.has_role(BandRole.BLUE))
        self.assertEqual(scene.get_band(BandRole.RED).scale_factor, 0.0001)


if __name__ == "__main__":
    unittest.main()

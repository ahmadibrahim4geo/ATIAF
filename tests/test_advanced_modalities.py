# -*- coding: utf-8 -*-
"""Unit and integration tests for ATIAF Advanced Modalities (Phase P8).

Tests:
1. Modality classification and router boundaries.
2. SAR Engine: linear-to-dB conversion, cross-polarization ratio, RVI, Lee speckle filter.
3. Strict gating: rejection of SAR products from optical spectral indices and thermal tools.
4. Hyperspectral Engine: metadata validation, water vapor absorption mask, SAM, absorption feature depth.
5. Strict gating: rejection of L1 hyperspectral from mineral unmixing.
6. Sentinel-1 SAR parser and SceneScanner integration.
"""

from datetime import datetime
from pathlib import Path
import shutil
import tempfile
import unittest
import numpy as np

from atiaf_core.discovery import (
    BandAsset,
    BandRole,
    ProductLevel,
    SceneInfo,
    SceneMetadata,
    SceneScanner,
    SensorFamily,
)
from atiaf_core.discovery.sentinel1 import Sentinel1Parser
from atiaf_core.indices import SpectralIndicesEngine
from atiaf_core.modalities import (
    HyperspectralCubeMetadata,
    HyperspectralEngine,
    ModalityCapabilityError,
    ModalityRouter,
    PolarizationRole,
    SAREngine,
    SensorModality,
)
from atiaf_core.temperature import SurfaceTemperatureEngine


class TestSAREngineAndGating(unittest.TestCase):
    """Tests SAR calculations, dB scaling, polarimetric ratios, and optical rejection."""

    def test_linear_to_db(self):
        # 0.1 -> -10 dB, 1.0 -> 0 dB, 10.0 -> +10 dB
        arr = np.array([[0.1, 1.0], [10.0, np.nan]], dtype=np.float32)
        db = SAREngine.linear_to_db(arr)

        self.assertAlmostEqual(float(db[0, 0]), -10.0, places=3)
        self.assertAlmostEqual(float(db[0, 1]), 0.0, places=3)
        self.assertAlmostEqual(float(db[1, 0]), 10.0, places=3)
        self.assertTrue(np.isnan(db[1, 1]))

    def test_db_to_linear(self):
        db = np.array([[-10.0, 0.0], [10.0, np.nan]], dtype=np.float32)
        lin = SAREngine.db_to_linear(db)

        self.assertAlmostEqual(float(lin[0, 0]), 0.1, places=3)
        self.assertAlmostEqual(float(lin[0, 1]), 1.0, places=3)
        self.assertAlmostEqual(float(lin[1, 0]), 10.0, places=3)
        self.assertTrue(np.isnan(lin[1, 1]))

    def test_cross_polarization_ratio(self):
        vh = np.array([[0.05, 0.2]], dtype=np.float32)
        vv = np.array([[0.25, 0.4]], dtype=np.float32)

        ratio_lin = SAREngine.cross_polarization_ratio(vh, vv, in_db=False)
        self.assertAlmostEqual(float(ratio_lin[0, 0]), 0.05 / 0.25, places=4)
        self.assertAlmostEqual(float(ratio_lin[0, 1]), 0.2 / 0.4, places=4)

        vh_db = SAREngine.linear_to_db(vh)
        vv_db = SAREngine.linear_to_db(vv)
        ratio_db = SAREngine.cross_polarization_ratio(vh_db, vv_db, in_db=True)
        self.assertAlmostEqual(float(ratio_db[0, 0]), float(vh_db[0, 0] - vv_db[0, 0]), places=3)

    def test_radar_vegetation_index(self):
        # Dense vegetation: VH high relative to VV
        vh_dense = np.array([[0.25]], dtype=np.float32)
        vv_dense = np.array([[0.50]], dtype=np.float32)
        rvi_dense = SAREngine.radar_vegetation_index(vh_dense, vv_dense)
        # RVI = (4 * 0.25) / (0.50 + 0.25) = 1.0 / 0.75 ≈ 1.333 -> clipped to 1.2
        self.assertAlmostEqual(float(rvi_dense[0, 0]), 1.2, places=3)

        # Bare soil: VH very low
        vh_bare = np.array([[0.01]], dtype=np.float32)
        vv_bare = np.array([[0.50]], dtype=np.float32)
        rvi_bare = SAREngine.radar_vegetation_index(vh_bare, vv_bare)
        # RVI = (4 * 0.01) / (0.50 + 0.01) = 0.04 / 0.51 ≈ 0.0784
        self.assertAlmostEqual(float(rvi_bare[0, 0]), 0.0784, places=3)

    def test_apply_lee_filter(self):
        np.random.seed(42)
        base = np.full((16, 16), 0.2, dtype=np.float32)
        noise = np.random.exponential(scale=0.05, size=(16, 16)).astype(np.float32)
        noisy = base + noise
        noisy[0, 0] = np.nan

        filtered = SAREngine.apply_lee_filter(noisy, window_size=3, num_looks=1)
        self.assertEqual(filtered.shape, noisy.shape)
        self.assertTrue(np.isnan(filtered[0, 0]))
        # Filtered variance should be reduced
        self.assertLess(np.nanvar(filtered), np.nanvar(noisy))

    def test_strict_sar_optical_rejection(self):
        """Verifies that attempting to run optical equations on SAR raises ModalityCapabilityError."""
        sar_meta = SceneMetadata(
            scene_id="S1A_IW_GRDH_1SDV_20230715T160000",
            sensor_family=SensorFamily.SENTINEL_1,
            sensor_id="C-SAR",
            platform="Sentinel-1A",
            instrument="C-SAR",
            product_level=ProductLevel.L1_GRD,
        )
        fake_scene = SceneInfo(
            scene_path=Path("dummy"),
            metadata=sar_meta,
            bands={},
        )

        with self.assertRaises(ModalityCapabilityError) as cm:
            SpectralIndicesEngine.run_scene_indices(
                scene=fake_scene,
                selected_index_ids=["NDVI"],
            )
        err = cm.exception
        self.assertEqual(err.detected_modality, SensorModality.SAR_RADAR)
        self.assertIn("SAR", err.reason_en)
        self.assertIn("رادار", err.reason_ar)


class TestHyperspectralEngineAndGating(unittest.TestCase):
    """Tests Hyperspectral cube metadata, SAM angle, absorption depth, and Level-2 gating."""

    def setUp(self):
        # 100 contiguous bands from 400 nm to 2400 nm
        self.wavelengths = np.linspace(400, 2400, 100).tolist()
        self.meta = HyperspectralCubeMetadata(
            num_bands=len(self.wavelengths),
            wavelengths_nm=self.wavelengths,
        )

    def test_water_vapor_absorption_detection(self):
        # 1400 nm is in 1350-1450 nm water window -> should be True (bad)
        idx_1400 = self.meta.find_closest_band_index(1400.0)
        self.assertIsNotNone(idx_1400)
        self.assertTrue(self.meta.bad_bands_mask[idx_1400])

        # 850 nm (NIR) is clear -> should be False (good)
        idx_850 = self.meta.find_closest_band_index(850.0)
        self.assertIsNotNone(idx_850)
        self.assertFalse(self.meta.bad_bands_mask[idx_850])

    def test_spectral_angle_mapper_identical_and_scaled(self):
        ref = np.array([0.1, 0.2, 0.4, 0.3], dtype=np.float32)

        # 1. Identical spectrum: angle = 0
        pixels_identical = ref.reshape(4, 1, 1)
        angle_0 = HyperspectralEngine.spectral_angle_mapper(pixels_identical, ref)
        self.assertAlmostEqual(float(angle_0[0, 0]), 0.0, places=5)

        # 2. Scaled spectrum (illumination change: twice brighter): SAM must be 0!
        pixels_scaled = (ref * 2.5).reshape(4, 1, 1)
        angle_scaled = HyperspectralEngine.spectral_angle_mapper(pixels_scaled, ref)
        self.assertAlmostEqual(float(angle_scaled[0, 0]), 0.0, places=5)

    def test_spectral_angle_mapper_orthogonal(self):
        ref = np.array([1.0, 0.0], dtype=np.float32)
        ortho = np.array([[0.0]], dtype=np.float32)
        target = np.array([[0.0], [1.0]], dtype=np.float32).reshape(2, 1, 1)

        angle = HyperspectralEngine.spectral_angle_mapper(target, ref)
        # cos(alpha) = 0 -> alpha = pi / 2 ≈ 1.57079 rad
        self.assertAlmostEqual(float(angle[0, 0]), np.pi / 2.0, places=4)

    def test_absorption_feature_depth(self):
        # Construct synthetic cube with a dip at 2200 nm (Al-OH feature)
        bands = len(self.wavelengths)
        cube = np.full((bands, 4, 4), 0.5, dtype=np.float32)

        idx_2200 = self.meta.find_closest_band_index(2205.0)
        self.assertIsNotNone(idx_2200)

        # Create absorption dip: R_center = 0.2, shoulders = 0.5
        cube[idx_2200] = 0.2

        depth = HyperspectralEngine.absorption_feature_depth(
            cube=cube,
            wavelengths_nm=self.wavelengths,
            feature_name="AL_OH_2200",
        )
        self.assertEqual(depth.shape, (4, 4))
        # Expected depth = 1 - (0.2 / 0.5) = 0.6
        self.assertAlmostEqual(float(depth[0, 0]), 0.6, places=2)

    def test_strict_hyperspectral_l1_gating(self):
        """Verifies that uncalibrated TOA/L1 hyperspectral cubes are rejected from mineral unmixing."""
        with self.assertRaises(ModalityCapabilityError) as cm:
            HyperspectralEngine.assert_l2_surface_reflectance(
                scene_id="ENMAP01-____-L1B_TOA",
                instrument="HSI",
                product_level="L1B_TOA",
                requested_tool="Geological_Analysis",
            )
        err = cm.exception
        self.assertEqual(err.detected_modality, SensorModality.HYPERSPECTRAL)
        self.assertIn("Level-2", err.reason_en)
        self.assertIn("Level-2", err.reason_ar)


class TestSentinel1DiscoveryAndScanner(unittest.TestCase):
    """Tests discovery of Sentinel-1 SAFE directory and SceneScanner routing."""

    def setUp(self):
        self.temp_dir = Path(tempfile.mkdtemp(prefix="atyaf_s1_test_"))
        self.s1_dir = self.temp_dir / "S1A_IW_GRDH_1SDV_20230715T160000_20230715T160025_049441_05F2BA_ABCD.SAFE"
        self.s1_dir.mkdir(parents=True, exist_ok=True)

        meas_dir = self.s1_dir / "measurement"
        meas_dir.mkdir(parents=True, exist_ok=True)

        # Write dummy measurement GeoTIFFs for VV and VH
        (meas_dir / "s1a-iw-grd-vv-20230715t160000-20230715t160025-049441-05f2ba-001.tiff").write_bytes(b"DUMMY_VV")
        (meas_dir / "s1a-iw-grd-vh-20230715t160000-20230715t160025-049441-05f2ba-002.tiff").write_bytes(b"DUMMY_VH")

        manifest_content = """<?xml version="1.0" encoding="utf-8"?>
<xfdu:XFDU xmlns:xfdu="urn:ccsds:schema:xfdu:encodings:metadata:cdsm:1.0">
  <metadataSection>
    <metadataObject ID="acquisitionPeriod">
      <metadataWrap mimeType="text/xml" vocabularyName="SAFE">
        <xmlData>
          <safe:acquisitionPeriod xmlns:safe="http://www.esa.int/safe/sentinel-1.0">
            <safe:startTime>2023-07-15T16:00:00.123456Z</safe:startTime>
            <safe:stopTime>2023-07-15T16:00:25.123456Z</safe:stopTime>
          </safe:acquisitionPeriod>
        </xmlData>
      </metadataWrap>
    </metadataObject>
  </metadataSection>
</xfdu:XFDU>
"""
        (self.s1_dir / "manifest.safe").write_text(manifest_content, encoding="utf-8")

    def tearDown(self):
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_sentinel1_parser_can_parse(self):
        self.assertTrue(Sentinel1Parser.can_parse(self.s1_dir))

    def test_sentinel1_parser_extracts_bands_and_metadata(self):
        scene = Sentinel1Parser.parse(self.s1_dir)
        self.assertIsNotNone(scene)
        self.assertEqual(scene.metadata.sensor_family, SensorFamily.SENTINEL_1)
        self.assertEqual(scene.metadata.platform, "Sentinel-1A")
        self.assertEqual(scene.metadata.instrument, "C-SAR")
        self.assertEqual(scene.metadata.product_level, ProductLevel.L1_GRD)
        self.assertEqual(scene.metadata.acquisition_date.year, 2023)
        self.assertEqual(scene.metadata.acquisition_date.month, 7)
        self.assertEqual(scene.metadata.acquisition_date.day, 15)

        # Bands check
        self.assertIn(BandRole.SAR_VV, scene.bands)
        self.assertIn(BandRole.SAR_VH, scene.bands)
        self.assertFalse(scene.has_thermal())

    def test_scene_scanner_identifies_sentinel1(self):
        scan = SceneScanner.scan(self.s1_dir)
        self.assertTrue(scan.is_single_scene)
        self.assertEqual(len(scan.scenes), 1)
        scene = scan.scenes[0]
        self.assertEqual(scene.metadata.sensor_family, SensorFamily.SENTINEL_1)

        # Modality Router classification check
        modality = ModalityRouter.classify_modality(scene.metadata)
        self.assertEqual(modality, SensorModality.SAR_RADAR)


if __name__ == "__main__":
    unittest.main()

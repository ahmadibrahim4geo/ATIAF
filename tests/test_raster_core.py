"""Unit and integration tests for ATIAF Core Raster Array Processing, CRS, Masks & Workspace Manager (Phase P2)."""

import json
from pathlib import Path
import shutil
import tempfile
import unittest

import numpy as np
import pyproj
import rasterio
from rasterio.transform import from_origin
from shapely.geometry import box, Polygon

from atyaf_core.raster import (
    CRSManager,
    CRSValidationResult,
    QualityMaskEngine,
    PolygonClipEngine,
    WindowedRasterEngine,
    WorkspaceManager,
)

ROOT = Path(__file__).resolve().parents[1]


class TestCRSValidation(unittest.TestCase):
    def test_projected_metre_accepted(self):
        # UTM zone 36N (WGS 84 / UTM zone 36N, EPSG:32636)
        res = CRSManager.validate_projected_metre(32636)
        self.assertTrue(res.is_valid_projected_metre)
        self.assertTrue(res.is_projected)
        self.assertFalse(res.is_geographic)
        self.assertEqual(res.epsg, 32636)
        self.assertIn("metre", res.linear_unit_name.lower())

    def test_geographic_degree_rejected(self):
        # WGS 84 geographic (EPSG:4326)
        res = CRSManager.validate_projected_metre(4326)
        self.assertFalse(res.is_valid_projected_metre)
        self.assertTrue(res.is_geographic)
        self.assertFalse(res.is_projected)
        self.assertIn("Geographic coordinate system rejected", res.message)

    def test_web_mercator_accepted(self):
        # WGS 84 / Pseudo-Mercator (EPSG:3857) - metre based
        res = CRSManager.validate_projected_metre("EPSG:3857")
        self.assertTrue(res.is_valid_projected_metre)
        self.assertTrue(res.is_projected)

    def test_invalid_string_rejected(self):
        res = CRSManager.validate_projected_metre("INVALID_PROJECTION_XYZ")
        self.assertFalse(res.is_valid_projected_metre)
        self.assertIn("Invalid or unparseable", res.message)


class TestQualityMaskEngine(unittest.TestCase):
    def test_landsat_c2_qa_mask(self):
        # Construct synthetic QA_PIXEL values
        # Bit 0=Fill, 1=Dilated Cloud, 2=Cirrus, 3=Cloud, 4=Cloud Shadow, 5=Snow, 6=Clear
        clear_pixel = 1 << QualityMaskEngine.LANDSAT_BIT_CLEAR
        cloud_pixel = (1 << QualityMaskEngine.LANDSAT_BIT_CLOUD) | (1 << QualityMaskEngine.LANDSAT_BIT_DILATED_CLOUD)
        shadow_pixel = 1 << QualityMaskEngine.LANDSAT_BIT_CLOUD_SHADOW
        snow_pixel = 1 << QualityMaskEngine.LANDSAT_BIT_SNOW
        fill_pixel = 1 << QualityMaskEngine.LANDSAT_BIT_FILL

        qa_arr = np.array([clear_pixel, cloud_pixel, shadow_pixel, snow_pixel, fill_pixel], dtype=np.uint16)
        clear_mask = QualityMaskEngine.get_landsat_c2_clear_mask(qa_arr)

        # Expected: only index 0 is clear/valid
        self.assertTrue(clear_mask[0])
        self.assertFalse(clear_mask[1])
        self.assertFalse(clear_mask[2])
        self.assertFalse(clear_mask[3])
        self.assertFalse(clear_mask[4])

    def test_sentinel2_scl_mask(self):
        scl_arr = np.array([
            QualityMaskEngine.S2_SCL_VEGETATION,
            QualityMaskEngine.S2_SCL_BARE_SOIL,
            QualityMaskEngine.S2_SCL_WATER,
            QualityMaskEngine.S2_SCL_CLOUD_SHADOW,
            QualityMaskEngine.S2_SCL_CLOUD_HIGH_PROB,
            QualityMaskEngine.S2_SCL_THIN_CIRRUS,
            QualityMaskEngine.S2_SCL_SNOW,
            QualityMaskEngine.S2_SCL_NODATA,
        ], dtype=np.uint8)

        clear_mask = QualityMaskEngine.get_sentinel2_scl_clear_mask(scl_arr)

        # 0=Veg (True), 1=Soil (True), 2=Water (True), rest are invalid
        self.assertTrue(clear_mask[0])
        self.assertTrue(clear_mask[1])
        self.assertTrue(clear_mask[2])
        self.assertFalse(clear_mask[3])
        self.assertFalse(clear_mask[4])
        self.assertFalse(clear_mask[5])
        self.assertFalse(clear_mask[6])
        self.assertFalse(clear_mask[7])

    def test_apply_valid_range_and_nodata(self):
        raw = np.array([10.0, 50.0, 100.0, 0.0, -999.0], dtype=np.float32)
        cleaned = QualityMaskEngine.apply_valid_range_and_nodata(
            raw, valid_min=5.0, valid_max=80.0, nodata=-999.0
        )
        self.assertEqual(cleaned[0], 10.0)
        self.assertEqual(cleaned[1], 50.0)
        self.assertTrue(np.isnan(cleaned[2]))  # > 80.0
        self.assertTrue(np.isnan(cleaned[3]))  # < 5.0
        self.assertTrue(np.isnan(cleaned[4]))  # nodata


class TestWindowedRasterEngine(unittest.TestCase):
    def setUp(self):
        self.temp_dir = Path(tempfile.mkdtemp())
        self.red_path = self.temp_dir / "red.tif"
        self.nir_path = self.temp_dir / "nir.tif"
        self.out_path = self.temp_dir / "ndvi.tif"

        # Create synthetic GeoTIFFs (64 x 64 pixels, 30m resolution, UTM 36N)
        width, height = 64, 64
        transform = from_origin(300000, 3300000, 30, 30)
        crs = "EPSG:32636"

        # Synthetic reflectance values (scaled 0 to 1)
        red_data = np.full((height, width), 0.10, dtype=np.float32)
        nir_data = np.full((height, width), 0.50, dtype=np.float32)

        profile = {
            "driver": "GTiff",
            "width": width,
            "height": height,
            "count": 1,
            "dtype": "float32",
            "crs": crs,
            "transform": transform,
            "nodata": -9999.0,
        }

        with rasterio.open(self.red_path, "w", **profile) as ds:
            ds.write(red_data, 1)

        with rasterio.open(self.nir_path, "w", **profile) as ds:
            ds.write(nir_data, 1)

    def tearDown(self):
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_windowed_ndvi_computation(self):
        def compute_ndvi(blocks):
            r = blocks["red"]
            n = blocks["nir"]
            return (n - r) / (n + r)

        res = WindowedRasterEngine.process_bands(
            band_paths={"red": self.red_path, "nir": self.nir_path},
            output_path=self.out_path,
            compute_fn=compute_ndvi,
            output_nodata=-9999.0,
            block_size=16,  # 16x16 blocks
        )

        self.assertTrue(self.out_path.exists())
        self.assertEqual(res["valid_pixels"], 64 * 64)
        self.assertEqual(res["nodata_pixels"], 0)

        # Expected NDVI = (0.50 - 0.10) / (0.50 + 0.10) = 0.40 / 0.60 = 0.6666667
        expected_ndvi = (0.50 - 0.10) / (0.50 + 0.10)
        self.assertAlmostEqual(res["statistics"]["mean"], expected_ndvi, places=4)
        self.assertAlmostEqual(res["statistics"]["min"], expected_ndvi, places=4)
        self.assertAlmostEqual(res["statistics"]["max"], expected_ndvi, places=4)

        # Re-read GeoTIFF and verify raster integrity
        with rasterio.open(self.out_path) as ds:
            data = ds.read(1)
            self.assertEqual(ds.width, 64)
            self.assertEqual(ds.height, 64)
            self.assertEqual(ds.crs.to_string(), "EPSG:32636")
            self.assertAlmostEqual(float(data[0, 0]), expected_ndvi, places=4)

    def test_atomic_write_failure_cleanup(self):
        def failing_compute(blocks):
            raise RuntimeError("Simulated processing crash")

        fail_out = self.temp_dir / "fail_ndvi.tif"
        with self.assertRaises(RuntimeError):
            WindowedRasterEngine.process_bands(
                band_paths={"red": self.red_path, "nir": self.nir_path},
                output_path=fail_out,
                compute_fn=failing_compute,
                block_size=16,
            )

        # Neither the target file nor any temporary file should remain
        self.assertFalse(fail_out.exists())
        tmp_files = list(self.temp_dir.glob(".tmp_*"))
        self.assertEqual(len(tmp_files), 0)


class TestPolygonClipping(unittest.TestCase):
    def setUp(self):
        self.temp_dir = Path(tempfile.mkdtemp())
        self.raster_path = self.temp_dir / "grid.tif"
        self.clip_path = self.temp_dir / "clipped.tif"

        # 100 x 100 raster, origin (0, 1000), cell size 10m
        width, height = 100, 100
        transform = from_origin(0, 1000, 10, 10)
        data = np.ones((height, width), dtype=np.float32)

        with rasterio.open(
            self.raster_path,
            "w",
            driver="GTiff",
            width=width,
            height=height,
            count=1,
            dtype="float32",
            crs="EPSG:32636",
            transform=transform,
            nodata=-9999.0,
        ) as ds:
            ds.write(data, 1)

    def tearDown(self):
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_polygon_clip(self):
        # Clip polygon: box from x=200..600, y=400..800 (40x40 pixels)
        poly = box(200, 400, 600, 800)
        res = PolygonClipEngine.clip_raster_file(
            src_raster_path=self.raster_path,
            dst_raster_path=self.clip_path,
            aoi_geometry=poly,
            aoi_crs="EPSG:32636",
            crop=True,
            nodata=-9999.0,
        )

        self.assertTrue(self.clip_path.exists())
        self.assertEqual(res["width"], 40)
        self.assertEqual(res["height"], 40)

        with rasterio.open(self.clip_path) as ds:
            clipped_data = ds.read(1)
            self.assertEqual(ds.width, 40)
            self.assertEqual(ds.height, 40)
            self.assertTrue(np.all(clipped_data == 1.0))


class TestWorkspaceManager(unittest.TestCase):
    def setUp(self):
        self.temp_dir = Path(tempfile.mkdtemp())
        self.scene_dir = self.temp_dir / "LC08_L2SP_176039_20230520"
        self.scene_dir.mkdir(parents=True, exist_ok=True)
        self.dummy_band = self.scene_dir / "LC08_B4.TIF"
        self.dummy_band.write_bytes(b"TEST_BAND_BYTES")

    def tearDown(self):
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_workspace_roots_single_scene_default(self):
        scene_root, work_dir, cache_dir, results_dir, reports_dir = WorkspaceManager.resolve_workspace_roots(
            self.scene_dir, custom_destination=None
        )
        self.assertEqual(scene_root, self.scene_dir)
        self.assertEqual(work_dir, self.scene_dir / "Work")
        self.assertEqual(cache_dir, self.scene_dir / "Work" / "Preprocessing_Cache")
        self.assertEqual(results_dir, self.scene_dir / "Results")
        self.assertEqual(reports_dir, self.scene_dir / "Results" / "Reports")

        # Second call does not create Results_2
        roots_2 = WorkspaceManager.resolve_workspace_roots(self.scene_dir)
        self.assertEqual(roots_2[3], self.scene_dir / "Results")
        self.assertFalse((self.scene_dir / "Results_2").exists())

    def test_workspace_roots_custom_destination(self):
        custom_dest = self.temp_dir / "CustomOutput"
        scene_root, work_dir, cache_dir, results_dir, _ = WorkspaceManager.resolve_workspace_roots(
            self.scene_dir, custom_destination=custom_dest
        )
        expected_scene = custom_dest / self.scene_dir.name
        self.assertEqual(scene_root, expected_scene)
        self.assertEqual(results_dir, expected_scene / "Results")

    def test_cache_fingerprint(self):
        fp1 = WorkspaceManager.compute_cache_fingerprint(
            source_paths=[self.dummy_band],
            method_name="NDVI",
            parameters={"scale": 0.0000275, "offset": -0.2},
            target_crs_str="EPSG:32636",
        )
        fp2 = WorkspaceManager.compute_cache_fingerprint(
            source_paths=[self.dummy_band],
            method_name="NDVI",
            parameters={"scale": 0.0000275, "offset": -0.2},
            target_crs_str="EPSG:32636",
        )
        # Same parameters -> identical fingerprint
        self.assertEqual(fp1, fp2)

        # Changed parameter -> different fingerprint
        fp3 = WorkspaceManager.compute_cache_fingerprint(
            source_paths=[self.dummy_band],
            method_name="NDVI",
            parameters={"scale": 0.0001, "offset": 0.0},
            target_crs_str="EPSG:32636",
        )
        self.assertNotEqual(fp1, fp3)

    def test_run_manifest_generation(self):
        _, _, _, results_dir, reports_dir = WorkspaceManager.resolve_workspace_roots(self.scene_dir)
        run_dir = WorkspaceManager.create_run_manifest(
            reports_dir=reports_dir,
            scene_id="LC08_L2SP_176039_20230520",
            tool_name="Spectral_Indices",
            parameters={"index": "NDVI"},
            output_products=[{"name": "NDVI_FULL.tif", "valid_pixels": 4096}],
            qa_summary={"cloud_pixels": 0, "clear_pixels": 4096},
            log_messages=["Step 1: Scaled bands", "Step 2: Computed NDVI"],
        )

        self.assertTrue(run_dir.exists())
        self.assertTrue((run_dir / "Processing_Manifest.json").exists())
        self.assertTrue((run_dir / "Parameters.json").exists())
        self.assertTrue((run_dir / "Quality_Assessment.csv").exists())
        self.assertTrue((run_dir / "Processing_Log.txt").exists())

        manifest_data = json.loads((run_dir / "Processing_Manifest.json").read_text(encoding="utf-8"))
        self.assertEqual(manifest_data["scene_id"], "LC08_L2SP_176039_20230520")
        self.assertEqual(manifest_data["tool_name"], "Spectral_Indices")


if __name__ == "__main__":
    unittest.main()

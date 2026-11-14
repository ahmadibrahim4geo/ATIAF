"""Unit and integration tests for ATIAF Quality Mosaic and Temporal Change Detection (Phase P5)."""

from datetime import datetime
import json
from pathlib import Path
import shutil
import tempfile
import unittest
import numpy as np
import rasterio

from atyaf_core.discovery.models import (
    BandAsset,
    BandRole,
    ProductLevel,
    QualityAsset,
    SceneInfo,
    SceneMetadata,
    SensorFamily,
)
from atyaf_core.mosaic import MosaicStrategy, QualityMosaicEngine
from atyaf_core.temporal import ChangeDetectionEngine

ROOT = Path(__file__).resolve().parents[1]


def create_synthetic_scene_info(
    scene_id: str,
    date_str: str,
    scene_dir: Path,
    raster_path: Path,
) -> SceneInfo:
    """Helper to construct a SceneInfo mock for testing."""
    meta = SceneMetadata(
        scene_id=scene_id,
        sensor_family=SensorFamily.LANDSAT,
        sensor_id="LANDSAT_8",
        platform="Landsat-8",
        instrument="OLI_TIRS",
        product_level=ProductLevel.L2_SR,
        acquisition_date=datetime.fromisoformat(date_str),
    )
    bands = {
        BandRole.RED: BandAsset(
            role=BandRole.RED,
            file_path=raster_path,
            band_name="SR_B4.TIF",
            center_wavelength_nm=655.0,
            resolution_m=30.0,
            scale_factor=0.0000275,
            offset=-0.2,
        ),
    }
    return SceneInfo(
        scene_path=scene_dir,
        metadata=meta,
        bands=bands,
        quality_masks={},
    )


class TestQualityMosaicEngine(unittest.TestCase):
    """Tests multi-scene mosaic blending, union extent, provenance raster, and strategies."""

    def setUp(self):
        self.temp_dir = Path(tempfile.mkdtemp())
        self.output_root = self.temp_dir / "mosaic_output"

        # Construct two synthetic raster files representing adjacent overlapping satellite scenes
        # Resolution: 30m, 32x32 pixels
        self.width, self.height = 32, 32
        self.res = 30.0

        # Scene 1: origin (300000, 3300000)
        self.t1_origin = (300000.0, 3300000.0)
        self.transform1 = rasterio.transform.from_origin(self.t1_origin[0], self.t1_origin[1], self.res, self.res)

        # Scene 2: origin (300480, 3300000) -> shifted right by 16 pixels (16 * 30m = 480m)
        self.t2_origin = (300480.0, 3300000.0)
        self.transform2 = rasterio.transform.from_origin(self.t2_origin[0], self.t2_origin[1], self.res, self.res)

        profile = {
            "driver": "GTiff",
            "width": self.width,
            "height": self.height,
            "count": 1,
            "dtype": "float32",
            "crs": "EPSG:32636",
            "nodata": -9999.0,
        }

        # Scene 1 data: constant 0.40
        self.scene1_path = self.temp_dir / "scene1_ndvi.tif"
        profile1 = profile.copy()
        profile1["transform"] = self.transform1
        with rasterio.open(self.scene1_path, "w", **profile1) as ds:
            ds.write(np.full((self.height, self.width), 0.40, dtype=np.float32), 1)

        # Scene 2 data: constant 0.80
        self.scene2_path = self.temp_dir / "scene2_ndvi.tif"
        profile2 = profile.copy()
        profile2["transform"] = self.transform2
        with rasterio.open(self.scene2_path, "w", **profile2) as ds:
            ds.write(np.full((self.height, self.width), 0.80, dtype=np.float32), 1)

        self.scene1_info = create_synthetic_scene_info("LC08_SCENE1", "2023-05-10", self.temp_dir, self.scene1_path)
        self.scene2_info = create_synthetic_scene_info("LC08_SCENE2", "2023-05-26", self.temp_dir, self.scene2_path)

    def tearDown(self):
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_mosaic_union_extent_and_provenance(self):
        res = QualityMosaicEngine.run_mosaic(
            scene_products=[(self.scene1_info, self.scene1_path), (self.scene2_info, self.scene2_path)],
            product_name="NDVI",
            category="Spectral_Indices",
            output_root=self.output_root,
            strategy=MosaicStrategy.HIGHEST_QUALITY,
        )

        self.assertTrue(Path(res.full_path).exists())
        self.assertTrue(Path(res.provenance_path).exists())

        # Inspect mosaic dimensions: width should span 300000 to 300480 + 32*30 = 301440 -> 1440 / 30 = 48 pixels
        with rasterio.open(res.full_path) as ds:
            self.assertEqual(ds.width, 48)
            self.assertEqual(ds.height, 32)
            arr = ds.read(1)
            valid = arr[arr != -9999.0]
            self.assertEqual(len(valid), 48 * 32)

        # Inspect provenance raster
        with rasterio.open(res.provenance_path) as ds_prov:
            prov = ds_prov.read(1)
            # Left non-overlap region should be Scene 1 (numeric_id = 1)
            self.assertTrue(np.all(prov[:, :16] == 1))
            # Right non-overlap region should be Scene 2 (numeric_id = 2)
            self.assertTrue(np.all(prov[:, 32:] == 2))

    def test_mosaic_mean_valid_strategy(self):
        res = QualityMosaicEngine.run_mosaic(
            scene_products=[(self.scene1_info, self.scene1_path), (self.scene2_info, self.scene2_path)],
            product_name="NDVI",
            category="Spectral_Indices",
            output_root=self.output_root,
            strategy=MosaicStrategy.MEAN_VALID,
        )

        with rasterio.open(res.full_path) as ds:
            arr = ds.read(1)
            # In the overlap zone (columns 16 to 32), value should be (0.40 + 0.80) / 2 = 0.60
            overlap_vals = arr[:, 16:32]
            np.testing.assert_allclose(overlap_vals, 0.60, atol=1e-3)

    def test_mosaic_latest_date_strategy(self):
        # Scene 2 has later date (2023-05-26 > 2023-05-10); should overwrite Scene 1 in overlap
        res = QualityMosaicEngine.run_mosaic(
            scene_products=[(self.scene1_info, self.scene1_path), (self.scene2_info, self.scene2_path)],
            product_name="NDVI",
            category="Spectral_Indices",
            output_root=self.output_root,
            strategy=MosaicStrategy.LATEST_DATE,
        )

        with rasterio.open(res.full_path) as ds:
            arr = ds.read(1)
            overlap_vals = arr[:, 16:32]
            np.testing.assert_allclose(overlap_vals, 0.80, atol=1e-3)


class TestChangeDetectionEngine(unittest.TestCase):
    """Tests temporal change calculations: absolute delta, relative %, burn severity, and std classes."""

    def setUp(self):
        self.temp_dir = Path(tempfile.mkdtemp())
        self.output_root = self.temp_dir / "change_output"

        self.width, self.height = 32, 32
        transform = rasterio.transform.from_origin(300000.0, 3300000.0, 30.0, 30.0)
        profile = {
            "driver": "GTiff",
            "width": self.width,
            "height": self.height,
            "count": 1,
            "dtype": "float32",
            "crs": "EPSG:32636",
            "transform": transform,
            "nodata": -9999.0,
        }

        # T1: baseline NBR = 0.60
        self.t1_path = self.temp_dir / "t1_nbr.tif"
        with rasterio.open(self.t1_path, "w", **profile) as ds:
            ds.write(np.full((self.height, self.width), 0.60, dtype=np.float32), 1)

        # T2: target post-fire NBR = 0.20
        self.t2_path = self.temp_dir / "t2_nbr.tif"
        with rasterio.open(self.t2_path, "w", **profile) as ds:
            ds.write(np.full((self.height, self.width), 0.20, dtype=np.float32), 1)

    def tearDown(self):
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_burn_severity_classification_math(self):
        # Test USGS classification mappings
        dnbr = np.array([[-0.50, -0.20, 0.0, 0.15, 0.35, 0.55, 0.80]], dtype=np.float32)
        classes = ChangeDetectionEngine.classify_burn_severity(dnbr)
        expected = np.array([[1, 2, 3, 4, 5, 6, 7]], dtype=np.uint8)
        np.testing.assert_array_equal(classes, expected)

    def test_std_change_classification(self):
        # Array with an extreme outlier so std is well controlled
        delta = np.array([[-10.0, -1.0, 0.0, 1.0, 10.0]], dtype=np.float32)
        classes = ChangeDetectionEngine.classify_std_change(delta)
        # 1: sig dec, 2: mod dec, 3: stable, 4: mod inc, 5: sig inc
        self.assertEqual(classes[0, 0], 1)
        self.assertEqual(classes[0, 2], 3)
        self.assertEqual(classes[0, 4], 5)

    def test_run_change_detection_nbr_burn(self):
        res = ChangeDetectionEngine.run_change_detection(
            t1_raster_path=self.t1_path,
            t2_raster_path=self.t2_path,
            t1_scene_id="LC08_PRE_FIRE",
            t2_scene_id="LC08_POST_FIRE",
            t1_date="2023-05-15",
            t2_date="2023-06-15",
            metric_name="NBR",
            output_root=self.output_root,
            calc_relative=True,
            classify_severity=True,
        )

        self.assertIn("executed_products", res)
        # Should have Delta_NBR, Relative_Change_NBR, and Burn_Severity_Classification
        prod_names = [p["product_name"] for p in res["executed_products"]]
        self.assertIn("Delta_NBR", prod_names)
        self.assertIn("Relative_Change_NBR", prod_names)
        self.assertIn("Burn_Severity_Classification", prod_names)

        # For NBR with classify_severity=True, dNBR = T1 - T2 = 0.60 - 0.20 = 0.40
        delta_stat = res["delta_statistics"]
        self.assertAlmostEqual(delta_stat["mean"], 0.40, places=3)

        # 0.40 falls into Moderate-Low Severity (Class 5: 0.27 to 0.44)
        burn_prod = next(p for p in res["executed_products"] if p["product_name"] == "Burn_Severity_Classification")
        with rasterio.open(burn_prod["full_path"]) as ds:
            burn_arr = ds.read(1)
            self.assertTrue(np.all(burn_arr == 5))

        # Check run manifest
        run_dir = Path(res["run_dir"])
        self.assertTrue((run_dir / "Processing_Manifest.json").exists())
        with open(run_dir / "Processing_Manifest.json", "r", encoding="utf-8") as f:
            manifest = json.load(f)
            self.assertEqual(manifest["tool_name"], "06_Temporal_Change_Detection")


class TestArcGISProToolboxPhase5(unittest.TestCase):
    """Verifies that arcgis_pro/ATIAF.pyt exposes Tools 01, 02, 05, and 06."""

    def test_toolbox_tools_list_phase5(self):
        pyt_path = ROOT / "arcgis_pro" / "ATIAF.pyt"
        self.assertTrue(pyt_path.exists())

        code = pyt_path.read_text(encoding="utf-8")
        compiled = compile(code, str(pyt_path), "exec")
        namespace = {"__file__": str(pyt_path)}
        exec(compiled, namespace)

        self.assertIn("Toolbox", namespace)
        self.assertIn("TemporalChangeTool", namespace)

        tb = namespace["Toolbox"]()
        tool_names = [t.__name__ for t in tb.tools]
        self.assertEqual(len(tool_names), 4)
        self.assertIn("SpectralIndicesTool", tool_names)
        self.assertIn("SurfaceTemperatureTool", tool_names)
        self.assertIn("GeologicalAnalysisTool", tool_names)
        self.assertIn("TemporalChangeTool", tool_names)

        change_tool = namespace["TemporalChangeTool"]()
        self.assertIn("Temporal Analysis", change_tool.label)
        self.assertTrue(change_tool.isLicensed())
        self.assertTrue(hasattr(change_tool, "getParameterInfo"))
        self.assertTrue(hasattr(change_tool, "updateParameters"))
        self.assertTrue(hasattr(change_tool, "updateMessages"))
        self.assertTrue(hasattr(change_tool, "execute"))


if __name__ == "__main__":
    unittest.main()

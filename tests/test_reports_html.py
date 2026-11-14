# -*- coding: utf-8 -*-
"""Unit tests for bilingual HTML run report generation and cumulative Reports/index.html."""

import json
from pathlib import Path
import shutil
import tempfile
import unittest

from atyaf_core.raster.workspace import WorkspaceManager


class TestHtmlReporting(unittest.TestCase):
    """Verifies standalone HTML run report and cumulative index generation."""

    def setUp(self):
        self.temp_dir = Path(tempfile.mkdtemp(prefix="atyaf_test_reports_"))
        self.reports_dir = self.temp_dir / "Results" / "Reports"
        self.reports_dir.mkdir(parents=True, exist_ok=True)

    def tearDown(self):
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_single_run_html_and_index_generation(self):
        """Verifies report.html and index.html are generated on run completion."""
        parameters = {
            "indices": ["NDVI", "NDWI"],
            "apply_qa_mask": True,
            "has_aoi": False,
        }
        outputs = [
            {
                "product_name": "NDVI",
                "full_path": str(self.temp_dir / "NDVI_LC08_FULL.tif"),
                "clipped_path": None,
                "valid_pixels": 256,
            },
            {
                "product_name": "NDWI",
                "full_path": str(self.temp_dir / "NDWI_LC08_FULL.tif"),
                "clipped_path": None,
                "valid_pixels": 250,
            },
        ]
        qa = {"executed_count": 2, "skipped_count": 0}
        logs = ["Starting spectral index calculation.", "Processing completed successfully."]

        run_dir = WorkspaceManager.create_run_manifest(
            reports_dir=self.reports_dir,
            scene_id="LC08_L2SP_176039_20230520",
            tool_name="01_Spectral_Indices",
            parameters=parameters,
            output_products=outputs,
            qa_summary=qa,
            log_messages=logs,
        )

        # 1. Verify standard manifest files exist
        self.assertTrue((run_dir / "Processing_Manifest.json").is_file())
        self.assertTrue((run_dir / "Parameters.json").is_file())
        self.assertTrue((run_dir / "Quality_Assessment.csv").is_file())
        self.assertTrue((run_dir / "Processing_Log.txt").is_file())

        # 2. Verify standalone report.html exists and is well-formed
        report_html_path = run_dir / "report.html"
        self.assertTrue(report_html_path.is_file(), "report.html was not generated")
        content = report_html_path.read_text(encoding="utf-8")
        self.assertIn("ATIAF", content)
        self.assertIn("LC08_L2SP_176039_20230520", content)
        self.assertIn("01_Spectral_Indices", content)
        self.assertIn("NDVI", content)
        self.assertIn("NDWI", content)
        self.assertIn("256", content)
        # Check Arabic / bilingual elements
        self.assertIn("أطياف", content)
        self.assertIn("معاملات وبيانات التشغيل", content)

        # 3. Verify cumulative index.html exists
        index_html_path = self.reports_dir / "index.html"
        self.assertTrue(index_html_path.is_file(), "index.html was not generated")
        idx_content = index_html_path.read_text(encoding="utf-8")
        self.assertIn("Cumulative Processing Reports Index", idx_content)
        self.assertIn("01_Spectral_Indices", idx_content)
        self.assertIn("LC08_L2SP_176039_20230520", idx_content)
        self.assertIn("report.html", idx_content)

    def test_cumulative_index_multiple_runs(self):
        """Verifies that multiple runs are cumulatively aggregated without losing past history."""
        # Run 1
        run_dir_1 = WorkspaceManager.create_run_manifest(
            reports_dir=self.reports_dir,
            scene_id="SCENE_01",
            tool_name="01_Spectral_Indices",
            parameters={"test": 1},
            output_products=[{"product_name": "NDVI"}],
        )

        # Run 2
        run_dir_2 = WorkspaceManager.create_run_manifest(
            reports_dir=self.reports_dir,
            scene_id="SCENE_02",
            tool_name="02_Surface_Temperature",
            parameters={"test": 2},
            output_products=[{"product_name": "LST"}],
        )

        index_html_path = self.reports_dir / "index.html"
        self.assertTrue(index_html_path.is_file())
        idx_content = index_html_path.read_text(encoding="utf-8")

        # Both runs must be present
        self.assertIn("SCENE_01", idx_content)
        self.assertIn("SCENE_02", idx_content)
        self.assertIn("01_Spectral_Indices", idx_content)
        self.assertIn("02_Surface_Temperature", idx_content)
        self.assertIn(run_dir_1.name, idx_content)
        self.assertIn(run_dir_2.name, idx_content)
        self.assertIn("Total Runs Recorded", idx_content)


if __name__ == "__main__":
    unittest.main()

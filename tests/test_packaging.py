# -*- coding: utf-8 -*-
"""Unit tests for ATIAF packaging, verification CLI, and release readiness (Phase P9)."""

from pathlib import Path
import sys
import unittest

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from atyaf_core.cli import run_diagnostics


class TestPackagingAndReleaseReadiness(unittest.TestCase):
    """Verifies packaging metadata, CLI diagnostics, documentation, and release files."""

    def test_pyproject_toml_structure(self):
        pyproject_path = PROJECT_ROOT / "pyproject.toml"
        self.assertTrue(pyproject_path.is_file(), "pyproject.toml is missing")

        # Parse with tomllib or basic checks
        try:
            import tomllib
            data = tomllib.loads(pyproject_path.read_text(encoding="utf-8"))
        except ImportError:
            try:
                import tomli as tomllib
                data = tomllib.loads(pyproject_path.read_text(encoding="utf-8"))
            except ImportError:
                data = None

        if data:
            self.assertEqual(data["project"]["name"], "atyaf")
            self.assertEqual(data["project"]["version"], "1.0.0")
            self.assertEqual(data["project"]["license"]["text"], "MIT")
            self.assertIn("atyaf-verify", data["project"]["scripts"])
            self.assertIn("numpy>=1.22.0", data["project"]["dependencies"])
            self.assertIn("rasterio>=1.3.0", data["project"]["dependencies"])
        else:
            text = pyproject_path.read_text(encoding="utf-8")
            self.assertIn('name = "atyaf"', text)
            self.assertIn('version = "1.0.0"', text)

    def test_run_diagnostics_cli(self):
        """Verifies that the CLI diagnostics utility runs and returns 0 errors."""
        res = run_diagnostics(verbose=False)
        self.assertEqual(res, 0, "run_diagnostics returned non-zero error count")

    def test_docs_index_html(self):
        index_path = PROJECT_ROOT / "docs" / "index.html"
        self.assertTrue(index_path.is_file(), "docs/index.html is missing")
        content = index_path.read_text(encoding="utf-8")
        self.assertIn("ATIAF", content)
        self.assertIn("أطياف", content)
        self.assertIn("01. Spectral Indices", content)
        self.assertIn("02. Surface Temperature", content)
        self.assertIn("03. Urban Heat Islands", content)
        self.assertIn("04. Environmental Drought", content)
        self.assertIn("05. Geological Analysis", content)
        self.assertIn("06. Temporal Change", content)

    def test_readme_and_changelog(self):
        readme_en = PROJECT_ROOT / "README.md"
        readme_ar = PROJECT_ROOT / "README.ar.md"
        changelog = PROJECT_ROOT / "CHANGELOG.md"

        self.assertTrue(readme_en.is_file())
        self.assertTrue(readme_ar.is_file())
        self.assertTrue(changelog.is_file())

        self.assertIn("1.0.0", readme_en.read_text(encoding="utf-8"))
        self.assertIn("1.0.0", readme_ar.read_text(encoding="utf-8"))
        self.assertIn("1.0.0", changelog.read_text(encoding="utf-8"))


if __name__ == "__main__":
    unittest.main()

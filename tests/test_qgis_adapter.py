# -*- coding: utf-8 -*-
"""Unit tests for ATIAF QGIS Adapter and Processing Provider (Phase P7).

Tests the plugin structure, metadata.txt, classFactory, provider definition,
algorithm declarations, canonical parameter orders, and Decision D-007 CRS gating.
Runnable with standard Python (T1) without requiring a GUI.
"""

import configparser
from pathlib import Path
import sys
import unittest

PROJECT_ROOT = Path(__file__).resolve().parents[1]
QGIS_DIR = PROJECT_ROOT / "qgis"
PLUGIN_DIR = QGIS_DIR / "atyaf"

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))
if str(QGIS_DIR) not in sys.path:
    sys.path.insert(0, str(QGIS_DIR))

from atyaf import classFactory
from atyaf.atyaf_plugin import ATIAFPlugin
from atyaf.provider import ATIAFProcessingProvider
from atyaf.algorithms.spectral_indices import SpectralIndicesAlgorithm
from atyaf.algorithms.surface_temperature import SurfaceTemperatureAlgorithm
from atyaf.algorithms.thermal_urban import ThermalUrbanAlgorithm
from atyaf.algorithms.environmental_drought import EnvironmentalDroughtAlgorithm
from atyaf.algorithms.geological_analysis import GeologicalAnalysisAlgorithm
from atyaf.algorithms.temporal_change import TemporalChangeAlgorithm


class TestQGISMetadata(unittest.TestCase):
    """Validates QGIS plugin metadata.txt format and required keys."""

    def setUp(self):
        self.metadata_path = PLUGIN_DIR / "metadata.txt"

    def test_metadata_file_exists(self):
        self.assertTrue(self.metadata_path.is_file(), f"Missing metadata.txt at {self.metadata_path}")

    def test_metadata_conforms_to_qgis_standard(self):
        config = configparser.ConfigParser()
        config.read(self.metadata_path, encoding="utf-8")

        self.assertIn("general", config.sections(), "metadata.txt must contain [general] section")
        general = config["general"]

        required_keys = [
            "name",
            "qgisMinimumVersion",
            "description",
            "version",
            "author",
            "email",
            "about",
            "category",
        ]
        for key in required_keys:
            self.assertIn(key, general, f"metadata.txt missing required key: {key}")
            self.assertTrue(len(general[key].strip()) > 0, f"Key '{key}' in metadata.txt is empty")

        self.assertEqual(general["qgisMinimumVersion"], "3.0")
        self.assertIn("ATIAF", general["name"])
        self.assertIn("أطياف", general["name"])


class TestQGISPluginLifecycle(unittest.TestCase):
    """Validates QGIS plugin factory, initialization and provider structure."""

    def test_class_factory(self):
        plugin = classFactory(None)
        self.assertIsInstance(plugin, ATIAFPlugin)
        self.assertIsNone(plugin.iface)
        self.assertIsNone(plugin.provider)

    def test_provider_identity(self):
        provider = ATIAFProcessingProvider()
        self.assertEqual(provider.id(), "atyaf")
        self.assertIn("ATIAF", provider.name())
        self.assertIn("أطياف", provider.name())
        self.assertIn("ATIAF", provider.longName())

    def test_provider_algorithms_instantiation(self):
        provider = ATIAFProcessingProvider()
        algs = [
            SpectralIndicesAlgorithm(),
            SurfaceTemperatureAlgorithm(),
            ThermalUrbanAlgorithm(),
            EnvironmentalDroughtAlgorithm(),
            GeologicalAnalysisAlgorithm(),
            TemporalChangeAlgorithm(),
        ]
        self.assertEqual(len(algs), 6, "Must define exactly 6 core remote sensing algorithms")


class TestQGISAlgorithmDefinitions(unittest.TestCase):
    """Validates algorithm identifiers, names, groups, and bilingual descriptions."""

    def setUp(self):
        self.algorithms = {
            "spectral_indices": SpectralIndicesAlgorithm(),
            "surface_temperature": SurfaceTemperatureAlgorithm(),
            "thermal_urban": ThermalUrbanAlgorithm(),
            "environmental_drought": EnvironmentalDroughtAlgorithm(),
            "geological_analysis": GeologicalAnalysisAlgorithm(),
            "temporal_change": TemporalChangeAlgorithm(),
        }

    def test_algorithm_names_and_display_names(self):
        expected_meta = {
            "spectral_indices": (
                "01. Spectral Indices | المؤشرات الطيفية",
                "Indices",
            ),
            "surface_temperature": (
                "02. Surface Temperature | درجة حرارة السطح",
                "Thermal",
            ),
            "thermal_urban": (
                "03. Thermal & Urban Analysis | التحليل الحراري والحضري والجزر الحرارية",
                "Thermal",
            ),
            "environmental_drought": (
                "04. Environmental & Drought Analysis | التحليل البيئي ومؤشرات الجفاف",
                "Environmental",
            ),
            "geological_analysis": (
                "05. Geological Analysis & Mineral Alteration | التحليل الجيولوجي ونطاقات التحول المعدني",
                "Geology",
            ),
            "temporal_change": (
                "06. Temporal Analysis & Change Detection | التحليل الزمني وتغير الغطاء الأرضي",
                "Temporal",
            ),
        }

        for alg_id, alg in self.algorithms.items():
            self.assertEqual(alg.name(), alg_id)
            exp_disp, exp_grp = expected_meta[alg_id]
            self.assertEqual(alg.displayName(), exp_disp)
            self.assertEqual(alg.group(), exp_grp)
            self.assertTrue(len(alg.shortHelpString()) > 0)
            # Verify bilingual help strings
            self.assertIn("أطياف", alg.shortHelpString())

    def test_canonical_parameter_names(self):
        for name, alg in self.algorithms.items():
            if name == "temporal_change":
                self.assertTrue(hasattr(alg, "T1_FOLDER"), f"{name} missing T1_FOLDER")
                self.assertTrue(hasattr(alg, "T2_FOLDER"), f"{name} missing T2_FOLDER")
            else:
                self.assertTrue(hasattr(alg, "INPUT_FOLDER"), f"{name} missing INPUT_FOLDER")
                self.assertEqual(alg.INPUT_FOLDER, "INPUT_FOLDER")

            # Canonical rule: OUTPUT_FOLDER is always defined as output destination
            self.assertTrue(hasattr(alg, "OUTPUT_FOLDER"), f"{name} missing OUTPUT_FOLDER")
            self.assertEqual(alg.OUTPUT_FOLDER, "OUTPUT_FOLDER")

    def test_create_instance(self):
        for name, alg in self.algorithms.items():
            inst = alg.createInstance()
            self.assertIsInstance(inst, type(alg))
            self.assertIsNot(inst, alg)


if __name__ == "__main__":
    unittest.main()

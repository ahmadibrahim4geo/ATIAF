"""Unit and structural tests for ATIAF scientific registries and repository layout.
Part of Phase P0 baseline validation.
"""
import json
import pathlib
import re
import unittest

ROOT = pathlib.Path(__file__).resolve().parents[1]

class TestRepositoryStructure(unittest.TestCase):
    def test_required_files_exist(self):
        required = [
            'AGENTS.md',
            'documentation/project/START_AGENT_PROMPT.txt',
            'PROJECT_STATE.md',
            'documentation/project/DECISIONS.md',
            'documentation/project/PROJECT_SPECIFICATION.md',
            'documentation/project/PROJECT_SPECIFICATION_AR.md',
            'documentation/project/DEVELOPMENT_ROADMAP.md',
            'documentation/project/DEVELOPMENT_ROADMAP_AR.md',
            'README.md',
            'README.ar.md',
            'LICENSE',
            'Development_Plans/INDEX.md',
            'Reports/INDEX.md',
            'development_resources/REPOSITORIES.md',
            'development_resources/SKILLS_REGISTRY.md',
            'development_resources/SOURCES.md',
            'scientific_library/sensors/sensor_registry.json',
            'scientific_library/indices/candidate_indices.json',
            'documentation/ar/SENSORS_AND_DOWNLOADS.md',
            'documentation/en/SENSORS_AND_DOWNLOADS.md',
            'documentation/ar/SCIENTIFIC_METHODS.md',
            'documentation/en/SCIENTIFIC_METHODS.md',
        ]
        for f in required:
            target = ROOT / f
            self.assertTrue(target.is_file(), f"Missing required file: {f}")

    def test_json_files_well_formed(self):
        json_files = [p for p in ROOT.rglob('*.json') if '.agent_resources' not in p.relative_to(ROOT).parts]
        self.assertGreater(len(json_files), 0, "No JSON files found to validate")
        for jf in json_files:
            try:
                data = json.loads(jf.read_text(encoding='utf-8'))
                self.assertIsNotNone(data, f"JSON in {jf} is empty or None")
            except Exception as e:
                self.fail(f"Invalid JSON syntax in {jf.relative_to(ROOT)}: {e}")

    def test_no_broken_local_markdown_links(self):
        from tools.link_validation import broken_links
        self.assertEqual(broken_links(), [])



class TestScientificRegistries(unittest.TestCase):
    def test_candidate_indices(self):
        path = ROOT / 'scientific_library' / 'indices' / 'candidate_indices.json'
        self.assertTrue(path.is_file())
        data = json.loads(path.read_text(encoding='utf-8'))
        self.assertIn('items', data)
        items = data['items']
        self.assertGreater(len(items), 0)

        ids = [item['id'] for item in items]
        self.assertEqual(len(ids), len(set(ids)), "Duplicate index IDs found in candidate_indices.json")

        for item in items:
            self.assertEqual(
                item.get('status'), 'CANDIDATE_UNVERIFIED',
                f"Index {item.get('id')} has premature status claim: {item.get('status')}"
            )
            self.assertIn('name_en', item)
            self.assertIn('category', item)
            self.assertIn('formula', item)
            self.assertIn('band_roles', item)

    def test_sensor_registry(self):
        path = ROOT / 'scientific_library' / 'sensors' / 'sensor_registry.json'
        self.assertTrue(path.is_file())
        data = json.loads(path.read_text(encoding='utf-8'))
        self.assertIn('sensors', data)
        sensors = data['sensors']
        self.assertGreater(len(sensors), 0)

        sensor_ids = [s['id'] for s in sensors]
        self.assertEqual(len(sensor_ids), len(set(sensor_ids)), "Duplicate sensor IDs found in sensor_registry.json")

        for s in sensors:
            self.assertEqual(
                s.get('implementation_status'), 'PLANNED_NOT_TESTED',
                f"Sensor {s.get('id')} has premature implementation status: {s.get('implementation_status')}"
            )
            self.assertIn('platform', s)
            self.assertIn('instrument', s)
            self.assertIn('modality', s)
            self.assertIn('preferred_products', s)
            self.assertIn('available_roles', s)


class TestEnvironmentLibraries(unittest.TestCase):
    def test_geospatial_packages_available(self):
        """Verifies core standalone Python libraries needed for headless calculations."""
        import numpy
        import rasterio
        import shapely
        import geopandas
        import pyproj

        self.assertTrue(hasattr(numpy, '__version__'))
        self.assertTrue(hasattr(rasterio, '__version__'))
        self.assertTrue(hasattr(shapely, '__version__'))
        self.assertTrue(hasattr(geopandas, '__version__'))
        self.assertTrue(hasattr(pyproj, '__version__'))


if __name__ == '__main__':
    unittest.main()

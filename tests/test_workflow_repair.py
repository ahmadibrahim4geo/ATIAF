"""Behavioral regression evidence for PLAN-0015; fixture tests are T1."""
import hashlib
import importlib.util
import json
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch
from types import SimpleNamespace
import rasterio
from shapely.geometry import Polygon
from atiaf_core.workflow import run_tool, discover, unavailable_reason
from atiaf_core.tool_contract import CATALOG, title
from workflow_fixture import make_scene

ROOT = Path(__file__).resolve().parents[1]


class TestWorkflowRepair(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name).resolve()
        self.scene = make_scene(self.root)

    def tearDown(self):
        self.temp.cleanup()

    def run_spectral(self, **kwargs):
        return run_tool('spectral_indices', self.scene, ['NDVI'], **kwargs)

    def test_default_destination_and_immutable_reruns(self):
        first = Path(self.run_spectral(output_folder=self.scene)['OUTPUT_RASTERS'][0])
        before = hashlib.sha256(first.read_bytes()).hexdigest()
        second = Path(self.run_spectral()['OUTPUT_RASTERS'][0])
        self.assertNotEqual(first, second)
        self.assertEqual(before, hashlib.sha256(first.read_bytes()).hexdigest())
        self.assertTrue(first.is_relative_to(self.scene / 'Results'))
        self.assertTrue(first.is_relative_to(self.scene / 'Results' / 'Spectral_Indices'))
        self.assertFalse((self.scene / self.scene.name).exists())

    def test_quality_nodata_and_saturation(self):
        with rasterio.open(self.run_spectral()['OUTPUT_RASTERS'][0]) as ds:
            data = ds.read(1, masked=True)
            self.assertTrue(data.mask[0, 0])
            self.assertTrue(data.mask[0, 1])
            self.assertTrue(data.mask[0, 2])
            self.assertAlmostEqual(float(data[1, 1]), 2/3, places=3)

    def test_raw_dn_valid_range_is_applied(self):
        path = next(self.scene.glob('*SR_B5.TIF'))
        with rasterio.open(path, 'r+') as ds:
            data = ds.read(1)
            data[2,2] = 65535
            ds.write(data,1)
        with rasterio.open(self.run_spectral()['OUTPUT_RASTERS'][0]) as ds:
            self.assertTrue(ds.read(1, masked=True).mask[2,2])

    def test_auto_profile_rejects_potential_double_scaling(self):
        path = next(self.scene.glob('*SR_B5.TIF'))
        with rasterio.open(path) as ds:
            profile = ds.profile.copy()
        profile.update(dtype='float32')
        import numpy as np
        with rasterio.open(path, 'w', **profile) as ds:
            ds.write(np.full((16,16), .5, dtype='float32'),1)
        with self.assertRaisesRegex(ValueError, 'double calibration'):
            self.run_spectral()

    def test_actual_crs_reprojection(self):
        with rasterio.open(self.run_spectral(output_crs='EPSG:32635')['OUTPUT_RASTERS'][0]) as ds:
            self.assertEqual(ds.crs.to_epsg(), 32635)
            self.assertNotAlmostEqual(ds.bounds.left, 300000)

    def test_polygon_clip_independent_of_mosaic(self):
        polygon = Polygon([(300000, 3300000), (300480, 3300000), (300000, 3299520)])
        with rasterio.open(self.run_spectral(aoi_geometry=polygon, aoi_crs='EPSG:32636')['OUTPUT_RASTERS'][0]) as ds:
            data = ds.read(1, masked=True)
            self.assertTrue(data.mask[-1, -1])
            self.assertFalse(data.mask[2, 2])

    def test_empty_selection_fails_without_outputs(self):
        with self.assertRaisesRegex(ValueError, 'Select at least one'):
            run_tool('spectral_indices', self.scene, [])
        self.assertFalse((self.scene / 'Results').exists())

    def test_sensor_mismatch_fails_without_outputs(self):
        with self.assertRaisesRegex(ValueError, 'mismatch'):
            self.run_spectral(sensor='SENTINEL_2_L2A')
        self.assertFalse((self.scene / 'Results').exists())

    def test_degrees_and_feet_rejected(self):
        for crs in ['EPSG:4326', 'EPSG:2227']:
            with self.subTest(crs=crs), self.assertRaisesRegex(ValueError, 'D-007'):
                self.run_spectral(output_crs=crs)

    def test_invalid_aoi_does_not_silently_process_full_extent(self):
        with self.assertRaisesRegex(ValueError, 'AOI'):
            self.run_spectral(aoi_geometry=Polygon())
        self.assertFalse((self.scene / 'Results').exists())

    def test_missing_qa_explicit_optout(self):
        next(self.scene.glob('*QA_PIXEL*')).unlink()
        with self.assertRaisesRegex(ValueError, 'quality mask'):
            self.run_spectral()
        self.assertTrue(self.run_spectral(apply_qa=False)['OUTPUT_RASTERS'])

    def test_physics_gates_show_reasons(self):
        sc = discover(self.scene)[0]
        for tool, calc in [('environmental_drought', 'TVDI'), ('thermal_urban', 'SUHI'),
                           ('spectral_indices', 'TCB'), ('environmental_drought', 'ALBEDO')]:
            with self.subTest(calc=calc):
                self.assertTrue(unavailable_reason(tool, calc, sc))
                with self.assertRaises(ValueError):
                    run_tool(tool, self.scene, [calc])

    def test_temperature_unit_and_urban_selection(self):
        result = run_tool('surface_temperature', self.scene, ['LST_CELSIUS'])
        with rasterio.open(result['OUTPUT_RASTERS'][0]) as ds:
            self.assertAlmostEqual(float(ds.read(1)[1, 1]), 44017 * .00341802 + 149 - 273.15, places=3)
        urban = run_tool('thermal_urban', self.scene, ['HOTSPOTS'])
        self.assertEqual(len(urban['OUTPUT_RASTERS']), 1)
        with rasterio.open(urban['OUTPUT_RASTERS'][0]) as ds:
            self.assertEqual(ds.nodata, 255)
            self.assertEqual(ds.read(1)[1, 1], 0)  # zero remains valid non-hotspot

    def test_environment_and_geology(self):
        l7 = make_scene(self.root, 'l7', platform=7)
        self.assertTrue(run_tool('environmental_drought', l7, ['ALBEDO'])['OUTPUT_RASTERS'])
        geo = run_tool('geological_analysis', self.scene, ['IRON_OXIDE'])
        with rasterio.open(geo['OUTPUT_RASTERS'][0]) as ds:
            self.assertGreater(float(ds.read(1)[1, 1]), 1)

    def test_temporal_computes_selected_metric(self):
        second = make_scene(self.root, 'later', date='2023-06-20', red_dn=12000)
        result = run_tool('temporal_change', self.scene, ['NDVI'], second_folder=second)
        self.assertEqual(len(result['OUTPUT_RASTERS']), 1)
        with rasterio.open(result['OUTPUT_RASTERS'][0]) as ds:
            self.assertLess(float(ds.read(1)[1, 1]), 0)

    def test_cross_date_mosaic_rejected(self):
        make_scene(self.root, 'later', date='2023-06-20')
        with self.assertRaisesRegex(ValueError, 'acquisition day'):
            run_tool('spectral_indices', self.root, ['NDVI'], mosaic=True)

    def test_same_date_mosaic_and_prior_outputs_preserved(self):
        make_scene(self.root, 'adjacent')
        first = run_tool('spectral_indices', self.root, ['NDVI'], mosaic=True)
        hashes = {p: hashlib.sha256(Path(p).read_bytes()).hexdigest() for p in first['OUTPUT_RASTERS']}
        second = run_tool('spectral_indices', self.root, ['NDVI'], mosaic=True)
        self.assertEqual(len(first['OUTPUT_RASTERS']), 3)
        self.assertFalse(set(first['OUTPUT_RASTERS']) & set(second['OUTPUT_RASTERS']))
        self.assertEqual(hashes, {p: hashlib.sha256(Path(p).read_bytes()).hexdigest() for p in hashes})

    def test_manifest_includes_exact_sources_and_options(self):
        result = self.run_spectral(output_crs='EPSG:32636')
        manifest = json.loads((Path(result['RUN_MANIFESTS'][0])/'Processing_Manifest.json').read_text('utf-8'))
        self.assertIn('source_scene', manifest)
        self.assertEqual(manifest['requested_calculations'], ['NDVI'])
        self.assertEqual(manifest['source_scene']['bands']['red']['scale_factor'], .0000275)
        run_dir = Path(result['RUN_MANIFESTS'][0])
        self.assertIn('lang="ar" dir="rtl"', (run_dir/'report.ar.html').read_text('utf-8'))
        self.assertIn('lang="en" dir="ltr"', (run_dir/'report.en.html').read_text('utf-8'))

    def mapping_file(self):
        data = dict(scene_id='EXPERT_SCENE', platform='Landsat 8', instrument='OLI_TIRS',
                    sensor_family='Landsat', product_level='L2_SR', acquisition_date='2023-05-20', bands={})
        for role, band, wavelength in [('red',4,655), ('nir',5,865)]:
            data['bands'][role] = dict(file=next(self.scene.glob(f'*SR_B{band}.TIF')).name,
                                      scale=.0000275, offset=-.2, unit='reflectance', wavelength_nm=wavelength,
                                      provenance='Synthetic fixture explicit calibration')
        path = self.root/'expert.json'
        path.write_text(json.dumps(data), 'utf-8')
        return path, data

    def test_expert_mapping_is_executed_and_recorded(self):
        path, _ = self.mapping_file()
        result = self.run_spectral(sensor='EXPERT', expert_mapping=path, apply_qa=False)
        with rasterio.open(result['OUTPUT_RASTERS'][0]) as ds:
            self.assertAlmostEqual(float(ds.read(1)[1,1]), 2/3, places=3)
        record = json.loads((Path(result['RUN_MANIFESTS'][0])/'Processing_Manifest.json').read_text('utf-8'))
        self.assertTrue(record['source_scene']['expert_mapped'])
        self.assertEqual(record['source_scene']['bands']['nir']['calibration_provenance'], 'Synthetic fixture explicit calibration')

    def test_expert_invalid_wavelength_and_traversal_are_rejected(self):
        path, data = self.mapping_file()
        data['bands']['nir']['wavelength_nm'] = 50
        path.write_text(json.dumps(data), 'utf-8')
        with self.assertRaisesRegex(ValueError, 'Wavelength'):
            self.run_spectral(sensor='EXPERT', expert_mapping=path, apply_qa=False)
        data['bands']['nir']['wavelength_nm'] = 865
        data['bands']['nir']['file'] = '../../escape.tif'
        path.write_text(json.dumps(data), 'utf-8')
        with self.assertRaisesRegex(ValueError, 'inside the input scene'):
            self.run_spectral(sensor='EXPERT', expert_mapping=path, apply_qa=False)

    def test_cancellation_preserves_sources_and_leaves_no_partial_raster(self):
        calls = []
        def canceled():
            calls.append(1)
            return len(calls) >= 2
        with self.assertRaises(InterruptedError):
            self.run_spectral(canceled=canceled)
        self.assertFalse(list((self.scene/'Results').rglob('*.tif')))
        self.assertTrue(list(self.scene.glob('*SR_B4.TIF')))

    def test_unsafe_metadata_scene_id_is_rejected(self):
        path = next(self.scene.glob('*MTL.txt'))
        content = path.read_text('utf-8')
        import re
        content = re.sub(r'LANDSAT_PRODUCT_ID = ".*"', 'LANDSAT_PRODUCT_ID = "../../escape"', content)
        path.write_text(content, 'utf-8')
        with self.assertRaisesRegex(ValueError, 'unsafe filename'):
            self.run_spectral()

    def test_missing_dependencies_do_not_erase_arcgis_calculations(self):
        import subprocess
        script = '''import sys,builtins
from pathlib import Path
from types import SimpleNamespace
sys.path.insert(0, 'ArcGIS Pro Tools')
original=builtins.__import__
def guarded(name,*args,**kwargs):
    if name.split('.')[0] in ('numpy','rasterio','shapely','pyproj'):
        raise ImportError('Deliberately absent science dependency')
    return original(name,*args,**kwargs)
builtins.__import__=guarded
class P:
    def __init__(self,**kw):
        self.__dict__.update(kw);self.filter=SimpleNamespace(list=[],type=None)
sys.modules['arcpy']=SimpleNamespace(Parameter=P)
from atiaf_arcgis import NativeTool
from atiaf_core.tool_contract import TITLES
for key in TITLES:
    tool=NativeTool.__new__(NativeTool);tool.tool_id=key
    params=tool.getParameterInfo()
    assert any(p.name.startswith('calc_') for p in params),key
print('Six calculation lists remain visible without scientific libraries')
'''
        result = subprocess.run([sys.executable, '-c', script], cwd=ROOT, capture_output=True, text=True, timeout=20)
        self.assertEqual(result.returncode, 0, result.stderr)


class FakeParameter:
    def __init__(self, **kwargs):
        self.__dict__.update(kwargs)
        self.filter = SimpleNamespace(type=None, list=[])
        self.value, self.enabled, self.altered = None, True, False
    @property
    def valueAsText(self):
        return str(self.value) if self.value is not None else None
    def clearMessage(self):
        self.message = ''
    def setErrorMessage(self, message):
        self.message = message
    setWarningMessage = setErrorMessage


class TestNativeDialogContractWithDouble(unittest.TestCase):
    def test_six_tools_order_empty_defaults_and_language(self):
        # Explicit T1 ArcPy double; does not prove the Pro UI works.
        fake = SimpleNamespace(Parameter=FakeParameter)
        sys.path.insert(0, str(ROOT/'ArcGIS Pro Tools'))
        with patch.dict(sys.modules, {'arcpy': fake}):
            sys.modules.pop('atiaf_arcgis', None)
            for filename, lang in [('ATIAF.pyt', 'en'), ('ATIAF_AR.pyt', 'ar')]:
                path = ROOT/'ArcGIS Pro Tools'/filename
                ns = {'__file__': str(path)}
                exec(compile(path.read_text('utf-8'), str(path), 'exec'), ns)
                for cls in ns['Toolbox']().tools:
                    params = cls().getParameterInfo()
                    self.assertEqual(params[0].name, 'sensor_product')
                    self.assertEqual(params[1].name, 'input_folder')
                    self.assertEqual(params[-1].name, 'output_folder')
                    checks = [p for p in params if p.name.startswith('calc_')]
                    self.assertTrue(checks)
                    self.assertTrue(all(p.value is False for p in checks))
                    self.assertEqual(cls().label, title(cls.tool_id, lang))
        sys.modules.pop('atiaf_arcgis', None)

    def test_no_duplicate_implementation_package(self):
        self.assertFalse((ROOT/'atyaf_core').exists())
        self.assertTrue((ROOT/'atiaf_core'/'indices'/'engine.py').is_file())

"""Independent numerics and real raster readback for the consolidated native contracts."""
from pathlib import Path
import json
import tempfile
import unittest
import numpy as np
import rasterio
from workflow_fixture import make_scene
from atiaf_core.workflow import run_tool, discover
from atiaf_core.classification import scheme, classify
from atiaf_core.temperature.ndvi_retrieval import retrieve, validate


class ConsolidatedChanges(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(prefix='atiaf_r6_')
        self.root = Path(self.tmp.name)
        self.scene = make_scene(self.root)
    def tearDown(self):
        self.tmp.cleanup()
    def raster(self, path, values, reference=None):
        with rasterio.open(reference or next(self.scene.glob('*SR_B4.TIF'))) as ds:
            profile = dict(ds.profile, dtype='float32', nodata=-9999)
        array = np.broadcast_to(np.array(values, dtype='float32'), (16,16)).copy()
        with rasterio.open(path, 'w', **profile) as ds:
            ds.write(array,1)
        return path
    def manual(self):
        folder = self.root/'no_header'; folder.mkdir()
        red = self.raster(folder/'red.tif', 0.1)
        nir = self.raster(folder/'nir.tif', 0.5)
        return folder, dict(manual_mode=True, manual_platform='LANDSAT_8', manual_date='2023-05-20',
            manual_provenance='Synthetic calibrated reflectance fixture', manual_scale=1, manual_offset=0,
            band_red=str(red), band_nir=str(nir))
    def test_manual_red_nir_only_and_missing_blue(self):
        folder, options = self.manual()
        result = run_tool('spectral_indices', folder, ['NDVI'], sensor='LANDSAT_8_9_C2_L2', apply_qa=False, options=options)
        with rasterio.open(result['OUTPUT_RASTERS'][0]) as ds:
            self.assertAlmostEqual(float(ds.read(1)[1,1]), 2/3, places=5)
        with self.assertRaisesRegex(ValueError, 'Missing physical band: blue'):
            run_tool('spectral_indices', folder, ['EVI'], sensor='LANDSAT_8_9_C2_L2', apply_qa=False, options=options)
    def test_manual_requires_actual_sensor_and_calibration(self):
        folder, options = self.manual()
        with self.assertRaisesRegex(ValueError, 'actual sensor'):
            discover(folder, manual_options=options)
        options['manual_scale'] = None
        with self.assertRaisesRegex(ValueError, 'calibration'):
            discover(folder, 'LANDSAT_8_9_C2_L2', manual_options=options)
        self.assertFalse((folder/'Results').exists())
    def test_manual_mapping_export_import_and_sensor_mismatch(self):
        folder,options=self.manual()
        result=run_tool('spectral_indices',folder,['NDVI'],sensor='LANDSAT_8_9_C2_L2',apply_qa=False,options=options)
        saved=Path(result['RUN_MANIFESTS'][0])/'Manual_Band_Mapping.json'
        self.assertTrue(saved.is_file())
        restored=dict(manual_mode=True,expert_mapping=str(saved))
        repeated=run_tool('spectral_indices',folder,['NDVI'],sensor='LANDSAT_8_9_C2_L2',apply_qa=False,options=restored)
        self.assertNotEqual(result['OUTPUT_RASTERS'],repeated['OUTPUT_RASTERS'])
        with self.assertRaisesRegex(ValueError,'does not match'):
            discover(folder,'SENTINEL_2_L2A',manual_options=restored)
    def test_manual_qa_is_optional_only_by_explicit_optout(self):
        folder, options = self.manual()
        with self.assertRaisesRegex(ValueError, 'quality mask'):
            run_tool('spectral_indices', folder, ['NDVI'], sensor='LANDSAT_8_9_C2_L2', options=options)
        self.assertFalse((folder/'Results').exists())
    def test_additional_index_independent_pixels(self):
        folder, options = self.manual()
        result = run_tool('spectral_indices', folder, ['EVI2','NIRv'], sensor='LANDSAT_8_9_C2_L2', apply_qa=False, options=options)
        expected = [2.5*0.4/(0.5+2.4*0.1+1), 0.5*2/3]
        for path, number in zip(result['OUTPUT_RASTERS'], expected):
            with rasterio.open(path) as ds:
                self.assertAlmostEqual(float(ds.read(1)[2,2]), number, places=5)
    def thermal(self):
        options = dict(ndvi_assisted=True, planck_k1=774.8853, planck_k2=1321.0789,
            transmittance=0.8, upwelling=1.2, downwelling=1.8, ndvi_soil=0.2, ndvi_vegetation=0.5,
            emissivity_soil=0.97, emissivity_vegetation=0.99,
            retrieval_provenance='Synthetic same-scene calibrated radiance/NDVI; locally supplied atmosphere/emissivity assumptions')
        ndvi, temperature = 0.4, 310
        pv = ((ndvi-0.2)/(0.5-0.2))**2
        epsilon = 0.97*(1-pv)+0.99*pv
        blackbody = options['planck_k1']/np.expm1(options['planck_k2']/temperature)
        at_sensor = options['transmittance']*(epsilon*blackbody+(1-epsilon)*options['downwelling'])+options['upwelling']
        options['radiance_file'] = str(self.raster(self.scene/'local_radiance.tif',at_sensor))
        options['ndvi_file'] = str(self.raster(self.scene/'local_ndvi.tif',ndvi))
        return options, temperature
    def test_rte_independent_forward_inverse(self):
        options, temperature = self.thermal()
        with rasterio.open(options['radiance_file']) as ds:
            radiance = ds.read(1)
        values = retrieve(np.full((16,16),0.4),radiance,validate(options))
        np.testing.assert_allclose(values, temperature, atol=0.0001)
    def test_rte_native_raster_pipeline_kelvin_celsius(self):
        options, expected = self.thermal()
        for unit, value in [('Celsius',expected-273.15),('Kelvin',expected)]:
            result = run_tool('surface_temperature', self.scene, ['LST'], options=dict(options,temperature_unit=unit))
            with rasterio.open(result['OUTPUT_RASTERS'][0]) as ds:
                arr=ds.read(1); self.assertAlmostEqual(float(arr[1,1]),value,places=3)
                self.assertEqual(arr[0,0],ds.nodata)
            params=json.loads((Path(result['RUN_MANIFESTS'][0])/'Parameters.json').read_text('utf-8'))
            self.assertIn('equation',params)
    def test_rte_no_automatic_default_inputs(self):
        options, _ = self.thermal(); options['transmittance']=None
        with self.assertRaisesRegex(ValueError,'transmittance'):
            run_tool('surface_temperature',self.scene,['LST'], options=options)
        self.assertFalse((self.scene/'Results').exists())
    def test_rte_computed_ndvi_and_optical_sensor_rejection(self):
        options,_=self.thermal(); options.pop('ndvi_file')
        result=run_tool('surface_temperature',self.scene,['LST'],options=options)
        self.assertTrue(Path(result['OUTPUT_RASTERS'][0]).is_file())
        source=discover(self.scene)[0]
        from atiaf_core.discovery.models import SensorFamily
        source.metadata.sensor_family=SensorFamily.SENTINEL_2
        with self.assertRaisesRegex(ValueError,'optical-only'):
            validate(options,source)
    def test_rte_refuses_official_st_as_radiance(self):
        options,_=self.thermal(); options['radiance_file']=str(next(self.scene.glob('*ST_B10.TIF')))
        with self.assertRaisesRegex(ValueError,'L2 ST'):
            run_tool('surface_temperature',self.scene,['LST'], options=options)
    def test_rte_negative_ndvi_not_assumed_water(self):
        options,_=self.thermal()
        arr=retrieve(np.array([-.1,1.1,.4]),np.array([10.,10.,10.]),validate(options))
        self.assertTrue(np.isnan(arr[:2]).all()); self.assertTrue(np.isfinite(arr[2]))
    def test_local_class_boundaries_and_nodata(self):
        effective=scheme(dict(ndvi_breaks='0.25,0.5,0.75',classification_basis='Independent local sample interpretation'))
        arr=np.array([-.1,np.nan,0,.249,.25,.5,.75,1,1.1])
        np.testing.assert_array_equal(classify(arr,effective),[0,0,1,1,2,3,4,4,0])
        self.assertEqual(effective['original_breaks'],[.2,.4,.6])
    def test_local_classes_require_order_and_basis(self):
        for text in ['0.4,0.2,0.6','0.2,0.2,0.6','nan,0.4,0.6','0.2,0.4,1','0.2,0.4']:
            with self.subTest(text=text),self.assertRaises(ValueError):
                scheme(dict(ndvi_breaks=text,classification_basis='fixture'))
        with self.assertRaisesRegex(ValueError,'local justification'):
            scheme({})
    def test_classification_outputs_and_reports_preserve_continuous(self):
        result=run_tool('spectral_indices',self.scene,['NDVI'],options=dict(classify_ndvi=True,
            ndvi_breaks='0.25,0.5,0.75',classification_basis='Synthetic boundary/readback fixture, not field validation'))
        self.assertEqual(len(result['OUTPUT_RASTERS']),2)
        original,classes=map(Path,result['OUTPUT_RASTERS'])
        with rasterio.open(original) as raw,rasterio.open(classes) as cls:
            self.assertAlmostEqual(float(raw.read(1)[1,1]),2/3,places=3)
            self.assertEqual(cls.read(1)[1,1],3)
            self.assertEqual(cls.read(1)[0,0],0)
        effective=json.loads(classes.with_suffix('.legend.json').read_text('utf-8'))
        self.assertEqual(effective['effective_breaks'],[.25,.5,.75])
        class_run=Path(result['RUN_MANIFESTS'][-1])
        for lang in ('en','ar'):
            page=(class_run/f'report.{lang}.html').read_text('utf-8')
            self.assertIn(effective['labels'][lang][2],page)
    def test_interpretation_coverage_and_language_independence(self):
        from atiaf_core.tool_contract import CATALOG
        for tool,rows in CATALOG.items():
            for row in rows:
                with self.subTest(tool=tool,id=row['id']):
                    item=row['interpretation']
                    for lang in ('en','ar'):
                        self.assertTrue(all(item[lang][key] for key in ('meaning','range','units','caution')))
                    self.assertIn('STANDARD',item['classification_status'])
        self.assertIn('No universal fixed',CATALOG['spectral_indices'][-2]['interpretation']['en']['range'])
    def test_generated_catalogs_retain_interpretation_and_local_class_warning(self):
        root=Path(__file__).resolve().parents[1]
        for lang,warning in [('en','NOT an international standard'),('ar','وليست معيارًا دوليًا')]:
            text=(root/'documentation'/lang/'INDICATORS_CATALOG.md').read_text('utf-8')
            self.assertIn(warning,text)
            self.assertIn('EVI2',text)
            self.assertIn('NIRv',text)
            self.assertIn('[0, 0.2)',text)
            self.assertIn('[0.6, 1]',text)
            self.assertIn('0.2–0.3',text)


if __name__=='__main__': unittest.main(verbosity=2)

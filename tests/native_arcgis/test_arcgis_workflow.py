"""Native ArcGIS Pro geoprocessing evidence on synthetic products, not real scene validation."""
from pathlib import Path
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT/'tests'))
import arcpy
import rasterio
from workflow_fixture import make_scene


class TestArcGISNativeWorkflow(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        arcpy.ImportToolbox(str(ROOT/'ArcGIS Pro Tools'/'ATIAF.pyt'))

    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix='atiaf_pro_')
        self.scene = make_scene(self.temp.name)

    def tearDown(self):
        self.temp.cleanup()

    def test_all_six_native_parameters(self):
        for tool in ['SpectralIndicesTool','SurfaceTemperatureTool','ThermalUrbanTool',
                     'EnvironmentalDroughtTool','GeologicalAnalysisTool','TemporalChangeTool']:
            params = arcpy.GetParameterInfo(tool + '_atiaf')
            self.assertEqual(params[0].name, 'sensor_product')
            self.assertEqual(params[1].name, 'input_folder')
            self.assertEqual(params[-1].name, 'output_folder')
            checks = [p for p in params if p.name.startswith('calc_')]
            self.assertTrue(checks, tool)
            self.assertTrue(all(str(p.value).lower() in ('false','none') for p in checks))

    def test_spectral_execution_and_crs(self):
        arcpy.atiaf.SpectralIndicesTool(input_folder=str(self.scene), calc_NDVI=True,
                                        output_crs=arcpy.SpatialReference(32635), add_to_map=False)
        paths = list((self.scene/'Results').rglob('*.tif'))
        self.assertEqual(len(paths), 1)
        with rasterio.open(paths[0]) as ds:
            self.assertEqual(ds.crs.to_epsg(), 32635)

    def test_temperature_and_geology_execution(self):
        arcpy.atiaf.SurfaceTemperatureTool(input_folder=str(self.scene), calc_LST=True, temperature_unit='Celsius')
        arcpy.atiaf.GeologicalAnalysisTool(input_folder=str(self.scene), calc_IRON_OXIDE=True)
        self.assertEqual(len(list((self.scene/'Results').rglob('*.tif'))), 2)

    def test_empty_and_mismatch_are_errors(self):
        with self.assertRaises(arcpy.ExecuteError):
            arcpy.atiaf.SpectralIndicesTool(input_folder=str(self.scene))
        with self.assertRaises(arcpy.ExecuteError):
            arcpy.atiaf.SpectralIndicesTool(input_folder=str(self.scene), sensor_product='SENTINEL_2_L2A', calc_NDVI=True)
        self.assertFalse((self.scene/'Results').exists())

    def test_urban_environment_and_temporal_execution(self):
        arcpy.atiaf.ThermalUrbanTool(input_folder=str(self.scene), calc_HOTSPOTS=True)
        l7 = make_scene(self.temp.name, 'l7', platform=7)
        arcpy.atiaf.EnvironmentalDroughtTool(input_folder=str(l7), calc_ALBEDO=True)
        later = make_scene(self.temp.name, 'later', date='2023-06-20', red_dn=12000)
        arcpy.atiaf.TemporalChangeTool(input_folder=str(self.scene), second_folder=str(later), calc_NDVI=True)
        self.assertTrue(list((l7/'Results').rglob('*ALBEDO*.tif')))
        self.assertTrue(list((self.scene/'Results'/'Temporal_Change').rglob('*.tif')))

    def test_arabic_toolbox_parameter_labels(self):
        arcpy.ImportToolbox(str(ROOT/'ArcGIS Pro Tools'/'ATIAF_AR.pyt'))
        params = arcpy.GetParameterInfo('SpectralIndicesTool_atiaf_ar')
        self.assertIn('المستشعر', params[0].displayName)
        self.assertEqual(params[-1].name, 'output_folder')

    def test_manual_inputs_groups_and_optional_classes(self):
        params = {p.name:p for p in arcpy.GetParameterInfo('SpectralIndicesTool_atiaf')}
        self.assertNotIn('search', params)
        self.assertEqual(params['input_folder'].displayName, 'Input Data Folder')
        self.assertIn('band_red',params)
        self.assertIn('band_nir',params)
        self.assertNotEqual(params['calc_NDVI'].category,params['calc_MNDWI'].category)
        from test_consolidated_changes import ConsolidatedChanges
        fixture=ConsolidatedChanges(); fixture.setUp()
        try:
            folder,options=fixture.manual()
            arcpy.atiaf.SpectralIndicesTool(input_folder=str(folder),sensor_product='LANDSAT_8_9_C2_L2',
                calc_NDVI=True, calc_EVI2=True, calc_NIRv=True, apply_qa_mask=False, classify_ndvi=True, classification_basis='Synthetic native Pro fixture', **options)
            classes=list((folder/'Results').rglob('*LOCAL_CLASSES*.tif'))
            self.assertEqual(len(classes),1)
            with rasterio.open(classes[0]) as saved:
                self.assertEqual(saved.count,1)
                self.assertEqual(saved.dtypes[0],'uint8')
                self.assertTrue(set(saved.read(1).ravel()) <= {0,1,2,3,4,255})
        finally:
            fixture.tearDown()

    def test_ndvi_assisted_temperature(self):
        from test_consolidated_changes import ConsolidatedChanges
        fixture=ConsolidatedChanges(); fixture.setUp()
        try:
            options,expected=fixture.thermal()
            arcpy.atiaf.SurfaceTemperatureTool(input_folder=str(fixture.scene),calc_LST=True,temperature_unit='Kelvin',**options)
            paths=list((fixture.scene/'Results').rglob('*LST_NDVI_RTE_KELVIN*.tif'))
            self.assertEqual(len(paths),1)
            with rasterio.open(paths[0]) as ds:
                self.assertAlmostEqual(float(ds.read(1)[1,1]),expected,places=3)
        finally: fixture.tearDown()


if __name__ == '__main__':
    unittest.main(verbosity=2)

"""Independent numeric, preservation, exact-band and RGB workflow acceptance fixtures."""
import json
from pathlib import Path
import tempfile
import unittest
import numpy as np
import rasterio
from shapely.geometry import Polygon

from workflow_fixture import make_scene
from atiaf_core.workflow import run_tool
from atiaf_core.composites.engine import validate_request, scientific_id
from atiaf_core.composites.expressions import calculate, parse
from atiaf_core.composites import render


class TestGeologicalComposites(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory(prefix='atiaf_rgb_test_')
        self.root=Path(self.temp.name)
        self.scene=make_scene(self.root)
    def tearDown(self): self.temp.cleanup()
    def run_rgb(self,methods=None,**kwargs):
        return run_tool('geological_composites',self.scene,methods or ['DIRECT_RGB','RATIO_RGB'],**kwargs)

    def test_direct_and_ratio_independent_reference_values_and_masks(self):
        result=self.run_rgb()
        with rasterio.open(result['OUTPUT_RASTERS'][0]) as ds:
            self.assertEqual(ds.count,3)
            np.testing.assert_allclose(ds.read()[:,2,2],[14000*.0000275-.2,25455*.0000275-.2,12000*.0000275-.2],rtol=1e-6)
            self.assertEqual(ds.descriptions,('B7','B5','B3'))
            self.assertEqual(ds.colorinterp[0].name,'red')
            for x in (0,1,2): self.assertTrue(np.all(ds.read_masks()[:,0,x]==0))
        b2,b4,b5,b6,b7=[v*.0000275-.2 for v in (10000,10909,25455,15000,14000)]
        with rasterio.open(result['OUTPUT_RASTERS'][1]) as ds:
            np.testing.assert_allclose(ds.read()[:,2,2],[b6/b7,b6/b2,(b4/b5)*(b6/b5)],rtol=1e-6)

    def test_second_published_ratio_variant(self):
        result=self.run_rgb(['RATIO_RGB'],options={'ratio_preset':'L89_CRC2'})
        r,b,s1,s2=[v*.0000275-.2 for v in (10909,10000,15000,14000)]
        with rasterio.open(result['OUTPUT_RASTERS'][0]) as ds:
            np.testing.assert_allclose(ds.read()[:,2,2],[r/s1,r/b,s1/s2],rtol=1e-6)

    def test_arithmetic_rejects_executable_content(self):
        for value in ('__import__("os")','B6.__class__','B6[0]','B6**2','B99/B2','True+B2'):
            with self.subTest(value=value), self.assertRaises(ValueError): parse(value)

    def test_zero_near_zero_nonfinite_and_negative_ratio(self):
        result=calculate('B6/B7',dict(B6=np.array([[2,2,-2,np.inf]]),B7=np.array([[0,1e-10,2,2]])))
        self.assertTrue(np.isnan(result[0,0])); self.assertTrue(np.isnan(result[0,1]))
        self.assertEqual(result[0,2],-1); self.assertTrue(np.isnan(result[0,3]))

    def test_preview_does_not_create_results_or_full_raster(self):
        result=self.run_rgb(['DIRECT_RGB'],options={'preview_only':True})
        self.assertEqual(result['OUTPUT_RASTERS'],[])
        self.assertFalse((self.scene/'Results').exists()); self.assertFalse((self.scene/'Work').exists())
        html=Path(result['PREVIEWS'][0]).read_text('utf-8')
        self.assertIn('Before selected enhancement',html); self.assertIn('After selected enhancement',html)
        self.assertFalse(list(Path(result['PREVIEWS'][0]).parent.glob('*.tif')))

    def test_display_settings_do_not_change_analysis(self):
        quiet=self.run_rgb(['DIRECT_RGB'],options={'display_mode':'quiet'})
        strong=self.run_rgb(['DIRECT_RGB'],options={'display_mode':'enhanced'})
        with rasterio.open(quiet['OUTPUT_RASTERS'][0]) as a,rasterio.open(strong['OUTPUT_RASTERS'][0]) as b:
            np.testing.assert_array_equal(a.read(),b.read())
        with rasterio.open(strong['DISPLAY_RASTERS'][0]) as ds:
            self.assertEqual(ds.dtypes,('uint8',)*3)
            self.assertIn('not_analytical',ds.tags()['ATIAF_PRODUCT'])

    def test_rerun_destination_and_source_preserved(self):
        source=next(self.scene.glob('*_SR_B7.TIF')); original=source.read_bytes()
        first=self.run_rgb(['DIRECT_RGB'],output_folder=self.root/'destination')
        before=Path(first['OUTPUT_RASTERS'][0]).read_bytes()
        second=self.run_rgb(['DIRECT_RGB'],output_folder=self.root/'destination')
        self.assertNotEqual(first['OUTPUT_RASTERS'],second['OUTPUT_RASTERS'])
        self.assertEqual(Path(first['OUTPUT_RASTERS'][0]).read_bytes(),before)
        self.assertEqual(source.read_bytes(),original)
        self.assertIn('destination',Path(first['OUTPUT_RASTERS'][0]).parts)

    def test_gates_before_writes(self):
        for options,selection in [({},[]),({'direct_preset':'S2_12114'},['DIRECT_RGB']),
            ({'direct_channels':'B12;B5;B3','custom_source':'local'},['DIRECT_RGB']),
            ({'direct_channels':'B6/B7;B5;B3','custom_source':'local'},['DIRECT_RGB'])]:
            with self.subTest(options=options),self.assertRaises(ValueError):
                run_tool('geological_composites',self.scene,selection,options=options)
        self.assertFalse((self.scene/'Results').exists())

    def test_experimental_is_explicit(self):
        with self.assertRaisesRegex(ValueError,'experimental'):
            self.run_rgb(['DIRECT_RGB'],options={'direct_preset':'L89_762'})
        result=self.run_rgb(['DIRECT_RGB'],options={'direct_preset':'L89_762','allow_experimental':True})
        self.assertEqual(len(result['OUTPUT_RASTERS']),1)

    def test_custom_preset_export_import_and_spoofing(self):
        first=self.run_rgb(['RATIO_RGB'],options={'ratio_channels':'B4/B2;B6/B7;B7/B5','custom_source':'local method'})
        preset=Path(first['RUN_MANIFESTS'][0])/'Composite_Preset.json'
        second=self.run_rgb(['RATIO_RGB'],options={'preset_file':str(preset),'restore_preset_display':True})
        with rasterio.open(first['OUTPUT_RASTERS'][0]) as a,rasterio.open(second['OUTPUT_RASTERS'][0]) as b:
            np.testing.assert_array_equal(a.read(),b.read())
        value=json.loads(preset.read_text('utf-8')); value['presets'][0]['status']='source_verified'
        edited=self.root/'edited.json'; edited.write_text(json.dumps(value),'utf-8')
        plans=validate_request(self.scene,['RATIO_RGB'],options={'preset_file':str(edited)})
        self.assertEqual(plans[0]['preset']['status'],'custom')

    def test_polygon_clip_and_output_crs(self):
        polygon=Polygon([(300000,3300000),(300360,3300000),(300000,3299640)])
        result=self.run_rgb(['DIRECT_RGB'],aoi_geometry=polygon,aoi_crs='EPSG:32636',output_crs='EPSG:32636')
        with rasterio.open(result['OUTPUT_RASTERS'][0]) as ds:
            self.assertEqual(ds.count,3); self.assertLess(ds.width,16)
            self.assertGreater(np.count_nonzero(ds.read_masks(1)==0),0)
            self.assertEqual(ds.descriptions,('B7','B5','B3'))

    def test_different_dates_mosaic_rejected_before_writes(self):
        make_scene(self.root,'later',date='2023-05-21')
        with self.assertRaisesRegex(ValueError,'Mosaic requires'):
            run_tool('geological_composites',self.root,['DIRECT_RGB'],mosaic=True)
        self.assertFalse((self.scene/'Results').exists())

    def test_batch_mosaic_has_one_scene_for_whole_rgb_pixel(self):
        second=make_scene(self.root,'second',red_dn=14000)
        result=run_tool('geological_composites',self.root,['RATIO_RGB'],mosaic=True)
        self.assertEqual(len(result['OUTPUT_RASTERS']),3)
        with rasterio.open(result['OUTPUT_RASTERS'][-1]) as merged,rasterio.open(result['OUTPUT_RASTERS'][0]) as original:
            np.testing.assert_array_equal(merged.read(),original.read())
        ids=list((self.root/'Results').rglob('*Source_Scene_ID.tif'))
        self.assertEqual(len(ids),1)
        with rasterio.open(ids[0]) as ds: self.assertEqual(ds.read(1)[2,2],1)

    def stack(self,sensor='ASTER_AST_07',date='2005-05-20',names='B4,B6,B8'):
        path=self.root/'stack.tif'
        a=np.arange(48,dtype='float32').reshape(4,12)/50+.1
        with rasterio.open(path,'w',driver='GTiff',width=12,height=4,count=3,dtype='float32',crs='EPSG:32636',
            transform=rasterio.transform.from_origin(300000,3300000,30,30),nodata=-9999) as ds:
            ds.write(np.stack([a,a+1,a+2]))
        return dict(stack_mode=True,stack_raster=str(path),stack_band_ids=names,stack_scales='1',stack_offsets='0',
            stack_date=date,stack_provenance='Independent synthetic reflectance fixture',allow_experimental=True)

    def test_explicit_aster_stack_maps_scientific_band_not_position(self):
        options=self.stack()
        result=self.run_rgb(['DIRECT_RGB'],sensor='ASTER_AST_07',apply_qa=False,options=options)
        with rasterio.open(result['OUTPUT_RASTERS'][0]) as ds:
            np.testing.assert_allclose(ds.read()[:,1,1],[.36,1.36,2.36],atol=1e-6)
        self.assertEqual(scientific_id('B08A'),'B8A')
        self.assertNotEqual(scientific_id('B08'),scientific_id('B8A'))

    def test_aster_invalid_date_and_stack_mapping_rejected(self):
        options=self.stack(date='2008-04-01')
        with self.assertRaisesRegex(ValueError,'before April 2008'):
            self.run_rgb(['DIRECT_RGB'],sensor='ASTER_AST_07',apply_qa=False,options=options)
        options['stack_date']='2005-05-20'; options['stack_band_ids']='B4,B4,B8'
        with self.assertRaisesRegex(ValueError,'uniquely'):
            self.run_rgb(['DIRECT_RGB'],sensor='ASTER_AST_07',apply_qa=False,options=options)

    def test_cancel_before_any_writes(self):
        with self.assertRaises(InterruptedError): self.run_rgb(canceled=lambda:True)
        self.assertFalse((self.scene/'Results').exists())

    def test_bilingual_fields_no_mixed_interface_and_output_last_contract(self):
        from atiaf_core.ui_schema import fields,ui_rows
        for spec in fields('geological_composites'):
            self.assertFalse(any('\u0600'<=c<='\u06ff' for c in spec['en']))
            self.assertTrue(spec['ar'])
        self.assertEqual([r['id'] for r in ui_rows('geological_composites')],['DIRECT_RGB','RATIO_RGB'])

    def test_render_fixed_limits_and_invalid_controls(self):
        with self.assertRaises(ValueError): render.settings({'display_mode':'custom','display_gamma':0})
        with self.assertRaises(ValueError): render.settings({'display_limits':'1,0,1,2,1,2'})
        config=render.settings({'display_limits':'0,1,0,2,-1,1'})
        self.assertEqual(render.limits(np.ones((3,2,2)),config),[[0.,1.],[0.,2.],[-1.,1.]])

    def legacy_fixture(self):
        folder=self.root/'legacy'; folder.mkdir()
        lines=['LANDSAT_SCENE_ID = "LC81760392014234LGN00"','SPACECRAFT_ID = "LANDSAT_8"',
               'DATA_TYPE = "L1T"','DATE_ACQUIRED = 2014-08-22','SUN_ELEVATION = 30',
               'FILE_NAME_BAND_QUALITY = "BQA.tif"']
        profile=dict(driver='GTiff',width=8,height=8,count=1,dtype='uint16',crs='EPSG:32636',
            transform=rasterio.transform.from_origin(300000,3300000,30,30),nodata=0)
        for n in range(1,8):
            name=f'B{n}.tif'; lines.extend([f'FILE_NAME_BAND_{n} = "{name}"',
                f'REFLECTANCE_MULT_BAND_{n} = 0.00002',f'REFLECTANCE_ADD_BAND_{n} = -0.1'])
            with rasterio.open(folder/name,'w',**profile) as ds: ds.write(np.full((8,8),10000+n*1000,dtype='uint16'),1)
        qa=np.zeros((8,8),dtype='uint16'); qa[0,:6]=[1,2,4,2<<10,2<<12,2<<14]
        with rasterio.open(folder/'BQA.tif','w',**dict(profile,nodata=None)) as ds: ds.write(qa,1)
        (folder/'fixture_MTL.txt').write_text('\n'.join(lines),'utf-8')
        return folder

    def test_legacy_toa_solar_scaling_and_exact_bqa_schema(self):
        folder=self.legacy_fixture()
        with self.assertRaisesRegex(ValueError,'explicit TOA'):
            run_tool('geological_composites',folder,['DIRECT_RGB'])
        result=run_tool('geological_composites',folder,['DIRECT_RGB'],options={'allow_toa':True})
        with rasterio.open(result['OUTPUT_RASTERS'][0]) as ds:
            np.testing.assert_allclose(ds.read()[:,2,2],[.48,.4,.32],atol=1e-6)
            self.assertTrue(np.all(ds.read_masks()[:,0,:6]==0))
        no_qa=run_tool('geological_composites',folder,['DIRECT_RGB'],options={'allow_toa':True},apply_qa=False)
        with rasterio.open(no_qa['OUTPUT_RASTERS'][0]) as ds: self.assertTrue(np.all(ds.read_masks()[:,0,:6]>0))

    def test_legacy_cannot_be_labeled_collection2(self):
        with self.assertRaisesRegex(ValueError,'pre-Collection'):
            run_tool('geological_composites',self.legacy_fixture(),['DIRECT_RGB'],sensor='LANDSAT_8_9_C2_L2',options={'allow_toa':True})

    def test_signed_minus9999_is_valid_and_outputs_explain_identity(self):
        result=self.run_rgb(['RATIO_RGB'],options={'ratio_channels':'B6/B7;B6*0-9999;B4/B5','custom_source':'signed sentinel collision fixture',
            'save_intermediates':True})
        path=Path(result['OUTPUT_RASTERS'][0]); self.assertEqual(path.parent.name,'Analytical')
        self.assertIn('Landsat8',path.name)
        with rasterio.open(path) as ds:
            self.assertTrue(np.isnan(ds.nodata)); self.assertEqual(ds.read(2)[2,2],-9999)
            self.assertEqual(ds.read_masks(2)[2,2],255)
        with rasterio.open(result['DISPLAY_RASTERS'][0]) as ds: self.assertTrue(np.all(ds.read()[:,2,2]>0))
        metadata=next((path.parent.parent/'Metadata').glob('*.json'))
        meta=json.loads(metadata.read_text('utf-8')); self.assertEqual(meta['actual_satellite'],'Landsat 8')
        self.assertEqual(meta['channel_statistics'][1]['min'],-9999)
        self.assertEqual(meta['channel_statistics'][1]['max'],-9999)
        self.assertEqual(meta['channel_statistics'][1]['mean'],-9999)
        self.assertGreater(meta['channel_statistics'][1]['nodata_pixels'],0)
        self.assertEqual(len(meta['intermediate_channels']),3)
        for channel in meta['intermediate_channels']:
            self.assertIn('Work',Path(channel).parts)
            with rasterio.open(channel) as ds: self.assertEqual(ds.count,1)

    def test_stretch_methods_have_independent_bounds_and_identical_analysis(self):
        sample=np.array([[[0,1,2,100]]]*3,dtype='float32')
        linear=render.settings({'stretch_method':'linear'})
        self.assertEqual(render.limits(sample,linear),[[0.,100.]]*3)
        std=render.settings({'stretch_method':'stddev','display_stddev':2})
        np.testing.assert_allclose(render.limits(sample,std),[[sample.mean()-2*sample.std(),sample.mean()+2*sample.std()]]*3,rtol=1e-6)
        with self.assertRaises(ValueError): render.settings({'stretch_method':'unknown'})
        arrays=[]
        for method in ('linear','percentile','stddev'):
            result=self.run_rgb(['DIRECT_RGB'],options={'stretch_method':method})
            with rasterio.open(result['OUTPUT_RASTERS'][0]) as ds: arrays.append(ds.read())
        np.testing.assert_array_equal(arrays[0],arrays[1]); np.testing.assert_array_equal(arrays[0],arrays[2])

    def test_legacy_qa_not_applied_to_collection1_by_filename(self):
        folder=self.legacy_fixture()
        with (folder/'fixture_MTL.txt').open('a',encoding='utf-8') as stream: stream.write('\nCOLLECTION_NUMBER = 01\n')
        plans=validate_request(folder,['DIRECT_RGB'],options={'allow_toa':True})
        self.assertIn('BQA_C1_L8',plans[0]['data']['scene'].quality_masks)
        self.assertNotIn('BQA_PRECOLLECTION',plans[0]['data']['scene'].quality_masks)

    def test_imported_preset_cannot_escape_output_directory(self):
        preset=self.root/'unsafe.json'
        preset.write_text(json.dumps(dict(format='atiaf_composite_preset_v1',presets=[dict(id='../escape',sensor='LANDSAT_8_9',
            method='DIRECT_RGB',channels=['B7','B5','B3'],source='local')])),encoding='utf-8')
        with self.assertRaisesRegex(ValueError,'unsafe filename'):
            self.run_rgb(['DIRECT_RGB'],options={'preset_file':str(preset)})


if __name__=='__main__': unittest.main(verbosity=2)

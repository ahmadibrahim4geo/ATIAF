"""Independent generation, physical-band, calibration and historic QA fixtures."""
from pathlib import Path
import json,math,tempfile,unittest
from datetime import datetime
import numpy as np
import rasterio
from atiaf_core.discovery import LandsatParser,Sentinel2Parser,SceneScanner
from atiaf_core.discovery.models import BandRole
from atiaf_core.workflow import discover,run_tool,unavailable_reason
from atiaf_core.raster.masks import QualityMaskEngine


class HistoricalProducts(unittest.TestCase):
    def setUp(self): self.temp=tempfile.TemporaryDirectory(); self.root=Path(self.temp.name)
    def tearDown(self): self.temp.cleanup()
    def landsat(self,number=8,collection=None,level='L1T',date='2014-08-22',sensor=None,fmt='txt',name='scene'):
        folder=self.root/name; folder.mkdir()
        sensor=sensor or ('OLI_TIRS' if number>=8 else 'ETM' if number==7 else 'TM')
        scene_id=f'LC{number}1760392014234LGN00' if number>=8 else f'LT{number}1760391994234XXX00'
        m=dict(SPACECRAFT_ID='LANDSAT_'+str(number),SENSOR_ID=sensor,LANDSAT_SCENE_ID=scene_id,DATE_ACQUIRED=date,
            SUN_ELEVATION='30',FILE_DATE='2014-08-23T12:00:00Z',WRS_PATH='176',WRS_ROW='39')
        if collection:
            m.update(COLLECTION_NUMBER=str(collection),PROCESSING_LEVEL=level,
                LANDSAT_PRODUCT_ID=f'LC{number:02d}_{"L2SP" if level.startswith("L2") else "L1TP"}_176039_20140822_20200101_{collection:02d}_T1')
        else: m['DATA_TYPE']=level
        indices=range(1,8) if number>=8 else [1,2,3,4,5,6,7]
        profile=dict(driver='GTiff',width=8,height=8,count=1,dtype='int16' if collection==1 and level.startswith('L2') else 'uint16',
            crs='EPSG:32636',transform=rasterio.transform.from_origin(300000,3300000,30,30),nodata=-9999 if collection==1 and level.startswith('L2') else 0)
        for n in indices:
            if number<8 and n==6 and sensor!='MSS': continue
            filename=f'nonstandard_asset_{n}.tif'
            m[f'FILE_NAME_BAND_{n}']=filename; m[f'REFLECTANCE_MULT_BAND_{n}']='0.00002';m[f'REFLECTANCE_ADD_BAND_{n}']='-0.1'
            values=np.full((8,8),2000 if collection==1 and level.startswith('L2') else 10000+n*1000,dtype=profile['dtype'])
            values[0,0]=profile['nodata']
            with rasterio.open(folder/filename,'w',**profile) as ds: ds.write(values,1)
        qa_name='scene_pixel_qa.tif' if collection==1 and level.startswith('L2') else 'scene_QA_PIXEL.tif' if collection==2 else 'scene_BQA.tif'
        m['FILE_NAME_BAND_QUALITY']=qa_name
        with rasterio.open(folder/qa_name,'w',**dict(profile,dtype='uint16',nodata=None)) as ds:
            ds.write(np.zeros((8,8),dtype='uint16'),1)
        if fmt=='json': (folder/'source_MTL.json').write_text(json.dumps({'LANDSAT_METADATA_FILE':{'FIELDS':m}}),'utf-8')
        elif fmt=='xml': (folder/'source_MTL.xml').write_text('<m:MTL xmlns:m="urn:fixture">'+''.join(f'<m:{k}>{v}</m:{k}>' for k,v in m.items())+'</m:MTL>','utf-8')
        else: (folder/'source_MTL.txt').write_text('\n'.join(f'{k} = "{v}"' for k,v in m.items()),'utf-8')
        return folder

    def test_legacy_identity_not_inferred_from_folder_name(self):
        folder=self.landsat(name='arbitrary_folder'); scene=discover(folder)[0]
        m=scene.metadata
        self.assertEqual((m.product_generation,m.collection,m.product_level.value),('PRE_COLLECTION',None,'L1T'))
        self.assertEqual((m.source_scene_id,m.product_id,m.wrs_path,m.wrs_row,m.ground_station,m.archive_version),
            ('LC81760392014234LGN00',None,176,39,'LGN','00'))
        self.assertEqual(m.acquisition_date,datetime(2014,8,22));self.assertEqual(m.processing_date,'2014-08-23T12:00:00Z')
        self.assertAlmostEqual(scene.bands[BandRole.RED].scale_factor,.00004)
        self.assertAlmostEqual(scene.bands[BandRole.RED].offset,-.2)
        self.assertIn('BQA_PRECOLLECTION',scene.quality_masks)

    def test_legacy_ndvi_is_opt_in_and_named_toa(self):
        folder=self.landsat(); scene=discover(folder)[0]
        self.assertTrue(unavailable_reason('spectral_indices','NDVI',scene))
        result=run_tool('spectral_indices',folder,['NDVI'],options={'allow_toa':True})
        self.assertIn('NDVI_TOA',Path(result['OUTPUT_RASTERS'][0]).name)
        expected=(.4-.36)/(.4+.36)
        with rasterio.open(result['OUTPUT_RASTERS'][0]) as ds: self.assertAlmostEqual(float(ds.read(1)[2,2]),expected,places=6)
        self.assertTrue(unavailable_reason('surface_temperature','LST',scene,{'allow_toa':True}))
        self.assertTrue(unavailable_reason('spectral_indices','EVI',scene,{'allow_toa':True}))

    def test_collection1_sr_never_uses_collection2_offset(self):
        scene=discover(self.landsat(collection=1,level='L2SR'))[0]
        band=scene.bands[BandRole.RED]
        self.assertEqual((band.scale_factor,band.offset,band.nodata),(.0001,0.,-9999.))
        self.assertAlmostEqual(2000*band.scale_factor+band.offset,.2)
        self.assertIn('PIXEL_QA_C1_L8',scene.quality_masks)
        self.assertNotIn('QA_PIXEL',scene.quality_masks)
        with self.assertRaises(ValueError): discover(scene.scene_path,'LANDSAT_8_9_C2_L2')

    def test_collection1_l1_qa_schema_not_precollection(self):
        scene=discover(self.landsat(collection=1,level='L1TP'))[0]
        self.assertEqual(scene.metadata.collection,'01');self.assertIn('BQA_C1_L8',scene.quality_masks)
        q=np.array([2<<14,2<<7,1<<4,1<<2,0],dtype='uint16')
        np.testing.assert_array_equal(QualityMaskEngine.clear_for_schema(q,'BQA_C1_L8'),[True,False,False,False,True])
        self.assertFalse(QualityMaskEngine.clear_for_schema(q,'BQA_PRECOLLECTION')[0])

    def test_collection2_l1_and_l2_keep_distinct_physical_scaling(self):
        a=discover(self.landsat(collection=2,level='L1TP',name='a'))[0]
        b=discover(self.landsat(collection=2,level='L2SP',name='b'))[0]
        self.assertEqual(a.metadata.radiometric_unit,'toa_reflectance');self.assertEqual(b.metadata.radiometric_unit,'surface_reflectance')
        self.assertAlmostEqual(a.bands[BandRole.RED].scale_factor,.00004)
        self.assertEqual(b.bands[BandRole.RED].scale_factor,.0000275)

    def test_mtl_xml_and_json(self):
        for fmt in ('xml','json'):
            with self.subTest(fmt=fmt):
                scene=discover(self.landsat(fmt=fmt,name=fmt))[0]
                self.assertEqual(scene.metadata.source_scene_id,'LC81760392014234LGN00')
                self.assertEqual(scene.bands[BandRole.SWIR_1].band_name,'B6')

    def test_tm_etm_roles_and_slc_dates(self):
        for n,date,off in [(7,'2003-05-30',False),(7,'2004-01-10',True),(5,'1994-08-22',False),(4,'1984-08-22',False)]:
            scene=discover(self.landsat(n,collection=2,level='L2SP',date=date,name=str(n)+date))[0]
            self.assertEqual(scene.bands[BandRole.SWIR_1].band_name,'B5')
            self.assertEqual(scene.bands[BandRole.SWIR_2].band_name,'B7')
            self.assertNotEqual(scene.bands[BandRole.SWIR_1].band_name,'B6')
            self.assertEqual('SLC_OFF' in scene.metadata.restrictions,off)

    def test_mss45_uses_different_band_numbers_and_no_swir(self):
        scene=discover(self.landsat(4,sensor='MSS',date='1984-08-22'))[0]
        self.assertEqual(scene.bands[BandRole.GREEN].band_name,'B1')
        self.assertEqual(scene.bands[BandRole.NIR].band_name,'B3')
        self.assertNotIn(BandRole.SWIR_1,scene.bands);self.assertIn('MSS',scene.metadata.sensor_id)

    def test_mss123_uses_bands4_to7_without_thermal(self):
        scene=discover(self.landsat(1,sensor='MSS',date='1974-08-22'))[0]
        self.assertEqual(scene.bands[BandRole.GREEN].band_name,'B4')
        self.assertEqual(scene.bands[BandRole.NIR].band_name,'B6')
        self.assertNotIn(BandRole.THERMAL_1,scene.bands)

    def test_explicit_espa_sr_band_metadata(self):
        folder=self.landsat(collection=1,level='L2SR')
        (folder/'source_MTL.txt').unlink()  # Only private fixture metadata, never user inputs.
        entries=''.join(f'<band product="sr_refl" name="sr_band{n}" scale_factor="0.0001" add_offset="0" fill_value="-9999"><file_name>nonstandard_asset_{n}.tif</file_name><data_units>reflectance</data_units></band>' for n in range(1,8))
        (folder/'product.xml').write_text('<espa_metadata><global_metadata><satellite>LANDSAT_8</satellite><instrument>OLI_TIRS</instrument><landsat_scene_id>LC81760392014234LGN00</landsat_scene_id><acquisition_date>2014-08-22</acquisition_date><collection_number>1</collection_number></global_metadata><bands>'+entries+'</bands></espa_metadata>','utf-8')
        scene=discover(folder)[0]
        self.assertEqual(scene.metadata.radiometric_unit,'surface_reflectance')
        self.assertAlmostEqual(scene.bands[BandRole.RED].scale_factor,.0001)
        self.assertIn('scale_factor',scene.bands[BandRole.RED].calibration_provenance)

    def test_companion_espa_and_mtl_identity_checked(self):
        folder=self.landsat(collection=1,level='L1TP')
        xml='<espa_metadata><global_metadata><satellite>LANDSAT_8</satellite><instrument>OLI_TIRS</instrument><landsat_scene_id>LC81760392014234LGN00</landsat_scene_id><acquisition_date>2014-08-22</acquisition_date></global_metadata><bands><band product="sr_refl" name="sr_band4" scale_factor="0.0001"><file_name>nonstandard_asset_4.tif</file_name><data_units>reflectance</data_units></band></bands></espa_metadata>'
        p=folder/'espa.xml';p.write_text(xml,'utf-8')
        scene=discover(folder)[0]
        self.assertEqual(scene.metadata.radiometric_unit,'surface_reflectance')
        self.assertEqual(scene.metadata.metadata_file.name,'espa.xml')
        self.assertEqual(scene.bands[BandRole.RED].scale_factor,.0001)
        self.assertNotIn(BandRole.NIR,scene.bands)
        p.write_text(xml.replace('LC81760392014234LGN00','LC81760392014234XXX00'),'utf-8')
        with self.assertRaisesRegex(ValueError,'matching'): discover(folder)

    def test_metadata_path_and_xml_entity_rejections(self):
        folder=self.landsat(); p=folder/'source_MTL.txt'
        p.write_text(p.read_text('utf-8').replace('nonstandard_asset_4.tif','../outside.tif'),'utf-8')
        with self.assertRaisesRegex(ValueError,'escapes'): discover(folder)
        for sensor in ('landsat','sentinel'):
            folder=self.landsat(fmt='xml',name='xmlbad') if sensor=='landsat' else self.sentinel(name='xmls2')
            p=next(folder.glob('*.xml'));p.write_text('<!DOCTYPE Product [<!ENTITY x "blocked">]>'+p.read_text('utf-8'),'utf-8')
            with self.assertRaises(ValueError): discover(folder)

    def test_missing_rgb_band_fails_before_writes(self):
        folder=self.landsat();(folder/'nonstandard_asset_7.tif').unlink()
        with self.assertRaisesRegex(ValueError,'missing'):
            run_tool('geological_composites',folder,['RATIO_RGB'],options={'allow_toa':True})
        self.assertFalse((folder/'Results').exists())

    def test_metadata_conflict_and_missing_coefficients_fail_safe(self):
        folder=self.landsat(collection=1,level='L1TP')
        p=folder/'source_MTL.txt';text=p.read_text('utf-8');p.write_text(text.replace('COLLECTION_NUMBER = "1"','COLLECTION_NUMBER = "2"'),'utf-8')
        with self.assertRaisesRegex(ValueError,'conflicts'): discover(folder)
        folder=self.landsat(name='missing');p=folder/'source_MTL.txt'
        p.write_text('\n'.join(l for l in p.read_text('utf-8').splitlines() if 'REFLECTANCE_' not in l),'utf-8')
        scene=discover(folder)[0]
        self.assertTrue(unavailable_reason('spectral_indices','NDVI',scene,{'allow_toa':True}))

    def test_generation_mixture_not_silently_mosaicked(self):
        self.landsat(name='pre');self.landsat(collection=1,level='L1TP',name='c1')
        with self.assertRaisesRegex(ValueError,'Mosaic requires'):
            run_tool('geological_composites',self.root,['DIRECT_RGB'],mosaic=True,options={'allow_toa':True})

    def sentinel(self,baseline='04.00',level='2A',offsets=True,name='s2'):
        folder=self.root/name; folder.mkdir(); tag='BOA_ADD_OFFSET' if level=='2A' else 'RADIO_ADD_OFFSET'
        quant='BOA_QUANTIFICATION_VALUE' if level=='2A' else 'QUANTIFICATION_VALUE'
        text=f'<s:Product xmlns:s="urn:fixture"><s:PRODUCT_URI>S2A_MSIL{level}_20230615T082611_N0400_R121_T36RUU</s:PRODUCT_URI><s:PROCESSING_LEVEL>Level-{level}</s:PROCESSING_LEVEL><s:PROCESSING_BASELINE>{baseline}</s:PROCESSING_BASELINE><s:{quant}>20000</s:{quant}>'
        if offsets: text+=f'<s:{tag} band_id="3">-1000</s:{tag}><s:{tag} band_id="7">-2000</s:{tag}>'
        text+='</s:Product>'; (folder/f'MTD_MSIL{level}.xml').write_text(text,'utf-8')
        for b in ('B04','B08'):
            with rasterio.open(folder/f'physical_{b}.tif','w',driver='GTiff',width=4,height=4,count=1,dtype='uint16',
                crs='EPSG:32636',transform=rasterio.transform.from_origin(300000,3300000,10,10),nodata=0) as ds:
                ds.write(np.full((4,4),12000,dtype='uint16'),1)
        return folder

    def test_sentinel_per_band_offset_quantum_and_namespace(self):
        for level in ('1C','2A'):
            scene=Sentinel2Parser.parse(self.sentinel(level=level,name=level))
            self.assertEqual(scene.bands[BandRole.RED].scale_factor,1/20000)
            self.assertEqual(scene.bands[BandRole.RED].offset,-.05)
            self.assertEqual(scene.bands[BandRole.NIR].offset,-.1)
            self.assertAlmostEqual(12000*scene.bands[BandRole.RED].scale_factor+scene.bands[BandRole.RED].offset,.55)
            self.assertTrue(scene.bands[BandRole.RED].valid_max is None or scene.bands[BandRole.RED].valid_max>12000)

    def test_sentinel_old_baseline_zero_offset_and_missing_modern_offset_rejected(self):
        scene=Sentinel2Parser.parse(self.sentinel(baseline='03.01',offsets=False,name='old'))
        self.assertEqual(scene.bands[BandRole.NIR].offset,0)
        with self.assertRaisesRegex(ValueError,'per-band'):
            Sentinel2Parser.parse(self.sentinel(offsets=False,name='bad'))

    def test_sentinel_missing_available_band_offset_and_quantification_rejected(self):
        folder=self.sentinel();p=next(folder.glob('*.xml'));text=p.read_text('utf-8')
        p.write_text(text.replace('<s:BOA_ADD_OFFSET band_id="7">-2000</s:BOA_ADD_OFFSET>',''),'utf-8')
        with self.assertRaisesRegex(ValueError,'available band'): discover(folder)
        p.write_text(text.replace('<s:BOA_QUANTIFICATION_VALUE>20000</s:BOA_QUANTIFICATION_VALUE>',''),'utf-8')
        with self.assertRaisesRegex(ValueError,'quantification'): discover(folder)


if __name__=='__main__': unittest.main(verbosity=2)

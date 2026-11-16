"""Actual Pro parameter and execution checks; synthetic scenes, no GUI click claim."""
from pathlib import Path
import sys,tempfile,unittest
ROOT=Path(__file__).resolve().parents[2]
sys.path[:0]=[str(ROOT),str(ROOT/'tests')]
import arcpy,numpy as np,rasterio
from workflow_fixture import make_scene


class NativeComposites(unittest.TestCase):
    def setUp(self): self.temp=tempfile.TemporaryDirectory(); self.scene=make_scene(self.temp.name)
    def tearDown(self): self.temp.cleanup()
    def test_parameters_and_both_methods_both_languages(self):
        for lang in ('en','ar'):
            toolbox='ATIAF_AR.pyt' if lang=='ar' else 'ATIAF.pyt'
            arcpy.ImportToolbox(str(ROOT/'ArcGIS Pro Tools'/toolbox))
            alias='atiaf_ar' if lang=='ar' else 'atiaf'
            params=arcpy.GetParameterInfo('GeologicalColorCompositesTool_'+alias)
            self.assertEqual(params[0].name,'sensor_product'); self.assertEqual(params[-1].name,'output_folder')
            for p in params:
                if p.name.startswith('calc_'): self.assertEqual(str(p.value).lower(),'false')
            out=Path(self.temp.name)/lang; out.mkdir()
            getattr(arcpy,alias).GeologicalColorCompositesTool(input_folder=str(self.scene),output_folder=str(out),
                calc_DIRECT_RGB=True,calc_RATIO_RGB=True)
            paths=[p for p in out.rglob('*.tif') if not p.stem.endswith('_DISPLAY')]
            self.assertEqual(len(paths),2)
            direct=next(p for p in paths if 'Direct_RGB' in p.parts)
            with rasterio.open(direct) as ds:
                np.testing.assert_allclose(ds.read()[:,2,2],[.185,.5000125,.13],rtol=1e-5)
            sys.path.insert(0,str(ROOT/'ArcGIS Pro Tools'))
            from atiaf_arcgis import NativeTool
            display=next(out.rglob('*_DISPLAY.tif'))
            layer=arcpy.management.MakeRasterLayer(str(display),'RGB_'+lang).getOutput(0)
            NativeTool.style_composite_display(layer)
            saved=out/'RGB.lyrx'; layer.saveACopy(str(saved))
            reopened=arcpy.mp.LayerFile(str(saved)).listLayers()[0]
            colorizer=reopened.getDefinition('V3').colorizer
            self.assertEqual(colorizer.redBandIndex,0); self.assertEqual(colorizer.blueBandIndex,2)
            self.assertEqual(colorizer.stretchType,'None')
            arcpy.management.Delete('RGB_'+lang)
            del layer,reopened,colorizer
            import gc
            gc.collect()
            arcpy.management.ClearWorkspaceCache()
    def test_native_temporary_preview_has_no_results(self):
        arcpy.ImportToolbox(str(ROOT/'ArcGIS Pro Tools'/'ATIAF.pyt'))
        arcpy.atiaf.GeologicalColorCompositesTool(input_folder=str(self.scene),calc_DIRECT_RGB=True,preview_only=True)
        self.assertFalse((self.scene/'Results').exists())

if __name__=='__main__': unittest.main(verbosity=2)

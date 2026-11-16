"""Actual QGIS runtime RGB calculations, queued renderer and bilingual panel/preview."""
from pathlib import Path
import sys,tempfile,time,unittest,os
ROOT=Path(__file__).resolve().parents[2]
sys.path[:0]=[str(ROOT),str(ROOT/'QGIS Tools'),str(ROOT/'tests')]
from qgis.core import QgsApplication,QgsProcessingContext,QgsProcessingFeedback,QgsProject,QgsRasterLayer
from qgis.PyQt.QtWidgets import QMainWindow
from qgis.gui import QgsMessageBar
import numpy as np
import rasterio
from workflow_fixture import make_scene
from atiaf.algorithms.geological_composites import GeologicalCompositesAlgorithm


class NativeComposites(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app=QgsApplication([],False); cls.app.initQgis()
        # A headless QgsApplication does not initialize the desktop's font setup.
        # Use the OS-installed font for this render test; no font is copied/bundled.
        from qgis.PyQt.QtGui import QFontDatabase,QFont
        font=Path('C:/Windows/Fonts/tahoma.ttf')
        if font.is_file():
            identifier=QFontDatabase.addApplicationFont(str(font))
            families=QFontDatabase.applicationFontFamilies(identifier)
            if families: cls.app.setFont(QFont(families[0],10))
        sys.path.insert(0,str(Path(QgsApplication.prefixPath())/'python'/'plugins'))
    @classmethod
    def tearDownClass(cls): cls.app.exitQgis()
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory(); self.scene=make_scene(self.temp.name)
    def tearDown(self): self.temp.cleanup()
    def algorithm(self,lang):
        a=GeologicalCompositesAlgorithm(); a.language=lang; a.initAlgorithm(); return a

    def test_native_methods_both_languages_and_queued_rgb_renderer(self):
        for lang in ('en','ar'):
            a=self.algorithm(lang); context=QgsProcessingContext(); feedback=QgsProcessingFeedback()
            project=QgsProject(); context.setProject(project)
            self.assertEqual(a.parameterDefinitions()[0].name(),'SENSOR')
            self.assertEqual(a.parameterDefinitions()[-1].name(),'OUTPUT_FOLDER')
            result=a.processAlgorithm(dict(INPUT_FOLDER=str(self.scene),calc_DIRECT_RGB=True,calc_RATIO_RGB=True,
                ADD_TO_MAP=True),context,feedback)
            self.assertEqual(len(result['OUTPUT_RASTERS']),2)
            with rasterio.open(result['OUTPUT_RASTERS'][0]) as ds:
                np.testing.assert_allclose(ds.read()[:,2,2],[.185,.5000125,.13],rtol=1e-5)
            a.postProcessAlgorithm(context,feedback)
            self.assertEqual(len(project.mapLayers()),0)
            for _ in range(8): QgsApplication.processEvents()
            self.assertEqual(len(project.mapLayers()),2)
            for layer in project.mapLayers().values():
                self.assertTrue(layer.isValid()); self.assertEqual(layer.renderer().type(),'multibandcolor')
                self.assertEqual(layer.renderer().redBand(),1); self.assertEqual(layer.renderer().blueBand(),3)
            project.clear()

    def test_native_panel_and_async_before_after_preview(self):
        class Parent(QMainWindow):
            def __init__(self): super().__init__(); self.bar=QgsMessageBar(self)
            def messageBar(self): return self.bar
        for lang in ('en','ar'):
            parent=Parent(); a=self.algorithm(lang); panel=a.createCustomParametersWidget(parent)
            panel.setParameters(dict(INPUT_FOLDER=str(self.scene),calc_DIRECT_RGB=True,APPLY_QA=True))
            self.assertIn('Composites',panel._group_boxes)
            self.assertTrue(hasattr(panel,'_preview_button'))
            parent.setCentralWidget(panel); parent.resize(1050,1000); parent.show(); QgsApplication.processEvents()
            panel.preview_composite()
            deadline=time.monotonic()+20
            while not hasattr(panel,'_preview_dialog') and time.monotonic()<deadline:
                QgsApplication.processEvents(); time.sleep(.02)
            self.assertTrue(hasattr(panel,'_preview_dialog'))
            evidence=Path(os.environ.get('ATIAF_TEST_EVIDENCE_DIR',self.temp.name)); evidence.mkdir(parents=True,exist_ok=True)
            panel.grab().save(str(evidence/f'qgis_panel_{lang}.png'))
            panel._preview_dialog.grab().save(str(evidence/f'qgis_preview_{lang}.png'))
            panel._preview_dialog.close(); parent.close(); parent.deleteLater(); QgsApplication.processEvents()
        self.assertFalse((self.scene/'Results').exists())

    @unittest.skipUnless(os.environ.get('ATIAF_REAL_TEST_INPUT'),'No explicitly supplied real preview scene')
    def test_real_scene_native_before_after_previews(self):
        class Parent(QMainWindow):
            def __init__(self): super().__init__(); self.bar=QgsMessageBar(self)
            def messageBar(self): return self.bar
        for lang in ('en','ar'):
            a=self.algorithm(lang); parent=Parent(); panel=a.createCustomParametersWidget(parent)
            panel.setParameters(dict(INPUT_FOLDER=os.environ['ATIAF_REAL_TEST_INPUT'],calc_DIRECT_RGB=True,
                                     allow_toa=True,APPLY_QA=True,display_mode=2))
            parent.setCentralWidget(panel); parent.show(); QgsApplication.processEvents(); panel.preview_composite()
            deadline=time.monotonic()+30
            while not hasattr(panel,'_preview_dialog') and time.monotonic()<deadline:
                QgsApplication.processEvents(); time.sleep(.02)
            self.assertTrue(hasattr(panel,'_preview_dialog'))
            evidence=Path(os.environ.get('ATIAF_TEST_EVIDENCE_DIR',self.temp.name)); evidence.mkdir(parents=True,exist_ok=True)
            panel._preview_dialog.grab().save(str(evidence/f'qgis_real_preview_{lang}.png'))
            panel._preview_dialog.close(); parent.close(); parent.deleteLater(); QgsApplication.processEvents()

if __name__=='__main__': unittest.main(verbosity=2)

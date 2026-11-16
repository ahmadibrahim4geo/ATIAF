"""Isolated native QGIS package smoke check; this is not a clean-machine installation test."""
from pathlib import Path
import os
import subprocess
import sys
import tempfile
import zipfile

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT/'tests'))
from workflow_fixture import make_scene

sys.path.insert(0,str(ROOT))
from atiaf_core import __version__
archive_path = ROOT/f'QGIS Tools/Distribution/ATIAF-QGIS-{__version__}.zip'
with tempfile.TemporaryDirectory(prefix='atiaf_zip_') as directory:
    target = Path(directory)
    with zipfile.ZipFile(archive_path) as archive:
        for name in archive.namelist():
            if not (target/name).resolve().is_relative_to(target):
                raise ValueError('Unsafe archive member')
        archive.extractall(target)
    scene = make_scene(target, 'synthetic_scene')
    code = '''from pathlib import Path
import sys
sys.path.insert(0, sys.argv[1])
from qgis.core import QgsApplication,QgsProcessingContext,QgsProcessingFeedback,QgsRasterLayer
app=QgsApplication([],False);app.initQgis()
from atiaf.provider import ATIAFProcessingProvider
provider=ATIAFProcessingProvider();QgsApplication.processingRegistry().addProvider(provider)
import atiaf_core
assert Path(atiaf_core.__file__).is_relative_to(Path(sys.argv[1]))
assert len(provider.algorithms())==7
alg=provider.algorithm('spectral_indices').createInstance();alg.language='en';alg.initAlgorithm()
result=alg.processAlgorithm({'INPUT_FOLDER':sys.argv[2],'INDICES':[0]},QgsProcessingContext(),QgsProcessingFeedback())
assert QgsRasterLayer(result['OUTPUT_RASTERS'][0],'NDVI').isValid()
rgb=provider.algorithm('geological_composites').createInstance();rgb.language='en';rgb.initAlgorithm()
composite=rgb.processAlgorithm({'INPUT_FOLDER':sys.argv[2],'calc_DIRECT_RGB':True},QgsProcessingContext(),QgsProcessingFeedback())
assert QgsRasterLayer(composite['OUTPUT_RASTERS'][0],'RGB').bandCount()==3
print('PACKAGED PLUGIN PASS: relocated core, seven algorithms, native synthetic NDVI and RGB readback')
QgsApplication.processingRegistry().removeProvider(provider);app.exitQgis()
'''
    result = subprocess.run([sys.executable, '-c', code, str(target), str(scene)], cwd=target,
                            capture_output=True, text=True, timeout=60)
    print(result.stdout)
    if result.returncode:
        print(result.stderr)
        raise SystemExit(result.returncode)

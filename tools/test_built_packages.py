"""Verify local wheel/ZIP source identity and import the wheel from an isolated temp folder."""
from pathlib import Path
import os
import subprocess
import sys
import tempfile
import zipfile

ROOT = Path(__file__).resolve().parents[1]
wheel = ROOT/'dist/atiaf-1.0.2.dev1-py3-none-any.whl'
plugin = ROOT/'QGIS Tools/Distribution/ATIAF-QGIS-1.0.2.dev1.zip'
with zipfile.ZipFile(wheel) as whl, zipfile.ZipFile(plugin) as archive:
    for source in (ROOT/'atiaf_core').rglob('*'):
        if source.is_file() and '__pycache__' not in source.parts and source.suffix in ('.py', '.json'):
            relative = source.relative_to(ROOT).as_posix()
            assert whl.read(relative) == source.read_bytes(), f'Stale wheel source: {relative}'
            assert archive.read('atiaf/' + relative) == source.read_bytes(), f'Stale plugin core: {relative}'
    assert 'atiaf/icon.png' in archive.namelist()
    for source in (ROOT/'QGIS Tools'/'atiaf').rglob('*'):
        if source.is_file() and '__pycache__' not in source.parts and source.suffix in ('.py','.json','.txt','.png'):
            relative=source.relative_to(ROOT/'QGIS Tools').as_posix()
            assert archive.read(relative)==source.read_bytes(), f'Stale plugin source: {relative}'
    for language in ('en','ar'):
        for page in ('INDICATORS_CATALOG','MANUAL_BANDS','SURFACE_TEMPERATURE'):
            assert archive.read(f'atiaf/help/{language}/{page}.html') == (ROOT/'documentation'/language/(page+'.html')).read_bytes()
    assert not any(p.startswith('atyaf_core/') for p in whl.namelist())
with tempfile.TemporaryDirectory(prefix='atiaf_wheel_') as directory:
    install = subprocess.run([sys.executable, '-m', 'pip', 'install', '--no-index', '--no-deps', '--target', directory, str(wheel)],
                             capture_output=True, text=True, timeout=45)
    if install.returncode:
        raise RuntimeError(install.stderr)
    environment = dict(os.environ, PYTHONPATH=directory)
    result = subprocess.run([sys.executable, '-c', '''from pathlib import Path
import sys,atiaf_core
from atiaf_core.tool_contract import CATALOG
from atiaf_core.indices.registry import INDEX_CATALOG
assert Path(atiaf_core.__file__).is_relative_to(Path(sys.argv[1]))
assert len(CATALOG)==6 and 'NDVI' in INDEX_CATALOG
print('WHEEL PASS: isolated installed core, six catalogs, scientific imports')
''', directory], cwd=directory, env=environment, capture_output=True, text=True, timeout=30)
    print(result.stdout)
    if result.returncode:
        raise RuntimeError(result.stderr)
print('SOURCE IDENTITY PASS: wheel, QGIS core/adapter and bundled bilingual help match current source; icon included')

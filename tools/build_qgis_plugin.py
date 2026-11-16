"""Build a self-contained ATIAF plugin ZIP from reviewed project source, offline."""
from pathlib import Path
import argparse
import zipfile

ROOT = Path(__file__).resolve().parents[1]
import sys
sys.path.insert(0,str(ROOT))
from atiaf_core import __version__


def build(destination):
    destination = Path(destination).resolve()
    if destination.exists():
        raise FileExistsError(f'Preserving existing package: {destination}')
    destination.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(destination, 'x', zipfile.ZIP_DEFLATED) as archive:
        for source, prefix in [(ROOT/'QGIS Tools'/'atiaf', 'atiaf'), (ROOT/'atiaf_core', 'atiaf/atiaf_core')]:
            for path in sorted(source.rglob('*')):
                if path.is_file() and '__pycache__' not in path.parts and path.suffix in ('.py', '.json', '.txt', '.png'):
                    archive.write(path, f'{prefix}/{path.relative_to(source).as_posix()}')
        archive.write(ROOT/'LICENSE', 'atiaf/LICENSE')
        for path in (ROOT/'documentation').rglob('*'):
            if path.is_file() and path.suffix in ('.html', '.png') and (path.parent.name in ('ar','en','assets') or path.name == 'index.html'):
                archive.write(path, 'atiaf/help/' + path.relative_to(ROOT/'documentation').as_posix())
    return destination


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', default=f'QGIS Tools/Distribution/ATIAF-QGIS-{__version__}.zip')
    print(build(parser.parse_args().output))

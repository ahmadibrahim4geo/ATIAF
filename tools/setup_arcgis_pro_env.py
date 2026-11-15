"""Read-only ArcGIS dependency check. Install compatible packages in a cloned environment yourself."""
import importlib
import sys

def setup_env():
    errors = []
    print('ATIAF environment check (read-only):', sys.executable)
    for name in ('numpy', 'rasterio', 'shapely', 'pyproj'):
        try:
            mod = importlib.import_module(name)
            print(name, getattr(mod, '__version__', 'unknown'))
        except Exception as exc:
            errors.append(name)
            print('UNAVAILABLE:', name, type(exc).__name__)
    print('No packages installed. See documentation/en/INSTALLATION.md or documentation/ar/INSTALLATION.md.')
    return int(bool(errors))

if __name__ == '__main__':
    sys.exit(setup_env())

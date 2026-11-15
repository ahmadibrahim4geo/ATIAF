"""Atomic new-raster writer for derived products; never replace an existing result."""
from contextlib import contextmanager
from pathlib import Path
import uuid
import rasterio


@contextmanager
def atomic_raster(path, mode='w', **profile):
    path = Path(path)
    if mode != 'w' or path.exists():
        raise FileExistsError(f'Only new immutable raster writes are allowed: {path}')
    temporary = path.with_name('.tmp_' + uuid.uuid4().hex + '_' + path.name)
    try:
        with rasterio.open(temporary, 'w', **profile) as dataset:
            yield dataset
        with rasterio.open(temporary) as saved:
            saved.read(1, window=((0, 1), (0, 1)))
        if path.exists():
            raise FileExistsError(f'Preserving existing raster: {path}')
        temporary.rename(path)
    finally:
        if temporary.exists():
            temporary.unlink()  # Only this writer's private, generated partial file.

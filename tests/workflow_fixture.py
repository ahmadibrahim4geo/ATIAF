"""Small synthetic satellite products, never represented as real acquisitions."""
from pathlib import Path
import numpy as np
import rasterio


def make_scene(root, name='scene', platform=8, date='2023-05-20', red_dn=10909):
    scene = Path(root) / name
    scene.mkdir(parents=True)
    prefix = f'LC08_L2SP_176039_{date.replace("-", "")}_20230527_02_T1' if platform == 8 else f'LE07_L2SP_176039_{date.replace("-", "")}_20230527_02_T1'
    (scene / f'{prefix}_MTL.txt').write_text(f'LANDSAT_PRODUCT_ID = "{prefix}"\nSPACECRAFT_ID = "LANDSAT_{platform}"\nSENSOR_ID = "{"OLI_TIRS" if platform == 8 else "ETM"}"\nPROCESSING_LEVEL = "L2SP"\nDATE_ACQUIRED = "{date}"\n', 'utf-8')
    profile = dict(driver='GTiff', width=16, height=16, count=1, dtype='uint16', crs='EPSG:32636',
                   transform=rasterio.transform.from_origin(300000, 3300000, 30, 30), nodata=0)
    values = {2: 10000, 3: 12000, 4: red_dn, 5: 25455, 6: 15000, 7: 14000} if platform == 8 else {1: 10000, 2: 12000, 3: red_dn, 4: 25455, 5: 15000, 7: 14000}
    for band, value in values.items():
        arr = np.full((16, 16), value, dtype='uint16')
        arr[0, 2] = 0
        with rasterio.open(scene / f'{prefix}_SR_B{band}.TIF', 'w', **profile) as ds:
            ds.write(arr, 1)
    thermal = np.arange(256, dtype='uint16').reshape(16, 16) + 44000
    for suffix, arr in [(f'ST_B{10 if platform == 8 else 6}', thermal),
                        ('QA_PIXEL', np.full((16, 16), 64, dtype='uint16')),
                        ('QA_RADSAT', np.zeros((16, 16), dtype='uint16'))]:
        if suffix == 'QA_PIXEL':
            arr[0, 0] = 8
        if suffix == 'QA_RADSAT':
            arr[0, 1] = 1
        # QA zero is valid, so do not mark it NoData.
        p = dict(profile)
        if suffix.startswith('QA_'):
            p['nodata'] = None
        with rasterio.open(scene / f'{prefix}_{suffix}.TIF', 'w', **p) as ds:
            ds.write(arr, 1)
    return scene

"""Optional local display/interpretation classes; preserve the continuous scientific raster."""
import math
import numpy as np

DEFAULT_BREAKS = [0.2, 0.4, 0.6]
NAMES = {
    'en': ['Low green-vegetation signal / mixed or bare surface', 'Sparse green vegetation', 'Moderate green vegetation', 'Dense green vegetation'],
    'ar': ['إشارة خضرة منخفضة / سطح مختلط أو مكشوف', 'غطاء نباتي أخضر متناثر', 'غطاء نباتي أخضر متوسط', 'غطاء نباتي أخضر كثيف']}

def scheme(options):
    text = options.get('ndvi_breaks') or '0.2,0.4,0.6'
    breaks = [float(x.strip()) for x in text.split(',')]
    if len(breaks) != 3 or any(not math.isfinite(x) or not 0 < x < 1 for x in breaks) or breaks != sorted(set(breaks)):
        raise ValueError('NDVI classification requires three strictly ascending finite breaks inside (0,1)')
    if not str(options.get('classification_basis') or '').strip():
        raise ValueError('NDVI classification requires a local justification/validation basis; example breaks are not an international standard')
    return dict(id='NDVI_LOCAL_GREENNESS_V1', status='USER_DEFINED_NOT_INTERNATIONAL_STANDARD',
        source='Local illustrative ATIAF scheme, not an ecological standard; NASA/USGS explain qualitative NDVI response',
        original_breaks=DEFAULT_BREAKS, effective_breaks=breaks, labels=NAMES,
        basis=options['classification_basis'], interval='[lower, upper), final upper=1 inclusive',
        domain=[0,1], nodata=0, excluded='negative NDVI, out-of-range, nonfinite, source NoData/QA',
        warning='Greenness classes do not establish vegetation health, species, biomass or yield; validate locally')

def classify(values, effective):
    valid = np.isfinite(values) & (values >= 0) & (values <= 1)
    output = np.zeros(values.shape, dtype='uint8')
    output[valid] = np.searchsorted(effective['effective_breaks'], values[valid], side='right') + 1
    return output

def save(path, options):
    from pathlib import Path
    import json
    import rasterio
    from atiaf_core.raster.windowed import WindowedRasterEngine
    from atiaf_core.raster.workspace import WorkspaceManager
    effective = scheme(options)
    target = WorkspaceManager.unique_path(Path(path).with_name(Path(path).stem + '_LOCAL_CLASSES.tif'))
    # The scientific input and its run remain unchanged. The classified file is a new product.
    WindowedRasterEngine.process_bands({'ndvi': Path(path)}, target, lambda blocks: classify(blocks['ndvi'], effective),
        output_nodata=0, output_dtype='uint8', predictor=2)
    with rasterio.open(target) as ds:
        if ds.count != 1 or ds.nodata != 0:
            raise ValueError('Classified output failed readback')
    target.with_suffix('.legend.json').write_text(json.dumps(effective, ensure_ascii=False, indent=2), 'utf-8')
    return str(target), effective

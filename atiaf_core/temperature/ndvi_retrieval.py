"""Explicit RTE inversion using local radiance/atmosphere and user-parameterized NDVI emissivity.

Reference: Sobrino et al. 2004, doi:10.1016/j.rse.2004.02.003 (RTE/NDVI approach).
The linear soil/vegetation emissivity mixture here has no fixed universal coefficients,
water classifier or automatic atmospheric download. Real-product accuracy is not implied.
"""
import math
from pathlib import Path
import numpy as np

NUMBERS = ('planck_k1', 'planck_k2', 'transmittance', 'upwelling', 'downwelling',
           'ndvi_soil', 'ndvi_vegetation', 'emissivity_soil', 'emissivity_vegetation')

def validate(options, scene=None):
    for name in NUMBERS:
        value = options.get(name)
        if value in (None, '') or not math.isfinite(float(value)):
            raise ValueError('NDVI retrieval requires explicit finite input: ' + name)
    p = {k: float(options[k]) for k in NUMBERS}
    if p['planck_k1'] <= 0 or p['planck_k2'] <= 0 or not 0 < p['transmittance'] <= 1:
        raise ValueError('NDVI retrieval requires positive Planck constants and 0 < transmittance <= 1')
    if min(p['upwelling'], p['downwelling']) < 0 or not 0 <= p['ndvi_soil'] < p['ndvi_vegetation'] <= 1:
        raise ValueError('NDVI retrieval requires nonnegative radiance and ordered NDVI thresholds within [0,1]')
    if any(not 0 < p[k] <= 1 for k in ('emissivity_soil', 'emissivity_vegetation')):
        raise ValueError('NDVI retrieval emissivities must be in (0,1]')
    if not str(options.get('retrieval_provenance') or '').strip():
        raise ValueError('NDVI retrieval requires thermal/atmospheric/emissivity provenance')
    if not options.get('radiance_file') or not Path(options['radiance_file']).is_file():
        raise ValueError('NDVI retrieval requires a local calibrated thermal radiance raster, not official L2 ST or brightness temperature')
    if scene is not None:
        from atiaf_core.discovery.models import BandRole
        if scene.metadata.sensor_family.value != 'Landsat':
            raise ValueError('NDVI retrieval currently accepts Landsat thermal provenance only; optical-only sensors are not thermal')
        if options.get('ndvi_file'):
            if not Path(options['ndvi_file']).is_file():
                raise ValueError('Existing NDVI file does not exist')
        elif not all(scene.has_role(r) and scene.bands[r].unit == 'reflectance' for r in (BandRole.RED, BandRole.NIR)):
            raise ValueError('NDVI retrieval requires existing compatible NDVI or calibrated Red/NIR')
        import rasterio
        reference = next(iter(scene.bands.values())).file_path
        with rasterio.open(reference) as ref:
            for key in ('radiance_file', 'ndvi_file'):
                if not options.get(key):
                    continue
                with rasterio.open(options[key]) as ds:
                    if ds.count != 1 or not ds.crs or ds.crs != ref.crs or ds.transform != ref.transform or ds.shape != ref.shape:
                        raise ValueError('NDVI retrieval inputs must have the same known source CRS/grid/extent; align them explicitly first')
                    if key == 'radiance_file' and any(Path(options[key]).resolve() == a.file_path.resolve() and a.unit == 'Kelvin' for a in scene.bands.values()):
                        raise ValueError('Official L2 ST cannot be re-used as at-sensor radiance')
    return p

def retrieve(ndvi, radiance, parameters):
    p = parameters
    # Negative NDVI is deliberately excluded: it does not provide a universal water emissivity.
    valid = np.isfinite(ndvi) & np.isfinite(radiance) & (ndvi >= 0) & (ndvi <= 1) & (radiance > 0)
    pv = np.clip((ndvi - p['ndvi_soil']) / (p['ndvi_vegetation'] - p['ndvi_soil']), 0, 1) ** 2
    emissivity = p['emissivity_soil'] * (1 - pv) + p['emissivity_vegetation'] * pv
    surface = (radiance - p['upwelling'] - p['transmittance'] * (1-emissivity) * p['downwelling']) / (p['transmittance'] * emissivity)
    with np.errstate(divide='ignore', invalid='ignore'):
        kelvin = p['planck_k2'] / np.log1p(p['planck_k1'] / surface)
    return np.where(valid & (surface > 0) & np.isfinite(kelvin), kelvin, np.nan).astype('float32')

def run(scene, options, output_unit='Celsius', custom_destination=None, aoi_geometry=None, aoi_crs=None, **unused):
    from atiaf_core.discovery.models import BandRole
    from atiaf_core.raster.workspace import WorkspaceManager
    from atiaf_core.raster.windowed import WindowedRasterEngine
    from atiaf_core.raster.clip import PolygonClipEngine
    p = validate(options, scene)
    _, _, _, results, reports = WorkspaceManager.resolve_workspace_roots(scene.scene_path, custom_destination)
    name = 'LST_NDVI_RTE_' + output_unit.upper()
    path = WorkspaceManager.get_output_raster_path(results, 'Surface_Temperature', name, scene.metadata.scene_id)
    paths = {'radiance': Path(options['radiance_file'])}
    if options.get('ndvi_file'):
        paths['ndvi'] = Path(options['ndvi_file'])
    else:
        for key, role in [('red', BandRole.RED), ('nir', BandRole.NIR)]:
            paths[key] = scene.bands[role].file_path
    def compute(blocks):
        if 'ndvi' in blocks:
            ndvi = blocks['ndvi']
        else:
            red_asset, nir_asset = scene.bands[BandRole.RED], scene.bands[BandRole.NIR]
            red = blocks['red'] * red_asset.scale_factor + red_asset.offset
            nir = blocks['nir'] * nir_asset.scale_factor + nir_asset.offset
            with np.errstate(divide='ignore', invalid='ignore'):
                ndvi = np.where(nir + red != 0, (nir-red)/(nir+red), np.nan)
        kelvin = retrieve(ndvi, blocks['radiance'], p)
        return kelvin-273.15 if output_unit == 'Celsius' else kelvin
    metadata = WindowedRasterEngine.process_bands(paths, path, compute)
    clipped = None
    if aoi_geometry is not None:
        clipped = WorkspaceManager.get_output_raster_path(results, 'Surface_Temperature', name, scene.metadata.scene_id, is_clip=True, aoi_slug='AOI')
        PolygonClipEngine.clip_raster_file(path, clipped, aoi_geometry, aoi_crs=aoi_crs)
    record = dict(product_name=name, category='Surface_Temperature', method='NDVI_RTE_USER_MIXTURE', unit=output_unit,
        full_path=str(path), clipped_path=str(clipped) if clipped else None,
        statistics=metadata['statistics'], valid_pixels=metadata['valid_pixels'], nodata_pixels=metadata['nodata_pixels'])
    run_dir = WorkspaceManager.create_run_manifest(reports, scene.metadata.scene_id, '02_Surface_Temperature',
        dict(options, output_unit=output_unit, equation='Lsurface=(Lsensor-Lup-tau*(1-epsilon)*Ldown)/(tau*epsilon); T=K2/ln(1+K1/Lsurface)',
             method_scope='User-parameterized linear soil/vegetation emissivity mixture; negative NDVI masked; not official ST or validated field accuracy'),
        [record], {'executed_count': 1}, ['Local NDVI-assisted RTE retrieval; no downloads; scalar atmosphere assumes scene-wide applicability'])
    return dict(run_dir=str(run_dir), executed_products=[record])

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
    if scene is not None:
        plat = scene.metadata.platform.upper()
        if '8' in plat or '9' in plat:
            options.setdefault('planck_k1', 774.89)
            options.setdefault('planck_k2', 1321.08)
        elif '7' in plat:
            options.setdefault('planck_k1', 666.09)
            options.setdefault('planck_k2', 1282.71)
        elif '5' in plat or '4' in plat:
            options.setdefault('planck_k1', 607.76)
            options.setdefault('planck_k2', 1260.56)
        options.setdefault('transmittance', 1.0)
        options.setdefault('upwelling', 0.0)
        options.setdefault('downwelling', 0.0)
        options.setdefault('ndvi_soil', 0.2)
        options.setdefault('ndvi_vegetation', 0.5)
        options.setdefault('emissivity_soil', 0.96)
        options.setdefault('emissivity_vegetation', 0.985)
        options.setdefault('retrieval_provenance', 'USGS Landsat metadata calibration + Sobrino (2004) NDVI emissivity model')
        if not options.get('radiance_file'):
            from atiaf_core.discovery.models import BandRole
            th = scene.get_band(BandRole.THERMAL_1) or scene.get_band(BandRole.THERMAL_2)
            if th:
                options['radiance_file'] = str(th.file_path)

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
        th_asset = scene.get_band(BandRole.THERMAL_1) or scene.get_band(BandRole.THERMAL_2)
        rad_raw = blocks['radiance'].astype(np.float32)
        if th_asset and Path(options['radiance_file']).resolve() == th_asset.file_path.resolve() and th_asset.scale_factor != 1:
            radiance = rad_raw * th_asset.scale_factor + th_asset.offset
        elif options.get('apply_radiance_scale'):
            radiance = rad_raw * options.get('radiance_scale', 1.0) + options.get('radiance_offset', 0.0)
        else:
            radiance = rad_raw
        kelvin = retrieve(ndvi, radiance, p)
        return kelvin-273.15 if output_unit == 'Celsius' else kelvin
    metadata = WindowedRasterEngine.process_bands(paths, path, compute)
    clipped = None
    if aoi_geometry is not None:
        clipped = WorkspaceManager.get_output_raster_path(results, 'Surface_Temperature', name, scene.metadata.scene_id, is_clip=True, aoi_slug='AOI')
        PolygonClipEngine.clip_raster_file(path, clipped, aoi_geometry, aoi_crs=aoi_crs)
    record = dict(product_name=name, category='Surface_Temperature', method='NDVI_RTE_USER_MIXTURE', unit=output_unit,
        full_path=str(path), clipped_path=str(clipped) if clipped else None,
        statistics=metadata['statistics'], valid_pixels=metadata['valid_pixels'], nodata_pixels=metadata['nodata_pixels'])
    executed_records = [record]
    if not options.get('ndvi_file') and scene.has_role(BandRole.RED) and scene.has_role(BandRole.NIR):
        try:
            ndvi_path = WorkspaceManager.get_output_raster_path(results, 'Vegetation', 'NDVI', scene.metadata.scene_id)
            def compute_ndvi(b):
                ra, na = scene.bands[BandRole.RED], scene.bands[BandRole.NIR]
                r = b['red'] * ra.scale_factor + ra.offset
                n = b['nir'] * na.scale_factor + na.offset
                with np.errstate(divide='ignore', invalid='ignore'):
                    val = (n - r) / (n + r)
                    mask = (n + r > 0) & (r >= 0) & (n >= 0) & np.isfinite(val)
                    return np.where(mask, np.clip(val, -1.0, 1.0), np.nan).astype(np.float32)
            ndvi_meta = WindowedRasterEngine.process_bands({'red': scene.bands[BandRole.RED].file_path,
                                                            'nir': scene.bands[BandRole.NIR].file_path},
                                                           ndvi_path, compute_ndvi)
            ndvi_clipped = None
            if aoi_geometry is not None:
                ndvi_clipped = WorkspaceManager.get_output_raster_path(results, 'Vegetation', 'NDVI', scene.metadata.scene_id, is_clip=True, aoi_slug='AOI')
                PolygonClipEngine.clip_raster_file(ndvi_path, ndvi_clipped, aoi_geometry, aoi_crs=aoi_crs)
            executed_records.append(dict(product_name='NDVI', category='Vegetation', method='NDVI', unit='dimensionless (-1 to 1)',
                                         full_path=str(ndvi_path), clipped_path=str(ndvi_clipped) if ndvi_clipped else None,
                                         statistics=ndvi_meta['statistics'], valid_pixels=ndvi_meta['valid_pixels'], nodata_pixels=ndvi_meta['nodata_pixels']))
        except Exception:
            pass
    run_dir = WorkspaceManager.create_run_manifest(reports, scene.metadata.scene_id, '02_Surface_Temperature',
        dict(options, output_unit=output_unit, equation='Lsurface=(Lsensor-Lup-tau*(1-epsilon)*Ldown)/(tau*epsilon); T=K2/ln(1+K1/Lsurface)',
             method_scope='User-parameterized linear soil/vegetation emissivity mixture; negative NDVI masked; not official ST or validated field accuracy'),
        executed_records, {'executed_count': len(executed_records)}, ['Local NDVI-assisted RTE retrieval; no downloads; scalar atmosphere assumes scene-wide applicability'])
    return dict(run_dir=str(run_dir), executed_products=executed_records)

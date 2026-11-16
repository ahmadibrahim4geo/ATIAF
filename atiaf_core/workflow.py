"""Shared local workflow used by both native adapters. No host imports here."""
from collections import defaultdict
from copy import deepcopy
from datetime import datetime
from pathlib import Path
import json
import math
import re

from atiaf_core.tool_contract import CATALOG, SENSORS


def discover(folder, sensor='AUTO', expert_mapping=None, manual_options=None):
    from atiaf_core.discovery import SceneScanner
    from atiaf_core.discovery.models import BandRole, ProductLevel, SensorFamily
    from atiaf_core.discovery.manual_mapper import ManualBandMapper
    folder = Path(folder).resolve()
    if not folder.is_dir():
        raise ValueError(f'Input folder does not exist: {folder}')
    if sensor not in SENSORS:
        raise ValueError(f'Unknown sensor choice: {sensor}')
    if manual_options and manual_options.get('manual_mode'):
        from atiaf_core.manual_input import manual_scene
        return manual_scene(folder, sensor, manual_options)
    if sensor == 'EXPERT':
        if not expert_mapping:
            raise ValueError('EXPERT requires an explicit mapping JSON; see documentation/en/EXPERT_MAPPING.md')
        mapping_path = Path(expert_mapping)
        if mapping_path.stat().st_size > 1024 * 1024:
            raise ValueError('Expert mapping exceeds 1 MiB')
        data = json.loads(mapping_path.read_text('utf-8'))
        mappings, scales, offsets, units = {}, {}, {}, {}
        for role_name, item in data['bands'].items():
            role = BandRole(role_name)
            asset_path = (folder / item['file']).resolve()
            if not asset_path.is_relative_to(folder) or not asset_path.is_file():
                raise ValueError(f'Band must be a local file inside the input scene: {role_name}')
            for key in ('scale', 'offset', 'wavelength_nm'):
                if not math.isfinite(float(item[key])):
                    raise ValueError(f'Explicit finite calibration and wavelength required: {role_name}')
            if item['unit'] not in ('reflectance', 'Kelvin'):
                raise ValueError('Only explicitly calibrated reflectance or official surface Kelvin is accepted')
            if not item.get('provenance'):
                raise ValueError(f'Calibration provenance required: {role_name}')
            windows = {'blue': (400, 520), 'green': (500, 610), 'red': (600, 700),
                       'nir': (740, 1000), 'narrow_nir': (800, 900), 'swir_1': (1400, 1800),
                       'swir_2': (2000, 2400), 'red_edge_1': (680, 750),
                       'thermal_1': (8000, 14000), 'thermal_2': (8000, 14000)}
            if role_name not in windows or not windows[role_name][0] <= float(item['wavelength_nm']) <= windows[role_name][1]:
                raise ValueError(f'Wavelength does not match the physical band role: {role_name}')
            if float(item['scale']) <= 0:
                raise ValueError(f'Positive explicit scale required: {role_name}')
            if role_name.startswith('thermal') and data.get('thermal_semantics') != 'official_surface_temperature':
                raise ValueError('Official surface temperature provenance is required; brightness temperature is not LST')
            mappings[role], scales[role], offsets[role], units[role] = asset_path, float(item['scale']), float(item['offset']), item['unit']
        scene = ManualBandMapper.create_custom_scene(
            folder, data['scene_id'], data['platform'], data['instrument'], ProductLevel(data['product_level']),
            mappings, scales, offsets, units, datetime.fromisoformat(data['acquisition_date']))
        scene.metadata.sensor_family = SensorFamily(data['sensor_family'])
        scene.metadata.metadata_file = mapping_path.resolve()
        for role, asset in scene.bands.items():
            asset.center_wavelength_nm = float(data['bands'][role.value]['wavelength_nm'])
            asset.calibration_provenance = data['bands'][role.value]['provenance']
        return [scene]
    if expert_mapping:
        raise ValueError('Expert mapping is only read when sensor is EXPERT')
    scenes = SceneScanner.scan(folder).scenes
    if not scenes:
        raise ValueError('No recognized satellite metadata and band assets found in this folder')
    for scene in scenes:
        m = scene.metadata
        if not m.metadata_file or not m.metadata_file.is_file():
            raise ValueError(f'Real product metadata is required: {m.scene_id}')
        platform = m.platform.upper().replace(' ', '_')
        match = sensor == 'AUTO'
        if sensor.startswith('LANDSAT_'):
            platforms = {'LANDSAT_8_9_C2_L2': ['LANDSAT_8', 'LANDSAT_9'],
                         'LANDSAT_7_C2_L2': ['LANDSAT_7'], 'LANDSAT_4_5_C2_L2': ['LANDSAT_4', 'LANDSAT_5']}[sensor]
            match = (platform in platforms and m.product_level.value in ('L2_SR', 'L2_ST')
                     and (m.collection=='02' or scene.expert_mapped))
        elif sensor.startswith('SENTINEL_2'):
            match = m.sensor_family.value == 'Sentinel-2' and m.product_level.value == ('L2A_BOA' if sensor.endswith('L2A') else 'L1C_TOA')
        elif sensor.startswith('ASTER_'):
            match = m.sensor_family.value == 'ASTER' and m.product_level.value == sensor.removeprefix('ASTER_')
        if not match:
            raise ValueError(f'Sensor/product mismatch: selected {sensor}; metadata says {m.platform}, {m.product_level.value}')
    return scenes


def unavailable_reason(tool, calculation, scene, options=None):
    from atiaf_core.discovery.models import BandRole
    rows = {row['id']: row for row in CATALOG[tool]}
    if calculation not in rows:
        return 'Unknown calculation ID'
    m = scene.metadata
    if m.sensor_family.value in ('Sentinel-1', 'ALOS PALSAR'):
        return 'Radar cannot be processed with optical/thermal equations'
    if tool == 'surface_temperature' and calculation in ('LST', 'LST_CELSIUS', 'LST_KELVIN') and (options or {}).get('ndvi_assisted'):
        try:
            from atiaf_core.temperature.ndvi_retrieval import validate
            validate(options, scene)
            return ''
        except (ValueError, OSError) as exc:
            return str(exc)
    if calculation in ('TCB', 'TCG', 'TCW', 'NDWI_GAO'):
        return 'Sensor, wavelength and product-level coefficients require scientific review'
    if calculation in ('TVDI', 'VCI_TCI_VHI', 'SUHI', 'EMISSIVITY_NDVI'):
        return {'TVDI': 'Validated NDVI-dependent dry/wet edges are required; temperature min/max is not TVDI',
                'VCI_TCI_VHI': 'A justified historical reference baseline is required',
                'SUHI': 'Urban and rural reference masks are required',
                'EMISSIVITY_NDVI': 'Emissivity method and scene-wide thresholds require review'}[calculation]
    if tool == 'temporal_change':
        return unavailable_reason('surface_temperature' if calculation == 'LST' else 'spectral_indices',
                                  'LST_CELSIUS' if calculation == 'LST' else calculation, scene)
    thermal = tool in ('surface_temperature', 'thermal_urban')
    if thermal:
        band = scene.bands.get(BandRole.THERMAL_1)
        if not band or not band.file_path.is_file():
            return 'Thermal infrared band is required; optical-only imagery cannot provide LST'
        if band.unit != 'Kelvin' and m.product_level.value not in ('L2_SR', 'L2_ST', 'AST_08'):
            if not (options or {}).get('allow_toa') and not (options or {}).get('ndvi_assisted'):
                return 'Official L2 surface temperature product required; for legacy L1 imagery enable allow_toa or ndvi_assisted for calibrated thermal retrieval'
    if tool == 'environmental_drought':
        if m.platform.upper().replace(' ', '_') not in ('LANDSAT_4', 'LANDSAT_5', 'LANDSAT_7'):
            return 'Current albedo coefficients are restricted to Landsat TM/ETM+; other sensors require review'
        roles = ['blue', 'red', 'nir', 'swir_1', 'swir_2']
    else:
        roles = rows[calculation].get('roles', [])
    if roles and m.product_level.value not in ('L2_SR', 'L2A_BOA', 'AST_07'):
        if not (((tool == 'spectral_indices' and calculation == 'NDVI') or tool == 'geological_analysis')
                and (options or {}).get('allow_toa') and m.radiometric_unit == 'toa_reflectance'):
            return ('Validated surface reflectance product required; this product is ' + str(m.product_generation or m.product_level.value) +
                    '. Enable allow_toa to calculate diagnostic ratios from calibrated TOA; TOA/DN is not surface reflectance')
    for role in roles:
        if not scene.has_role(BandRole(role)):
            return f'Missing physical band: {role}'
        if scene.bands[BandRole(role)].unit != 'reflectance':
            return f'Calibrated reflectance and provenance required: {role}'
    if tool == 'geological_analysis':
        from atiaf_core.geology import GeologicalAnalysisEngine
        if calculation not in {d.id for d in GeologicalAnalysisEngine.get_supported_indices_for_scene(scene)}:
            return 'Sensor band/date restrictions are not satisfied (including ASTER SWIR after April 2008)'
        if calculation.startswith('ASTER'):
            return 'Exact ASTER band semantics and product reader require validation'
    return ''


def preflight(tool, scenes, selected, apply_qa=True, mosaic=False, output_crs=None, options=None):
    import rasterio
    import numpy as np
    from pyproj import CRS
    if not selected:
        raise ValueError('Select at least one calculation; nothing is selected by default')
    options = options or {}
    if options.get('ndvi_assisted') and len(scenes) != 1:
        raise ValueError('NDVI retrieval currently requires one scene with matching local ancillary inputs')
    if options.get('classify_ndvi'):
        if tool != 'spectral_indices' or 'NDVI' not in selected:
            raise ValueError('NDVI classification requires selecting the NDVI calculation')
        from atiaf_core.classification import scheme
        scheme(options)
    for scene in scenes:
        if not re.fullmatch(r'[\w.-]{1,160}', scene.metadata.scene_id, re.ASCII) or '..' in scene.metadata.scene_id:
            raise ValueError('Scene ID contains unsafe filename characters')
        for calc in selected:
            reason = unavailable_reason(tool, calc, scene, options)
            if reason:
                raise ValueError(f'{scene.metadata.scene_id} / {calc}: {reason}')
        if apply_qa:
            expected = 'QA_PIXEL' if scene.metadata.sensor_family.value == 'Landsat' else 'SCL'
            from atiaf_core.raster.masks import QualityMaskEngine
            acceptable=(expected,)+QualityMaskEngine.LEGACY_SCHEMAS if expected=='QA_PIXEL' else (expected,)
            if not any(key in scene.quality_masks for key in acceptable):
                raise ValueError(f'{scene.metadata.scene_id}: requested quality mask {expected} is absent; supply it or explicitly turn QA off')
        for band in scene.bands.values():
            with rasterio.open(band.file_path) as ds:
                if ds.count != 1:
                    raise ValueError('Band assets must be single-band rasters; export the correct physical band first')
                if not scene.expert_mapped and (band.scale_factor != 1 or band.offset != 0) and np.issubdtype(np.dtype(ds.dtypes[0]), np.floating):
                    raise ValueError('Floating-point raster conflicts with raw DN product scaling; use verified expert scale/offset to avoid double calibration')
                if not ds.crs:
                    raise ValueError(f'Unknown source CRS: {band.file_path.name}; define the correct source CRS first')
                crs = CRS.from_user_input(output_crs or ds.crs)
                if not crs.is_projected or not crs.axis_info or any(abs(a.unit_conversion_factor - 1) > 1e-9 for a in crs.axis_info[:2]):
                    raise ValueError(f'Decision D-007: choose a projected metre CRS; received {crs.to_string()}')
                if ds.width * ds.height > 16_000_000 and tool in ('thermal_urban', 'environmental_drought', 'temporal_change'):
                    if not ((options or {}).get('allow_large_scene') or (options or {}).get('aoi_geometry')):
                        raise ValueError('This scene exceeds the bounded in-memory analysis limit; large-scene streaming is pending')
                if output_crs:
                    from pyproj.transformer import TransformerGroup
                    tg = TransformerGroup(ds.crs, output_crs, always_xy=True, allow_ballpark=False)
                    if not tg.transformers or not tg.best_available:
                        raise ValueError('Required datum transformation/grid is unavailable; no automatic grid download')
    if mosaic and len(scenes) > 1:
        keys = {(s.metadata.sensor_id, s.metadata.product_level.value,s.metadata.product_generation,
                 s.metadata.acquisition_date.date() if s.metadata.acquisition_date else None) for s in scenes}
        if len(keys) != 1 or next(iter(keys))[3] is None:
            raise ValueError('Mosaic requires matching sensor, product level and acquisition day; cross-date harmonization is not validated')
        if not output_crs:
            crss = set()
            for scene in scenes:
                with rasterio.open(next(iter(scene.bands.values())).file_path) as ds:
                    crss.add(ds.crs.to_wkt())
            if len(crss) != 1:
                raise ValueError('Choose a common output CRS before mosaicking scenes from different CRSs')


def run_tool(tool, input_folder, selected, sensor='AUTO', expert_mapping=None, apply_qa=True,
             mosaic=False, aoi_geometry=None, aoi_crs=None, output_crs=None, output_folder=None,
             second_folder=None, canceled=lambda: False, progress=lambda message: None, language='en', options=None):
    """Validate the whole request before writes. Return immutable outputs plus manifest paths."""
    if tool == 'geological_composites':
        from atiaf_core.composites.engine import run
        return run(input_folder, selected, sensor=sensor, options=options, apply_qa=apply_qa, mosaic=mosaic,
                   output_crs=output_crs, output_folder=output_folder, aoi_geometry=aoi_geometry, aoi_crs=aoi_crs,
                   language=language, canceled=canceled, progress=progress)
    from atiaf_core.execution_context import RUN_OPTIONS
    from atiaf_core.indices import SpectralIndicesEngine
    from atiaf_core.temperature import SurfaceTemperatureEngine
    from atiaf_core.geology import GeologicalAnalysisEngine
    from atiaf_core.environment import EnvironmentalDroughtEngine
    from atiaf_core.urban import ThermalUrbanEngine
    from atiaf_core.raster import WorkspaceManager
    import rasterio
    folder = Path(input_folder).resolve()
    options = dict(options or {})
    if aoi_geometry is not None:
        options['aoi_geometry'] = True
    scenes = discover(folder, sensor, expert_mapping, manual_options=options)
    preflight(tool, scenes, selected, apply_qa, mosaic, output_crs, options)
    if aoi_geometry is not None and (not aoi_crs or aoi_geometry.is_empty or not aoi_geometry.is_valid or aoi_geometry.geom_type not in ('Polygon', 'MultiPolygon')):
        raise ValueError('AOI requires valid, nonempty polygon geometry and a known source CRS')
    destination = Path(output_folder).resolve() if output_folder else None
    if destination == folder:
        destination = None  # Default parent means each scene stays in its own folder.
    epochs = None
    if tool == 'temporal_change':
        if sensor == 'EXPERT' or options.get('manual_mode'):
            raise ValueError('Temporal comparison does not yet accept two independent expert mappings')
        if not second_folder:
            raise ValueError('Select the second epoch folder')
        epochs = discover(second_folder, sensor, expert_mapping)
        preflight(tool, epochs, selected, apply_qa, mosaic, output_crs)
        if len(scenes) != 1 or len(epochs) != 1:
            raise ValueError('Temporal comparison currently requires one scene per epoch; parent mosaics are gated')
        a, b = scenes[0].metadata, epochs[0].metadata
        if a.sensor_id != b.sensor_id or a.product_level != b.product_level:
            raise ValueError('Temporal comparison requires matching sensor and product level')
        if not a.acquisition_date or not b.acquisition_date or a.acquisition_date >= b.acquisition_date:
            raise ValueError('Epoch dates must be known, distinct and ordered T1 before T2')
    outputs, manifests, grouped = [], [], defaultdict(list)
    for scene in scenes:
        if canceled():
            raise InterruptedError('ATIAF run canceled; already saved outputs are preserved')
        progress(scene.metadata.scene_id)
        token = RUN_OPTIONS.set(dict(output_crs=output_crs, source_scene=scene.to_dict(),
                                     quality_masks=scene.quality_masks if apply_qa else {},
                                     qa_mask_mode=options.get('qa_mask_mode', 'Cloud_Only_Arid') if apply_qa else 'None',
                                     sensor_family=scene.metadata.sensor_family.value, selected=list(selected), language=language,
                                     user_options=options, study_area_name=options.get('study_area_name'),
                                     canceled=canceled, scientific_definitions=[r for r in CATALOG[tool] if r['id'] in selected]))
        try:
            common = dict(scene=scene, custom_destination=destination, aoi_geometry=aoi_geometry,
                          aoi_crs=aoi_crs, apply_qa_mask=apply_qa)
            results = []
            if tool == 'spectral_indices':
                results = [SpectralIndicesEngine.run_scene_indices(selected_index_ids=selected, **common)]
            elif tool == 'geological_analysis':
                results = [GeologicalAnalysisEngine.run_geological_analysis(selected_index_ids=selected, **common)]
            elif tool == 'surface_temperature':
                for calc in selected:
                    unit = options.get('temperature_unit', 'Celsius') if calc == 'LST' else ('Kelvin' if calc == 'LST_KELVIN' else 'Celsius')
                    if unit not in ('Celsius', 'Kelvin'):
                        raise ValueError('Unknown temperature output unit')
                    if options.get('ndvi_assisted'):
                        from atiaf_core.temperature.ndvi_retrieval import run
                        results.append(run(options=options, output_unit=unit, **common))
                    else:
                        results.append(SurfaceTemperatureEngine.run_surface_temperature(method='Official_L2_ST', output_unit=unit, **common))
            elif tool == 'thermal_urban':
                results = [ThermalUrbanEngine.run_thermal_urban_analysis(selected_calculations=selected, **common)]
            elif tool == 'environmental_drought':
                results = [EnvironmentalDroughtEngine.run_environmental_analysis(calculate_albedo='ALBEDO' in selected, calculate_tvdi=False, **common)]
            elif tool == 'temporal_change':
                from atiaf_core.temporal import ChangeDetectionEngine
                for calc in selected:
                    pair = []
                    for epoch in [scene, epochs[0]]:
                        nested = run_tool('surface_temperature' if calc == 'LST' else 'spectral_indices', epoch.scene_path,
                                          ['LST_CELSIUS'] if calc == 'LST' else [calc], sensor=sensor, apply_qa=apply_qa,
                                          output_crs=output_crs, output_folder=destination, canceled=canceled)
                        pair.append(nested['OUTPUT_RASTERS'][0])
                    results.append(ChangeDetectionEngine.run_change_detection(
                        Path(pair[0]), Path(pair[1]), scene.metadata.scene_id, epochs[0].metadata.scene_id,
                        scene.metadata.acquisition_date.isoformat(), epochs[0].metadata.acquisition_date.isoformat(),
                        calc, destination or folder, calc_relative=False, aoi_geometry=aoi_geometry, aoi_crs=aoi_crs))
            for result in results:
                manifests.append(result['run_dir'])
                if options.get('manual_mode') and not options.get('expert_mapping'):
                    from atiaf_core.ui_schema import fields
                    manual_keys = {s['name'] for s in fields(tool) if s['group'] == 'Manual'} - {'expert_mapping'}
                    mapping = dict(format='atiaf_manual_v1', sensor=sensor,
                        values={k:v for k,v in options.items() if k in manual_keys})
                    mapping_path = Path(result['run_dir'])/'Manual_Band_Mapping.json'
                    with mapping_path.open('x', encoding='utf-8') as stream:
                        json.dump(mapping, stream, ensure_ascii=False, indent=2)
                for record in result['executed_products']:
                    path = record.get('clipped_path') or record['full_path']
                    with rasterio.open(path) as ds:
                        if not ds.crs or ds.width < 1 or ds.height < 1:
                            raise ValueError(f'Output failed readback: {path}')
                        ds.read(1, window=((0, 1), (0, 1)))
                    outputs.append(path)
                    if options.get('classify_ndvi') and tool == 'spectral_indices' and record.get('index_id') == 'NDVI':
                        from atiaf_core.classification import save
                        classified_path, effective = save(path, options)
                        outputs.append(classified_path)
                        _, _, _, _, reports = WorkspaceManager.resolve_workspace_roots(scene.scene_path, destination)
                        class_record = dict(product_name='NDVI_LOCAL_CLASSES', unit='class code',
                            full_path=classified_path, source_continuous_path=path, classification=effective)
                        manifests.append(str(WorkspaceManager.create_run_manifest(reports, scene.metadata.scene_id,
                            '01_NDVI_Local_Classification', effective, [class_record], {'executed_count':1},
                            ['Continuous NDVI preserved; local example classes are not an international standard'])))
                    grouped[record.get('index_id') or record.get('product_name') or record['acronym']].append((scene, Path(record['full_path'])))
        finally:
            RUN_OPTIONS.reset(token)
    if mosaic and len(scenes) > 1:
        from atiaf_core.mosaic import QualityMosaicEngine
        for product, pairs in grouped.items():
            result = QualityMosaicEngine.run_mosaic(pairs, product, tool, destination or folder,
                                                    aoi_geometry=aoi_geometry, aoi_crs=aoi_crs)
            outputs.append(str(result.clipped_path or result.full_path))
    if not outputs:
        raise ValueError('No raster outputs produced; inspect calculation eligibility and reports')
    return {'OUTPUT_FOLDER': str(destination or folder), 'OUTPUT_RASTERS': outputs, 'RUN_MANIFESTS': manifests}

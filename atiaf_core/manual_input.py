"""Explicit local file mapping when scene metadata is incomplete; no guessed calibration."""
from datetime import datetime
from pathlib import Path
import math
from atiaf_core.ui_schema import ROLES

def manual_scene(folder, sensor, values):
    from atiaf_core.discovery.models import BandRole, ProductLevel, SensorFamily, QualityAsset
    from atiaf_core.discovery.manual_mapper import ManualBandMapper
    from atiaf_core.workflow import discover
    profiles = {
        'LANDSAT_8_9_C2_L2': ('Landsat', 'OLI_TIRS', 'L2_SR', ('LANDSAT_8', 'LANDSAT_9')),
        'LANDSAT_7_C2_L2': ('Landsat', 'ETM+', 'L2_SR', ('LANDSAT_7',)),
        'LANDSAT_4_5_C2_L2': ('Landsat', 'TM', 'L2_SR', ('LANDSAT_4', 'LANDSAT_5')),
        'SENTINEL_2_L2A': ('Sentinel-2', 'MSI', 'L2A_BOA', ('SENTINEL_2A', 'SENTINEL_2B', 'SENTINEL_2C')),
    }
    if sensor not in profiles:
        raise ValueError('Manual mapping requires a supported actual sensor/product, not AUTO or EXPERT')
    family, instrument, level, platforms = profiles[sensor]
    if values.get('expert_mapping'):
        import json
        mapping_path = Path(values['expert_mapping'])
        if not mapping_path.is_file() or mapping_path.stat().st_size > 1024*1024:
            raise ValueError('Saved manual mapping must be a local JSON file under 1 MiB')
        document = json.loads(mapping_path.read_text('utf-8'))
        if document.get('format') == 'atiaf_manual_v1':
            if document.get('sensor') != sensor:
                raise ValueError('Imported manual mapping does not match the selected sensor/product')
            from atiaf_core.ui_schema import fields
            allowed = {s['name'] for s in fields('spectral_indices') if s['group'] == 'Manual'} - {'expert_mapping'}
            restored = {k:v for k,v in document['values'].items() if k in allowed}
            return manual_scene(folder, sensor, restored)
        scenes = discover(folder, 'EXPERT', values['expert_mapping'])
        for scene in scenes:
            if scene.metadata.sensor_family.value != family or scene.metadata.platform.upper().replace(' ', '_') not in platforms or scene.metadata.product_level.value != level:
                raise ValueError('Imported manual mapping does not match the selected sensor/product')
        return scenes
    platform = str(values.get('manual_platform') or '').upper().replace(' ', '_').replace('-', '_')
    if platform not in platforms:
        raise ValueError('Manual platform does not match the selected sensor/product')
    if not str(values.get('manual_provenance') or '').strip():
        raise ValueError('Manual calibration provenance is required')
    date = datetime.fromisoformat(values.get('manual_date') or '')
    mappings, scales, offsets, units = {}, {}, {}, {}
    def number(key):
        value = values.get(key)
        if value is None or value == '' or not math.isfinite(float(value)):
            raise ValueError('Explicit finite manual calibration required: ' + key)
        return float(value)
    for name in ROLES:
        if not values.get('band_' + name):
            continue
        role, path = BandRole(name), Path(values['band_' + name]).resolve()
        if not path.is_file():
            raise ValueError('Mapped local band does not exist: ' + name)
        thermal = name.startswith('thermal')
        if thermal and family != 'Landsat':
            raise ValueError('Optical-only sensor cannot supply an official thermal band')
        scale = number('manual_thermal_scale' if thermal else 'manual_scale')
        if scale <= 0:
            raise ValueError('Manual calibration scale must be positive')
        mappings[role], scales[role] = path, scale
        offsets[role] = number('manual_thermal_offset' if thermal else 'manual_offset')
        units[role] = 'Kelvin' if thermal else 'reflectance'
    if not mappings:
        raise ValueError('Select at least one available manual band file')
    scene = ManualBandMapper.create_custom_scene(Path(folder).resolve(), Path(folder).resolve().name,
        platform, instrument, ProductLevel(level), mappings, scales, offsets, units, date)
    scene.metadata.sensor_family = SensorFamily(family)
    scene.metadata.sensor_id = platform + '_' + instrument
    # Wavelengths are sensor-profile context, never values claimed read from missing metadata.
    centers = ({'blue': 482, 'green': 561, 'red': 655, 'nir': 865, 'swir_1': 1609, 'swir_2': 2201, 'thermal_1': 10895}
               if platform in ('LANDSAT_8', 'LANDSAT_9') else
               {'blue': 485, 'green': 560, 'red': 660, 'nir': 835, 'swir_1': 1650, 'swir_2': 2220, 'thermal_1': 11450})
    for role, asset in scene.bands.items():
        if family == 'Landsat' and role.value not in centers:
            raise ValueError('Selected sensor has no such physical band: ' + role.value)
        if family == 'Landsat':
            asset.center_wavelength_nm = centers[role.value]
        asset.calibration_provenance = str(values['manual_provenance'])
    if values.get('manual_qa'):
        path = Path(values['manual_qa']).resolve()
        if not path.is_file():
            raise ValueError('Manual quality mask does not exist')
        key = 'QA_PIXEL' if family == 'Landsat' else 'SCL'
        scene.quality_masks[key] = QualityAsset(key, path)
    return [scene]

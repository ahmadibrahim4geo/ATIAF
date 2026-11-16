"""Local RGB workflow with exact-band provenance and bounded analytical writes."""
from contextlib import ExitStack
from copy import deepcopy
from datetime import datetime, timedelta
import json
import hashlib
import math
from pathlib import Path
import re
import shutil
import tempfile
import uuid

import numpy as np
import rasterio
from rasterio.enums import ColorInterp, Resampling
from rasterio.vrt import WarpedVRT
from pyproj import CRS

from atiaf_core.composites.expressions import parse, calculate
from atiaf_core.composites.registry import PRESETS, DEFAULTS, DISCLAIMER, CENTERS_NM, SPECTRAL_SOURCES
from atiaf_core.composites import render
from atiaf_core.discovery.models import SceneInfo, SceneMetadata, SensorFamily, ProductLevel
from atiaf_core.execution_context import RUN_OPTIONS
from atiaf_core.raster.workspace import WorkspaceManager
from atiaf_core.raster.windowed import WindowedRasterEngine


def read_json(path):
    path = Path(path)
    if not path.is_file() or path.stat().st_size > 1024*1024:
        raise ValueError('Composite preset must be a local JSON file no larger than 1 MiB')
    data=json.loads(path.read_text('utf-8'))
    if not isinstance(data,dict): raise ValueError('Composite preset JSON must be an object')
    return data


def scientific_id(name):
    match = re.fullmatch(r'(?:SR_)?B0?([1-9]|1[0-2]|3N|8A)',name.upper())
    if not match:
        raise ValueError('Composite unknown scientific band ID: '+name)
    return 'B'+match[1]


def asset(path,index,scale,offset,source,**extra):
    return dict(path=Path(path),index=int(index),scale=float(scale),offset=float(offset),provenance=source,**extra)


def legacy_landsat(folder):
    """Compatibility adapter to the shared metadata-first reader; no duplicate decoder."""
    from atiaf_core.discovery.landsat import LandsatParser
    scene=LandsatParser.parse(folder)
    if scene is None or scene.metadata.product_generation!='PRE_COLLECTION' or scene.metadata.platform!='Landsat 8': return None
    assets={a.band_name:asset(a.file_path,1,a.scale_factor,a.offset,a.calibration_provenance,
        valid_min=a.valid_min,valid_max=a.valid_max,unit=scene.metadata.radiometric_unit,wavelength_nm=a.center_wavelength_nm)
        for a in scene.bands.values() if a.unit=='reflectance' and not a.is_thermal}
    return dict(scene=scene,assets=assets,family='LANDSAT_8_9',qa=None,qa_schema='BQA_PRECOLLECTION',
                level=scene.metadata.radiometric_unit,warnings=scene.metadata.warnings+
                ['Pre-Collection BQA has no cloud-shadow or per-band saturation flags; raw 0/65535 excluded.'])


def stack_scene(folder,sensor,options):
    path = Path(options['stack_raster']).resolve()
    if not path.is_file(): raise ValueError('Composite multiband raster is missing')
    family = ('LANDSAT_8_9' if sensor=='LANDSAT_8_9_C2_L2' else 'SENTINEL_2' if sensor in ('SENTINEL_2_L2A','SENTINEL_2_L1C')
              else 'ASTER' if sensor=='ASTER_AST_07' else None)
    if not family: raise ValueError('Composite multiband mapping requires an explicit supported sensor, not AUTO')
    names = [scientific_id(x.strip()) for x in str(options.get('stack_band_ids','')).split(',') if x.strip()]
    if any(n not in CENTERS_NM[family] for n in names):
        raise ValueError('Composite scientific band IDs do not belong to the selected optical sensor; ASTER uses B3N')
    try:
        scales = [float(x.strip()) for x in str(options.get('stack_scales','')).split(',')]
        offsets = [float(x.strip()) for x in str(options.get('stack_offsets','')).split(',')]
        date = datetime.fromisoformat(options['stack_date'])
    except (ValueError,KeyError,TypeError) as exc:
        raise ValueError('Composite stack requires explicit date, scales and offsets') from exc
    source = str(options.get('stack_provenance') or '').strip()
    if not source: raise ValueError('Composite stack calibration provenance is required')
    with rasterio.open(path) as ds:
        if ds.count != len(names) or len(set(names))!=len(names):
            raise ValueError('Composite stack band IDs must uniquely describe every file position in order')
    for values in (scales,offsets):
        if len(values) not in (1,len(names)) or not np.all(np.isfinite(values)):
            raise ValueError('Composite stack calibration must have one value or one per band')
    if min(scales)<=0: raise ValueError('Composite stack scales must be positive')
    unit = options.get('stack_level') or 'surface_reflectance'
    if unit not in ('surface_reflectance','toa_reflectance'): raise ValueError('Composite unknown stack reflectance level')
    expected='toa_reflectance' if sensor=='SENTINEL_2_L1C' else 'surface_reflectance'
    if unit!=expected: raise ValueError('Composite stack physical level conflicts with the selected product; choose its correct profile')
    if family=='SENTINEL_2' and unit=='surface_reflectance' and 'B10' in names:
        raise ValueError('Composite Sentinel-2 L2A does not provide a surface-reflectance B10 cirrus band')
    sf = {'LANDSAT_8_9':SensorFamily.LANDSAT,'SENTINEL_2':SensorFamily.SENTINEL_2,'ASTER':SensorFamily.ASTER}[family]
    level = ProductLevel.L2_SR if family=='LANDSAT_8_9' else ProductLevel.AST_07 if family=='ASTER' else (
        ProductLevel.L1C_TOA if unit=='toa_reflectance' else ProductLevel.L2A_BOA)
    scene_id=re.sub(r'[^A-Za-z0-9_.-]+','_',folder.name).strip('_.-')[:100] or 'CustomScene'
    scene_id+='_'+hashlib.sha256(str(folder).encode('utf-8')).hexdigest()[:8]
    scene = SceneInfo(folder,SceneMetadata(scene_id,sf,sensor,sensor,sensor,level,date),expert_mapped=True)
    assets = {name:asset(path,i+1,scales[min(i,len(scales)-1)],offsets[min(i,len(offsets)-1)],source,
                   unit=unit) for i,name in enumerate(names)}
    return dict(scene=scene,assets=assets,family=family,level=unit,qa=None,qa_schema=None,
                warnings=['Explicit user multiband mapping; raw stack is not inferred to be calibrated.'])


def sources(folder,sensor,options):
    folder=Path(folder).resolve()
    if not folder.is_dir(): raise ValueError('Composite input folder is missing')
    if options.get('stack_mode'):
        if not options.get('stack_raster'): raise ValueError('Composite stack mode requires its raster file')
        return [stack_scene(folder,sensor,options)]
    candidates=[folder]+[p for p in folder.iterdir() if p.is_dir() and not p.name.startswith('.') and p.name.upper() not in ('WORK','RESULTS','REPORTS')]
    legacy=[x for p in candidates if (x:=legacy_landsat(p)) is not None]
    from atiaf_core.discovery import SceneScanner
    from atiaf_core.workflow import discover
    scanned=SceneScanner.scan(folder).scenes
    legacy_paths={x['scene'].scene_path for x in legacy}
    for scene in scanned:
        if scene.scene_path in legacy_paths: continue
        # Reuse standard sensor mismatch checks for recognized metadata products.
        checked=discover(scene.scene_path,sensor)[0]
        family = 'LANDSAT_8_9' if checked.metadata.platform.upper().replace(' ','_') in ('LANDSAT_8','LANDSAT_9') else (
            'SENTINEL_2' if checked.metadata.sensor_family==SensorFamily.SENTINEL_2 else 'ASTER' if checked.metadata.sensor_family==SensorFamily.ASTER else None)
        if family is None: raise ValueError('Composite currently targets Landsat 8/9, Sentinel-2 and historical ASTER')
        if family=='ASTER':
            raise ValueError('Composite exact ASTER bands/calibration require explicit calibrated multiband mapping; automatic reader is incomplete')
        level = checked.metadata.radiometric_unit or ('surface_reflectance' if checked.metadata.product_level in (ProductLevel.L2_SR,ProductLevel.L2A_BOA) else None)
        if level not in ('surface_reflectance','toa_reflectance'):
            raise ValueError('Composite source radiometric level/calibration is not established')
        data={scientific_id(a.band_name):asset(a.file_path,1,a.scale_factor,a.offset,a.calibration_provenance,
              valid_min=a.valid_min,valid_max=a.valid_max,unit=level,wavelength_nm=a.center_wavelength_nm)
              for a in checked.bands.values() if not a.is_thermal and a.unit=='reflectance'}
        legacy.append(dict(scene=checked,assets=data,family=family,level=level,qa=None,qa_schema=None,warnings=[]))
    if not legacy: raise ValueError('Composite no recognized scenes or explicit multiband mapping')
    if any(x['qa_schema']=='BQA_PRECOLLECTION' for x in legacy) and sensor not in ('AUTO',):
        raise ValueError('Composite pre-Collection Landsat L1T requires AUTO; do not label it C2 L2')
    return legacy


def preset_for(method,family,options):
    name = options.get('direct_preset' if method=='DIRECT_RGB' else 'ratio_preset') or 'AUTO'
    custom = options.get('direct_channels' if method=='DIRECT_RGB' else 'ratio_channels') or ''
    imported=options.get('preset_file')
    if imported:
        document=read_json(imported)
        if document.get('format')!='atiaf_composite_preset_v1': raise ValueError('Composite preset format is invalid')
        matches=[r for r in document.get('presets',[]) if r.get('method')==method]
        if len(matches)!=1 or matches[0].get('sensor')!=family:
            raise ValueError('Composite imported preset sensor/method mismatch')
        preset=deepcopy(matches[0])
        # Imported records cannot claim source_verified merely by declaring that status.
        known=next((p for p in PRESETS if p['id']==preset.get('id') and p==preset),None)
        if known is None: preset['status']='custom'
    elif custom.strip():
        preset=dict(id='CUSTOM',sensor=family,method=method,channels=[s.strip() for s in custom.split(';')],
                    en='Custom RGB',ar='تركيب RGB مخصص',status='custom',source=options.get('custom_source') or '',source_location='User-defined local preset')
        if not preset['source']: raise ValueError('Composite custom channels require source / local justification')
    else:
        name=DEFAULTS.get((family,method)) if name=='AUTO' else name
        preset=deepcopy(next((p for p in PRESETS if p['id']==name),None))
        if preset is None: raise ValueError('Composite no default preset for this sensor/method; define three custom channels')
    if preset.get('method')!=method or preset.get('sensor')!=family: raise ValueError('Composite preset sensor/method mismatch')
    if not isinstance(preset.get('id'),str) or not re.fullmatch(r'[A-Za-z][A-Za-z0-9_-]{0,60}',preset['id']):
        raise ValueError('Composite preset ID contains unsafe filename characters')
    for key in ('en','ar','source','status'):
        if not isinstance(preset.get(key),str) or not preset[key].strip() or len(preset[key])>4096:
            raise ValueError('Composite preset needs bounded names, source and status')
    if preset.get('status')=='experimental' and not options.get('allow_experimental'):
        raise ValueError('Composite experimental preset requires explicit experimental option')
    if not isinstance(preset.get('channels'),list) or len(preset['channels'])!=3:
        raise ValueError('Composite requires exactly three RGB channels')
    required=set()
    for expr in preset['channels']:
        _,bands=parse(expr); required|=bands
        if method=='DIRECT_RGB' and expr.strip() not in bands:
            raise ValueError('Composite Direct RGB requires band IDs, not arithmetic')
    return preset,required


def validate_request(input_folder,selected,sensor='AUTO',options=None,apply_qa=True,mosaic=False,output_crs=None,**unused):
    options=dict(options or {})
    from atiaf_core.composites.registry import PRESETS
    valid_keys = {p['id'] for p in PRESETS} | {'DIRECT_RGB', 'RATIO_RGB'}
    if not selected or any(x not in valid_keys for x in selected):
        raise ValueError('Composite select at least one composite preset or method; no preset is selected by default')
    config=render.settings(options)
    if options.get('preset_file') and options.get('restore_preset_display'):
        saved=read_json(options['preset_file']).get('display',{})
        settings_options=dict(display_mode='custom',display_gamma=saved.get('gamma'),
            display_clip=saved.get('clip_percent_each_tail'),display_saturation=saved.get('saturation'),
            stretch_method=saved.get('stretch_method','percentile'),display_stddev=saved.get('standard_deviations',2),
            display_limits=','.join(str(x) for pair in saved.get('channel_limits',[]) for x in pair))
        config=render.settings(settings_options)
        if not config.get('fixed_limits'): raise ValueError('Composite saved display settings are incomplete')
    epsilon=float(options.get('ratio_epsilon') or 1e-8)
    if not math.isfinite(epsilon) or not 0<epsilon<=.01: raise ValueError('Composite ratio epsilon must be finite and 0<epsilon<=.01')
    rows=sources(input_folder,sensor,options)
    plans=[]
    for data in rows:
        scene=data['scene']
        if not re.fullmatch(r'[A-Za-z0-9_.-]{1,160}',scene.metadata.scene_id) or '..' in scene.metadata.scene_id:
            raise ValueError('Composite unsafe scene ID')
        if data['level']=='toa_reflectance' and not options.get('allow_toa'):
            raise ValueError('Composite TOA input requires explicit TOA option; atmospheric correction is not applied')
        if apply_qa and not data['qa'] and not scene.quality_masks:
            raise ValueError('Composite requested quality mask is absent; explicitly disable QA or supply a complete product')
        for item in dict.fromkeys(selected):
            if item in ('DIRECT_RGB', 'RATIO_RGB'):
                method = item
                preset, required = preset_for(method, data['family'], options)
            else:
                matched = next((p for p in PRESETS if p['id'] == item), None)
                if not matched:
                    raise ValueError(f'Composite unknown preset: {item}')
                preset = deepcopy(matched)
                method = preset['method']
                required = set()
                for expr in preset['channels']:
                    _, bands = parse(expr)
                    required |= bands
            missing=required-data['assets'].keys()
            if missing: raise ValueError('Composite missing scientific bands: '+','.join(sorted(missing)))
            if data['family']=='ASTER' and any(b in required for b in ('B4','B5','B6','B7','B8','B9')):
                date=scene.metadata.acquisition_date
                if not date or date>=datetime(2008,4,1):
                    raise ValueError('Composite ASTER SWIR requires known acquisition before April 2008')
                if datetime(2007,5,1)<=date<datetime(2008,2,1):
                    data['warnings'].append('NASA advisory: potential ASTER SWIR saturation in 2007 to January 2008; additional pixel QA needed.')
            resolutions=[]
            crss=set()
            for band in sorted(required):
                a=data['assets'][band]
                if not np.all(np.isfinite([a['scale'],a['offset']])) or a['scale']<=0: raise ValueError('Composite invalid band calibration')
                with rasterio.open(a['path']) as ds:
                    if not 1<=a['index']<=ds.count or not ds.crs: raise ValueError('Composite unknown source CRS or invalid band position')
                    if not scene.expert_mapped and data['qa_schema']!='landsat8_precollection' and a['scale']!=1 and np.issubdtype(np.dtype(ds.dtypes[a['index']-1]),np.floating):
                        raise ValueError('Composite floating source with raw product scaling risks double calibration; supply explicit stack mapping')
                    crs=CRS.from_user_input(output_crs or ds.crs)
                    if not crs.is_projected or any(abs(v.unit_conversion_factor-1)>1e-9 for v in crs.axis_info[:2]):
                        raise ValueError('Decision D-007: Composite requires a projected metre CRS')
                    if output_crs and CRS(ds.crs)!=crs:
                        from pyproj.transformer import TransformerGroup
                        group=TransformerGroup(ds.crs,crs,always_xy=True,allow_ballpark=False)
                        if not group.transformers or not group.best_available: raise ValueError('Composite datum transformation/grid unavailable')
                    crss.add(ds.crs.to_string())
                    resolutions.append((max(abs(ds.res[0]),abs(ds.res[1])),band))
            # Coarsest requested source band is reference; never claim upsampling adds detail.
            reference=max(resolutions)[1]
            ordered={reference:data['assets'][reference],**{b:data['assets'][b] for b in sorted(required) if b!=reference}}
            plans.append(dict(data=data,method=method,preset=preset,assets=ordered,config=config,epsilon=epsilon,apply_qa=apply_qa))
    if mosaic and len(rows)>1:
        keys={(r['family'],r['level'],r['scene'].metadata.product_generation,r['scene'].metadata.acquisition_date.date() if r['scene'].metadata.acquisition_date else None) for r in rows}
        if len(keys)!=1 or next(iter(keys))[3] is None: raise ValueError('Mosaic requires matching sensor, product generation/level and acquisition day')
        if not output_crs:
            source_crss=set()
            for plan in plans:
                with rasterio.open(next(iter(plan['assets'].values()))['path']) as ds: source_crss.add(ds.crs.to_wkt())
            if len(source_crss)>1: raise ValueError('Composite mosaic requires selecting a common output CRS')
    return plans


def clip_rgb(path,output,geometry,geometry_crs):
    """Bounded true polygon clip with preserved analytical tags/channel order."""
    from rasterio.features import geometry_mask
    from rasterio.windows import Window, from_bounds
    from shapely.geometry import mapping
    from atiaf_core.raster.clip import PolygonClipEngine
    from atiaf_core.raster.safe_io import atomic_raster
    with rasterio.open(path) as ds:
        geometry=PolygonClipEngine.reproject_geometry(geometry,geometry_crs,ds.crs)
        bounds=from_bounds(*geometry.bounds,transform=ds.transform)
        left,top=math.floor(bounds.col_off),math.floor(bounds.row_off)
        right,bottom=math.ceil(bounds.col_off+bounds.width),math.ceil(bounds.row_off+bounds.height)
        region=Window(left,top,right-left,bottom-top).intersection(Window(0,0,ds.width,ds.height))
        profile=dict(ds.profile,width=int(region.width),height=int(region.height),transform=ds.window_transform(region))
        with atomic_raster(output,**profile) as out:
            for _,win in out.block_windows(1):
                if RUN_OPTIONS.get().get('canceled',lambda:False)(): raise InterruptedError('Composite clip canceled')
                src_win=Window(win.col_off+region.col_off,win.row_off+region.row_off,win.width,win.height)
                values=ds.read(window=src_win)
                inside=geometry_mask([mapping(geometry)],out_shape=(int(win.height),int(win.width)),
                    transform=out.window_transform(win),invert=True)
                values[:,~inside]=ds.nodata
                out.write(values,window=win)
            out.colorinterp=ds.colorinterp
            out.update_tags(**ds.tags())
            for i,name in enumerate(ds.descriptions,1):
                if name: out.set_band_description(i,name)


def _compute(plan,blocks):
    bands={}
    for name,a in plan['assets'].items():
        raw=blocks[name]
        valid=np.isfinite(raw)
        if a.get('valid_min') is not None: valid&=raw>=a['valid_min']
        if a.get('valid_max') is not None: valid&=raw<=a['valid_max']
        val = raw.astype('float32')*a['scale']+a['offset']
        val = np.where(np.isfinite(val) & (val < 0.0001), 0.0001, val)
        bands[name]=np.where(valid,val,np.nan)
    result=np.stack([calculate(e,bands,plan['epsilon']) for e in plan['preset']['channels']])
    if '__LEGACY_BQA' in blocks:
        q=blocks['__LEGACY_BQA'].astype('uint16')
        from atiaf_core.execution_context import RUN_OPTIONS
        opts = RUN_OPTIONS.get() or {}
        user_opts = opts.get('user_options') or {}
        mode = opts.get('qa_mask_mode') or user_opts.get('qa_mask_mode') or 'Cloud_Only_Arid'
        clear=((q&7)==0)
        if mode not in ('Cloud_Only_Arid', 'arid', 'cloud_only'):
            for shift in (10,12,14): clear&=((q>>shift)&3)<2
        result[:,~clear]=np.nan
    return result


def _paths(plan):
    paths={k:a['path'] for k,a in plan['assets'].items()}
    if plan['apply_qa'] and plan['data']['qa'] is not None: paths['__LEGACY_BQA']=plan['data']['qa']
    return paths


def _sample(plan,output_crs=None,aoi_geometry=None,aoi_crs=None):
    # A genuinely bounded pre-write preview: no full-size analytical raster is created.
    with ExitStack() as stack:
        ref=stack.enter_context(rasterio.open(next(iter(plan['assets'].values()))['path']))
        target_crs=output_crs or ref.crs
        transform,width,height=ref.transform,ref.width,ref.height
        if output_crs and ref.crs!=rasterio.crs.CRS.from_user_input(output_crs):
            from rasterio.warp import calculate_default_transform
            transform,width,height=calculate_default_transform(ref.crs,output_crs,width,height,*ref.bounds)
        factor=min(1.,512/max(width,height))
        small_width,small_height=max(1,round(width*factor)),max(1,round(height*factor))
        transform=transform*transform.scale(width/small_width,height/small_height)
        width,height=small_width,small_height
        blocks={}
        mask=np.zeros((height,width),bool)
        for key,path in _paths(plan).items():
            ds=stack.enter_context(rasterio.open(path))
            vrt=stack.enter_context(WarpedVRT(ds,crs=target_crs,transform=transform,width=width,height=height,resampling=Resampling.nearest))
            index=plan['assets'].get(key,{}).get('index',1)
            blocks[key]=vrt.read(index)
            if not key.startswith('__'): mask|=vrt.read_masks(index)==0
        from atiaf_core.raster.masks import QualityMaskEngine
        for key,a in RUN_OPTIONS.get().get('quality_masks',{}).items():
            if key not in ('QA_PIXEL','SCL','QA_RADSAT')+QualityMaskEngine.LEGACY_SCHEMAS: continue
            ds=stack.enter_context(rasterio.open(a.file_path))
            vrt=stack.enter_context(WarpedVRT(ds,crs=target_crs,transform=transform,width=width,height=height,resampling=Resampling.nearest))
            q=vrt.read(1)
            mask|=~QualityMaskEngine.clear_for_schema(q,key)
        if aoi_geometry is not None:
            from atiaf_core.raster.clip import PolygonClipEngine
            from rasterio.features import geometry_mask
            from shapely.geometry import mapping
            geometry=PolygonClipEngine.reproject_geometry(aoi_geometry,aoi_crs,target_crs)
            mask|=~geometry_mask([mapping(geometry)],out_shape=(height,width),transform=transform,invert=True)
        sample=_compute(plan,blocks); sample[:,mask]=np.nan
        plan['_preview_grid']=dict(crs=str(target_crs),width=width,height=height,transform=list(transform),
                                   pixel_size=[abs(transform.a),abs(transform.e)])
        return sample


def _write(plan,path):
    result=WindowedRasterEngine.process_bands(_paths(plan),path,lambda b:_compute(plan,b),output_count=3,
        band_indexes={k:a['index'] for k,a in plan['assets'].items()},output_nodata=np.nan)
    with rasterio.open(path,'r+') as ds:
        ds.colorinterp=(ColorInterp.red,ColorInterp.green,ColorInterp.blue)
        for i,expression in enumerate(plan['preset']['channels'],1): ds.set_band_description(i,expression)
        ds.update_tags(ATIAF_PRODUCT='analytical_continuous_RGB',RGB_FORMULAS=json.dumps(plan['preset']['channels']),
                       PRESET=json.dumps(plan['preset']),CLASSIFICATION='false',INPUT_LEVEL=plan['data']['level'])
    result['valid_pixels']//=3; result['nodata_pixels']//=3
    result['nodata']='NaN'
    return result


def _display(path,output,config):
    def compute(blocks):
        values=np.stack([blocks[k] for k in ('R','G','B')])
        return render.colorize(values,config)
    WindowedRasterEngine.process_bands(dict(R=path,G=path,B=path),output,compute,output_count=3,
        band_indexes=dict(R=1,G=2,B=3),output_nodata=0,output_dtype='uint8')
    with rasterio.open(output,'r+') as ds:
        ds.colorinterp=(ColorInterp.red,ColorInterp.green,ColorInterp.blue)
        ds.update_tags(ATIAF_PRODUCT='display_RGB_not_analytical_reflectance',DISPLAY_SETTINGS=json.dumps(config))


def channel_statistics(path):
    """Full-resolution finite/masked moments, distinct from sampled stretch bounds."""
    counts=np.zeros(3,dtype='int64'); sums=np.zeros(3); squares=np.zeros(3)
    lows=np.full(3,np.inf); highs=np.full(3,-np.inf)
    with rasterio.open(path) as ds:
        total=ds.width*ds.height
        for _,window in ds.block_windows(1):
            values=ds.read(window=window,masked=True)
            for i in range(3):
                v=values[i].compressed().astype('float64');v=v[np.isfinite(v)]
                if not v.size: continue
                counts[i]+=len(v);sums[i]+=v.sum();squares[i]+=(v*v).sum()
                lows[i]=min(lows[i],v.min());highs[i]=max(highs[i],v.max())
    result=[]
    for i,label in enumerate(('R','G','B')):
        n=int(counts[i]);mean=sums[i]/n if n else None
        result.append(dict(channel=label,valid_pixels=n,nodata_pixels=total-n,min=float(lows[i]) if n else None,
            max=float(highs[i]) if n else None,mean=float(mean) if n else None,
            std_population=float(np.sqrt(max(0,squares[i]/n-mean*mean))) if n else None))
    return result


def run(input_folder,selected,sensor='AUTO',options=None,apply_qa=True,mosaic=False,output_crs=None,
        output_folder=None,aoi_geometry=None,aoi_crs=None,language='en',canceled=lambda:False,progress=lambda m:None,**unused):
    options=dict(options or {})
    plans=validate_request(input_folder,selected,sensor,options,apply_qa,mosaic,output_crs)
    if aoi_geometry is not None and (not aoi_crs or aoi_geometry.is_empty or not aoi_geometry.is_valid or aoi_geometry.geom_type not in ('Polygon','MultiPolygon')):
        raise ValueError('AOI requires a valid nonempty polygon and source CRS')
    preview=bool(options.get('preview_only'))
    if preview and mosaic: raise ValueError('Composite preview is per scene; disable mosaic for temporary previews')
    if not preview:
        target=Path(output_folder or input_folder).resolve()
        while not target.exists(): target=target.parent
        estimate=0
        for plan in plans:
            with rasterio.open(next(iter(plan['assets'].values()))['path']) as ds:
                estimate+=ds.width*ds.height*3*(4+(1 if options.get('save_display',True) else 0))
        # Conservative uncompressed allowance for staging, clips and complete RGB mosaics.
        if shutil.disk_usage(target).free < estimate*3+64*1024*1024:
            raise ValueError('Composite insufficient free disk space for protected analytical/display outputs and staging')
    outputs,manifests,previews,display_outputs=[],[],[],[]
    grouped={}
    for plan in plans:
        scene=plan['data']['scene']
        if canceled(): raise InterruptedError('Composite canceled; saved outputs preserved')
        progress(scene.metadata.scene_id)
        context=dict(output_crs=output_crs,source_scene=scene.to_dict(),sensor_family=scene.metadata.sensor_family.value,
                     quality_masks=scene.quality_masks if apply_qa else {},language=language,user_options=options,canceled=canceled,
                     selected=selected,scientific_definitions=[plan['preset']])
        token=RUN_OPTIONS.set(context)
        try:
            preset=plan['preset']; method=plan['method']
            if preview:
                directory=Path(tempfile.mkdtemp(prefix='atiaf_rgb_preview_'))
                sample=_sample(plan,output_crs,aoi_geometry,aoi_crs)
                config=dict(plan['config'],channel_limits=render.limits(sample,plan['config']),
                            method=method,channels=preset['channels'],preset_id=preset['id'],scientific_source=preset['source'],
                            sample_grid=plan['_preview_grid'])
                p=directory/'Preview.html'; p.write_text(render.preview_html(sample,config,preset[language],language),'utf-8')
                png=directory/'Preview.png'; png.write_bytes(render.png_bytes(sample,config))
                baseline=render.settings(dict(display_mode='quiet'))
                baseline['channel_limits']=render.limits(sample,baseline)
                (directory/'Before.png').write_bytes(render.png_bytes(sample,baseline))
                (directory/'Preview.json').write_text(json.dumps(config,ensure_ascii=False,indent=2),'utf-8')
                previews.append(str(p)); continue
            dest=Path(output_folder).resolve() if output_folder and Path(output_folder).resolve()!=Path(input_folder).resolve() else None
            _,work,_,results,reports=WorkspaceManager.resolve_workspace_roots(scene.scene_path,dest)
            category='Direct_RGB' if method=='DIRECT_RGB' else 'Band_Ratio_RGB'
            run_id=uuid.uuid4().hex[:12]
            directory=results/'Geological_Color_Composites'/category/preset['id']
            for folder in ('Analytical','Display','Metadata','QA_Reports'): (directory/folder).mkdir(parents=True,exist_ok=True)
            
            # Clean short filename: [<study_area>_]<preset_slug>_<date>
            study_name = options.get('study_area_name') or ''
            study_clean = re.sub(r'[^\w-]', '_', str(study_name).strip()) if study_name else ''
            date_str = ''
            if scene.metadata.acquisition_date:
                try:
                    date_str = scene.metadata.acquisition_date.strftime('%Y%m%d')
                except Exception:
                    pass
            if not date_str:
                m_date = re.search(r'_(20\d{6})_', scene.metadata.scene_id)
                if m_date:
                    date_str = m_date.group(1)
                else:
                    m_julian = re.search(r'L[CTEOM]\d{2}\d{4}(20\d{2})(\d{3})', scene.metadata.scene_id)
                    if m_julian:
                        try:
                            year, jday = int(m_julian.group(1)), int(m_julian.group(2))
                            dt = datetime(year, 1, 1) + timedelta(days=jday - 1)
                            date_str = dt.strftime('%Y%m%d')
                        except Exception:
                            pass
            if not date_str:
                date_str = scene.metadata.scene_id[:12]

            actual_satellite=re.sub(r'[^A-Za-z0-9]+','',scene.metadata.platform) or 'ExpertSensor'
            preset_slug = preset['id'].replace('L89_', '').replace('S2_', '')
            parts = []
            if study_clean:
                parts.append(study_clean)
            parts.append(actual_satellite)
            parts.append(preset_slug)
            parts.append(date_str)
            base = '_'.join(parts)

            path=WorkspaceManager.unique_path(directory/'Analytical'/(base+'.tif'))
            quality=_write(plan,path)
            saved=path
            if aoi_geometry is not None:
                saved=WorkspaceManager.unique_path(path.with_name(path.stem+'_CLIP.tif'))
                clip_rgb(path,saved,aoi_geometry,aoi_crs)
            sample=render.raster_sample(saved)
            config=dict(plan['config'],channel_limits=render.limits(sample,plan['config']),
                        method=method,channels=preset['channels'],preset_id=preset['id'],scientific_source=preset['source'])
            with rasterio.open(saved) as saved_ds:
                config['output_grid']=dict(crs=saved_ds.crs.to_string(),width=saved_ds.width,height=saved_ds.height,
                    transform=list(saved_ds.transform),pixel_size=list(map(abs,saved_ds.res)))
            preview_path=directory/'Display'/(base+'.preview.html'); preview_path.write_text(render.preview_html(sample,config,preset[language],language),'utf-8')
            preview_path.with_suffix('.png').write_bytes(render.png_bytes(sample,config))
            previews.append(str(preview_path))
            display_path=None
            if options.get('save_display',True):
                disp_target=directory/'Display'/(base+('_CLIP' if saved!=path else '')+'_DISPLAY.tif')
                display_path=WorkspaceManager.unique_path(disp_target)
                _display(saved,display_path,config)
                display_outputs.append(str(display_path))
            intermediates=[]
            if options.get('save_intermediates'):
                channel_dir=work/('Geology_'+preset['id'])/run_id/'Intermediate_Rasters'
                for index,label in enumerate(('R','G','B'),1):
                    channel=channel_dir/(base+'_'+label+'_Analytical.tif')
                    WindowedRasterEngine.process_bands({'channel':saved},channel,lambda b:b['channel'],
                        band_indexes={'channel':index},output_nodata=np.nan)
                    intermediates.append(str(channel))
            meta=dict(preset=preset,display=config,analytical_unit=plan['data']['level'] if method=='DIRECT_RGB' else 'dimensionless ratio',
                      channel_statistics=channel_statistics(saved),statistics_policy='Full resolution, finite valid analytical values; stretch bounds are sampled separately',
                      actual_satellite=scene.metadata.platform,compatibility_family=plan['data']['family'],
                      source_scene=scene.metadata.to_dict(),analytical_path=str(saved),intermediate_channels=intermediates,
                      sources={k:{**a,'path':str(a['path'])} for k,a in plan['assets'].items()},
                      reference_band=next(iter(plan['assets'])),resampling='nearest',epsilon=plan['epsilon'],
                      qa_applied=apply_qa,qa_schema=plan['data']['qa_schema'] or list(scene.quality_masks),
                      warnings=plan['data']['warnings'],disclaimer=DISCLAIMER[language],classification=False,
                      preview=str(preview_path),display_path=str(display_path) if display_path else None,
                      acquisition_date=scene.metadata.acquisition_date.isoformat() if scene.metadata.acquisition_date else None)
            for key,source in meta['sources'].items():
                source.update(scientific_band_id=key,nominal_center_wavelength_nm=CENTERS_NM[plan['data']['family']].get(key),
                    physical_role=next((a.role.value for a in scene.bands.values() if a.band_name==key),'explicit expert mapping'),
                    wavelength_source=SPECTRAL_SOURCES[plan['data']['family']],
                    wavelength_note='Nominal reference value, not extracted metadata or a measured spectral response')
            from atiaf_core import __version__
            from datetime import timezone
            fingerprint_sources=set(_paths(plan).values())
            if apply_qa: fingerprint_sources.update(a.file_path for a in scene.quality_masks.values())
            if scene.metadata.metadata_file: fingerprint_sources.add(scene.metadata.metadata_file)
            meta.update(engine_version=__version__,run_time_utc=datetime.now(timezone.utc).isoformat(),
                fingerprint=WorkspaceManager.compute_cache_fingerprint(
                    list(fingerprint_sources),method,
                    dict(preset=preset,epsilon=plan['epsilon'],qa=apply_qa,engine=__version__,
                         calibration={k:{key:a.get(key) for key in ('index','scale','offset','unit')} for k,a in plan['assets'].items()},
                         aoi=aoi_geometry.wkt if aoi_geometry is not None else None,aoi_crs=str(aoi_crs),
                         reference_band=next(iter(plan['assets'])),resampling='nearest'),output_crs),
                fingerprint_policy='Source filename, size, modification time and canonical analytical parameters; not full-content hashing',
                cache_policy='Recompute with unique filenames; no cache hit is claimed')
            with rasterio.open(saved) as ds:
                meta['output_grid']=dict(crs=ds.crs.to_string(),transform=list(ds.transform),width=ds.width,height=ds.height,nodata='NaN')
            metadata_path=directory/'Metadata'/(base+'.json')
            metadata_path.write_text(json.dumps(meta,ensure_ascii=False,indent=2,allow_nan=False),'utf-8')
            record=dict(product_name=preset['id']+'_'+method,full_path=str(path),clipped_path=str(saved) if saved!=path else None,
                        unit=meta['analytical_unit'],valid_pixels=quality['valid_pixels'],metadata_path=str(metadata_path),composite=meta)
            run_dir=WorkspaceManager.create_run_manifest(reports,scene.metadata.scene_id,'07_Geological_Color_Composites',
                dict(method=method,preset=preset,display=config,output_crs=output_crs,aoi=aoi_geometry is not None),
                [record],quality,[DISCLAIMER[language]]+plan['data']['warnings'],extra_metadata=meta)
            (Path(run_dir)/'Composite_Preset.json').write_text(json.dumps(dict(format='atiaf_composite_preset_v1',
                presets=[p['preset'] for p in plans if p['data']['scene'].scene_path==scene.scene_path],display=config),ensure_ascii=False,indent=2),'utf-8')
            (directory/'QA_Reports'/'Report_Location.json').write_text(json.dumps(dict(report_folder=str(run_dir),
                metadata=str(metadata_path),classification=False),indent=2),'utf-8')
            outputs.append(str(saved)); manifests.append(str(run_dir))
            grouped.setdefault(method,[]).append((scene,path))
        finally:
            RUN_OPTIONS.reset(token)
    if mosaic and len({p['data']['scene'].scene_path for p in plans})>1:
        from atiaf_core.composites.mosaic import merge_rgb
        for method,pairs in grouped.items():
            merged=merge_rgb(pairs,Path(output_folder or input_folder),method,canceled)
            saved=merged
            if aoi_geometry is not None:
                saved=merged.with_name(merged.stem+'_CLIP.tif'); clip_rgb(merged,saved,aoi_geometry,aoi_crs)
            outputs.append(str(saved))
            sample=render.raster_sample(saved)
            config=dict(plans[0]['config'],channel_limits=render.limits(sample,plans[0]['config']))
            if options.get('save_display',True):
                display=saved.with_name(saved.stem+'_DISPLAY.tif'); _display(saved,display,config)
                display_outputs.append(str(display))
            preview_path=merged.with_suffix('.preview.html')
            preview_path.write_text(render.preview_html(sample,config,method,language),'utf-8'); previews.append(str(preview_path))
            reports=Path(output_folder or input_folder)/'Results'/'Reports'
            reports.mkdir(parents=True,exist_ok=True)
            manifests.append(str(WorkspaceManager.create_run_manifest(reports,'Mosaic','07_Geological_Color_Composites',
                dict(method=method,display=config,policy='Same sensor/level/day; first valid triplet from QA-masked scenes'),
                [dict(product_name=method,full_path=str(merged),clipped_path=str(saved) if saved!=merged else None,
                      source_table=str(merged.with_suffix('.json')))],{},[DISCLAIMER[language]])))
    return dict(OUTPUT_FOLDER=str(output_folder or input_folder),OUTPUT_RASTERS=outputs,RUN_MANIFESTS=manifests,
                PREVIEWS=previews,DISPLAY_RASTERS=display_outputs,PREVIEW_ONLY=preview)

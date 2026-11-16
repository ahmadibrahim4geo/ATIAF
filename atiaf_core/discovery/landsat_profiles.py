"""Bounded metadata-first Landsat generations. No filename-only calibration.

Original implementation from documented USGS profiles; no external code vendored.
"""
from datetime import datetime
import json
import math
from pathlib import Path
import re
import xml.etree.ElementTree as ET
from .models import BandAsset,BandRole,ProductLevel,QualityAsset,SceneInfo,SceneMetadata,SensorFamily

SCALE_SOURCE='https://www.usgs.gov/faqs/how-do-i-use-a-scale-factor-landsat-level-2-science-products'


def _bounded(path):
    if path.stat().st_size>4*1024*1024: raise ValueError('Landsat metadata exceeds 4 MiB')
    return path.read_text('utf-8-sig')


def read_metadata(folder):
    files=list(folder.glob('*_MTL.json'))+list(folder.glob('*_MTL.xml'))+list(folder.glob('*_MTL.txt'))
    companions=[p for p in folder.glob('*.xml') if p not in files and 'espa_metadata' in _bounded(p)[:4096]]
    if len(companions)>1: raise ValueError('Landsat ambiguous ESPA metadata products in scene folder')
    if not files: return _read_file(companions[0]) if companions else (None,None)
    if len([p for p in files if p.suffix==files[0].suffix])>1:
        raise ValueError('Landsat ambiguous MTL products in scene folder')
    data,path=_read_file(files[0])
    if companions:
        sr,sr_path=_read_file(companions[0])
        if sr.get('_ESPA_SR_BANDS'):
            ids=lambda row:{row[k] for k in ('LANDSAT_SCENE_ID','SCENE_ID','LANDSAT_PRODUCT_ID','PRODUCT_ID') if row.get(k)}
            if not ids(data)&ids(sr): raise ValueError('Landsat companion ESPA requires a matching scene/product identifier')
            data.update(sr);data['_SOURCE_METADATA_FILES']=[str(path),str(sr_path)]
            path=sr_path
    return data,path


def _read_file(path):
    text=_bounded(path); data={}
    if path.suffix.lower()=='.json':
        def flatten(value):
            if not isinstance(value,dict): raise ValueError('Landsat MTL JSON must contain objects')
            for key,item in value.items():
                if isinstance(item,dict): flatten(item)
                elif isinstance(item,(str,int,float)) and key not in ('GROUP','END_GROUP'): data[key.upper()]=str(item)
        flatten(json.loads(text))
    elif path.suffix.lower()=='.xml':
        if '<!DOCTYPE' in text.upper() or '<!ENTITY' in text.upper(): raise ValueError('Landsat metadata XML declarations are not permitted')
        root=ET.fromstring(text)
        def _parse_xml(node, in_l1=False):
            tag=node.tag.split('}')[-1].upper()
            is_l1=in_l1 or ('LEVEL1' in tag)
            if node.text and node.text.strip() and not list(node):
                val=node.text.strip()
                if is_l1:
                    data.setdefault('L1_'+tag, val)
                    data.setdefault(tag, val)
                else:
                    data[tag]=val
            for child in node:
                _parse_xml(child, is_l1)
        _parse_xml(root)
        if root.tag.lower()=='espa_metadata':
            data['SPACECRAFT_ID']=data.get('SATELLITE','')
            data['SENSOR_ID']=data.get('INSTRUMENT','')
            data['DATE_ACQUIRED']=data.get('ACQUISITION_DATE','')
            data['FILE_DATE']=data.get('PRODUCTION_DATE','')
            entries=[]
            for band in root.findall('.//band'):
                if band.attrib.get('product')=='sr_refl':
                    entries.append(dict(band.attrib,**{c.tag:c.text.strip() for c in band if c.text and c.text.strip()}))
            if entries:
                data['_ESPA_SR_BANDS']=entries; data['PROCESSING_LEVEL']='L2SR'
    else:
        stack=[]
        for line in text.splitlines():
            line=line.strip()
            if line.startswith('GROUP =') or line.startswith('GROUP='):
                stack.append(line.split('=',1)[1].strip())
            elif line.startswith('END_GROUP =') or line.startswith('END_GROUP='):
                if stack: stack.pop()
            elif '=' in line:
                key,value=line.split('=',1)
                k=key.strip().upper()
                v=value.strip().strip('"')
                if k not in ('GROUP','END_GROUP'):
                    if any('LEVEL1' in g.upper() for g in stack):
                        data.setdefault('L1_'+k, v)
                        data.setdefault(k, v)
                    else:
                        data[k]=v
    if not data: raise ValueError('Landsat metadata has no usable fields')
    return data,path


def _path(folder,name):
    if not name: return None
    path=(folder/str(name)).resolve()
    if path.parent!=folder.resolve(): raise ValueError('Landsat metadata asset path escapes scene folder')
    return path if path.is_file() else None


def _find(folder,*suffixes):
    matches=[p for p in folder.iterdir() if p.is_file() and any(p.name.upper().endswith(x.upper()) for x in suffixes)]
    if len(matches)>1: raise ValueError('Landsat ambiguous band assets: '+', '.join(p.name for p in matches))
    return matches[0] if matches else None


def parse_profile(folder):
    m,path=read_metadata(folder)
    if m is None: return None
    product=m.get('LANDSAT_PRODUCT_ID') or m.get('PRODUCT_ID')
    old=m.get('LANDSAT_SCENE_ID') or m.get('SCENE_ID')
    identity=product or old or folder.name
    if not re.fullmatch(r'[A-Za-z0-9_.-]{1,160}',identity) or '..' in identity:
        raise ValueError('Landsat scene ID contains unsafe filename characters')
    satellite=m.get('SPACECRAFT_ID','').upper().replace(' ','_')
    sensor=m.get('SENSOR_ID','').upper().replace('+','')
    coded=product or old or ''
    if not satellite:
        match=re.match(r'L[COETM]0?([1-9])',coded)
        if match: satellite='LANDSAT_'+match[1]
    if not sensor:
        sensor=('MSS' if coded.startswith('LM') else 'TM' if coded.startswith('LT') else 'ETM' if coded.startswith('LE') else 'OLI_TIRS' if coded.startswith('LC') else '')
    if satellite not in {'LANDSAT_'+str(i) for i in range(1,10)} or not sensor:
        raise ValueError('Landsat metadata cannot establish satellite/instrument identity')
    number=int(satellite.rsplit('_',1)[-1]); is_mss='MSS' in sensor
    raw_level=m.get('PROCESSING_LEVEL') or m.get('DATA_TYPE') or ''
    if raw_level.startswith('L2'): level=ProductLevel.L2_SR
    elif raw_level.startswith('L1'): level=ProductLevel.L1_MSS if is_mss else ProductLevel.L1T
    else: level=ProductLevel.UNKNOWN
    collection=m.get('COLLECTION_NUMBER')
    encoded=re.fullmatch(r'L[COETM]\d\d_[A-Z0-9]{4}_\d{6}_\d{8}_\d{8}_(\d{2})_[A-Z0-9]{2}',product or '')
    if collection is not None:
        if str(collection).strip() not in ('1','01','2','02'): raise ValueError('Landsat unsupported collection number')
        collection=str(collection).strip().zfill(2)
        if encoded and collection!=encoded[1]: raise ValueError('Landsat collection metadata conflicts with product identifier')
    elif encoded: collection=encoded[1]
    old_id=re.fullmatch(r'L[COETM]([1-9])(\d{3})(\d{3})(\d{4})(\d{3})([A-Z0-9]{3})(\d{2})',old or '')
    generation='COLLECTION_'+str(int(collection)) if collection else 'PRE_COLLECTION' if old_id and not product else 'UNSPECIFIED'
    try:
        date=datetime.fromisoformat(m['DATE_ACQUIRED'].split('T')[0]) if m.get('DATE_ACQUIRED') else None
        if date and m.get('SCENE_CENTER_TIME'):
            date=datetime.fromisoformat(date.date().isoformat()+'T'+m['SCENE_CENTER_TIME'].rstrip('Z'))
            date=date.replace(microsecond=0)
    except ValueError as exc: raise ValueError('Landsat acquisition date/time is invalid') from exc
    def numeric(key):
        if key not in m: return None
        value=float(m[key])
        if not math.isfinite(value): raise ValueError('Landsat metadata coefficient is nonfinite: '+key)
        return value
    warnings=[]; restrictions=[]
    if is_mss: restrictions+=['NO_SWIR','NO_THERMAL']; warnings+=['MSS has no SWIR or thermal bands; no such result can be synthesized.']
    if number==7 and date and date>=datetime(2003,5,31):
        warnings+=['Landsat 7 SLC-off gaps retained as NoData; no silent gap filling.']; restrictions+=['SLC_OFF']
    if old_id and date:
        coded_date=datetime.strptime(old_id[4]+old_id[5],'%Y%j')
        if coded_date.date()!=date.date(): warnings+=['Historical scene identifier date disagrees with DATE_ACQUIRED; metadata date retained.']
    wrs_path=int(m['WRS_PATH']) if m.get('WRS_PATH') else int(old_id[2]) if old_id else None
    wrs_row=int(m['WRS_ROW']) if m.get('WRS_ROW') else int(old_id[3]) if old_id else None
    if level==ProductLevel.L2_SR and collection is None and not m.get('_ESPA_SR_BANDS'):
        raise ValueError('Landsat surface-reflectance scaling requires a proven collection or explicit ESPA band calibration')
    sun=numeric('SUN_ELEVATION')
    metadata=SceneMetadata(identity,SensorFamily.LANDSAT,
        {4:'LANDSAT_TM_4_5',5:'LANDSAT_TM_4_5',7:'LANDSAT_ETM_7',8:'LANDSAT_OLI_TIRS_8',9:'LANDSAT_OLI2_TIRS2_9'}.get(number,'LANDSAT_MSS'),
        satellite.replace('_',' ').title(),sensor,level,date,sun,numeric('SUN_AZIMUTH'),numeric('CLOUD_COVER'),path,warnings,restrictions,
        source_scene_id=old,product_id=product,collection=collection,processing_level=raw_level,
        processing_date=m.get('PROCESSING_DATE') or m.get('FILE_DATE'),product_generation=generation,
        wrs_path=wrs_path,wrs_row=wrs_row,ground_station=old_id[6] if old_id else None,archive_version=old_id[7] if old_id else None)
    if is_mss: metadata.sensor_id='LANDSAT_MSS_'+str(number)
    if m.get('_SOURCE_METADATA_FILES'): metadata.calibration_fields['source_metadata_files']=m['_SOURCE_METADATA_FILES']
    if is_mss:
        indices=[4,5,6,7] if number<=3 else [1,2,3,4]
        roles=[BandRole.GREEN,BandRole.RED,BandRole.NIR,BandRole.NARROW_NIR]; centers=[550,650,750,900]
    elif number>=8:
        indices=[1,2,3,4,5,6,7]; roles=[BandRole.COASTAL_AEROSOL,BandRole.BLUE,BandRole.GREEN,BandRole.RED,BandRole.NIR,BandRole.SWIR_1,BandRole.SWIR_2]
        centers=[443,482,561,655,865,1609,2201]
    else:
        indices=[1,2,3,4,5,7]; roles=[BandRole.BLUE,BandRole.GREEN,BandRole.RED,BandRole.NIR,BandRole.SWIR_1,BandRole.SWIR_2]
        centers=[485,560,660,830,1650,2215]
    bands={}; units=set(); espa={}
    for record in m.get('_ESPA_SR_BANDS',[]):
        match=re.fullmatch(r'sr_band(\d+)',record.get('name',''))
        if match: espa[int(match[1])]=record
    for n,role,wavelength in zip(indices,roles,centers):
        record=espa.get(n)
        if espa and record is None: continue  # Never apply SR scaling to companion L1 raw assets.
        filename=(record or {}).get('file_name') or m.get(f'FILE_NAME_BAND_{n}')
        if record:
            source=_path(folder,filename)
        elif level==ProductLevel.L2_SR:
            source=_path(folder,filename) if filename else (_find(folder,f'_SR_B{n}.TIF') if collection=='02' else _find(folder,f'_sr_band{n}.tif',f'_SR_B{n}.TIF'))
        else:
            source=_path(folder,filename) if filename else _find(folder,f'_B{n}.TIF',f'_B{n:02d}.TIF')
        if source is None: continue
        scale,offset,unit,low,high,nodata=1.,0.,'DN',1.,None,0.
        provenance='Raw DN; calibration is not established'
        if level==ProductLevel.L2_SR:
            if record:
                if record.get('data_units','').lower() not in ('reflectance','surface reflectance') or 'scale_factor' not in record:
                    raise ValueError('Landsat ESPA SR band lacks explicit reflectance calibration')
                scale=float(record['scale_factor']);offset=float(record.get('add_offset',0));nodata=float(record.get('fill_value',-9999))
                low,high=0.,10000.; provenance=f'{path.name}:band[{record["name"]}].scale_factor/add_offset/fill_value'
            elif collection=='02':
                scale,offset,low,high,nodata=.0000275,-.2,1.,65455.,0.
                provenance='USGS Collection2 L2 SR profile: DN*0.0000275-0.2; '+SCALE_SOURCE
            elif collection=='01':
                scale,offset,low,high,nodata=.0001,0.,0.,10000.,-9999.
                provenance='USGS Collection1 L2 SR profile: DN*0.0001; '+SCALE_SOURCE
            unit='reflectance'; units.add('surface_reflectance')
        elif not is_mss or all(f'REFLECTANCE_{k}_BAND_{n}' in m for k in ('MULT','ADD')):
            mult,add=f'REFLECTANCE_MULT_BAND_{n}',f'REFLECTANCE_ADD_BAND_{n}'
            if mult in m and add in m and sun is not None and 0<sun<=90:
                sine=math.sin(math.radians(sun));scale=numeric(mult)/sine;offset=numeric(add)/sine
                unit='reflectance'; high=65534.;units.add('toa_reflectance')
                provenance=f'{path.name}:{mult}, {add}, SUN_ELEVATION; (DN*MULT+ADD)/sin(sun elevation)'
                metadata.calibration_fields['B'+str(n)]={mult:m[mult],add:m[add],'SUN_ELEVATION':m['SUN_ELEVATION']}
            else:
                rm,ra=f'RADIANCE_MULT_BAND_{n}',f'RADIANCE_ADD_BAND_{n}'
                if rm in m and ra in m:
                    scale,offset,unit=numeric(rm),numeric(ra),'radiance';units.add('radiance')
                    provenance=f'{path.name}:{rm}, {ra}; no reflectance coefficients/valid sun elevation'
                else: units.add('DN')
        else: units.add('DN')
        if not all(math.isfinite(float(v)) for v in (scale,offset)) or scale<=0: raise ValueError('Landsat invalid calibration coefficients')
        bands[role]=BandAsset(role,source,'B'+str(n),wavelength,60. if is_mss else 30.,scale,offset,low,high,nodata,unit,False,provenance)
    if not is_mss:
        n=10 if number>=8 else 6
        if collection=='02' and level==ProductLevel.L2_SR:
            source=_find(folder,f'_ST_B{n}.TIF')
            if source:
                bands[BandRole.THERMAL_1]=BandAsset(BandRole.THERMAL_1,source,'B'+str(n),10895. if n==10 else 11450.,100. if n==10 else 60. if number==7 else 120.,
                    .00341802,149.,1.,65455.,0.,'Kelvin',True,'USGS C2 official L2 ST profile: DN*0.00341802+149; '+SCALE_SOURCE)
        else:
            filename=m.get(f'FILE_NAME_BAND_{n}')
            source=_path(folder,filename) if filename else _find(folder,f'_B{n}.TIF',f'_b{n}.tif')
            if source:
                rm,ra=f'RADIANCE_MULT_BAND_{n}',f'RADIANCE_ADD_BAND_{n}'
                if rm in m and ra in m:
                    scale,offset,unit=numeric(rm),numeric(ra),'radiance'
                    provenance=f'{path.name}:{rm}, {ra}; at-sensor radiance'
                else:
                    scale,offset,unit=1.,0.,'DN'
                    provenance='Raw DN; calibration is not established'
                bands[BandRole.THERMAL_1]=BandAsset(BandRole.THERMAL_1,source,'B'+str(n),10895. if n==10 else 11450.,100. if n==10 else 60. if number==7 else 120.,
                    scale,offset,1.,65455.,0.,unit,True,provenance)
                k1,k2=numeric(f'K1_CONSTANT_BAND_{n}'),numeric(f'K2_CONSTANT_BAND_{n}')
                if k1 and k2:
                    metadata.calibration_fields['THERMAL']={'K1':k1,'K2':k2}
    metadata.radiometric_unit=next(iter(units)) if len(units)==1 else 'mixed_or_unknown'
    if metadata.radiometric_unit=='toa_reflectance': warnings+=['TOA reflectance, not surface reflectance. No atmospheric correction performed.']
    masks={}
    def quality(key,source,description):
        if source: masks[key]=QualityAsset(key,source,description,dict(schema=key,source_metadata=path.name))
    if collection=='02':
        quality('QA_PIXEL',_find(folder,'_QA_PIXEL.TIF'),'USGS Collection2 QA_PIXEL')
        quality('QA_RADSAT',_find(folder,'_QA_RADSAT.TIF'),'USGS Collection2 saturation flags')
        if 'QA_PIXEL' in masks:
            masks['QA_PIXEL'].flags_info.update(fill_bit=0,dilated_cloud_bit=1,cirrus_bit=2,cloud_bit=3,
                cloud_shadow_bit=4,snow_bit=5,clear_bit=6,water_bit=7)
    elif generation=='PRE_COLLECTION' and number==8:
        qa=_path(folder,m.get('FILE_NAME_BAND_QUALITY')) or _find(folder,'_BQA.TIF')
        quality('BQA_PRECOLLECTION',qa,'Pre-Collection Landsat8 BQA; no shadow flag; confidence00 retained as unknown')
    elif collection=='01':
        if level==ProductLevel.L2_SR:
            quality('PIXEL_QA_C1_L8' if number>=8 else 'PIXEL_QA_C1_TM',_find(folder,'_pixel_qa.tif'),'Collection1 SR pixel_qa')
        else:
            quality('BQA_C1_L8' if number>=8 else 'BQA_C1_TM',_path(folder,m.get('FILE_NAME_BAND_QUALITY')) or _find(folder,'_BQA.TIF'),'Collection1 Level1 BQA')
    return SceneInfo(folder,metadata,bands,masks,False)

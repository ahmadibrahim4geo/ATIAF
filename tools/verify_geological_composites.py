"""Local real-product verification with independent sample arithmetic; no data download.

Use only on a positively identified pre-Collection Landsat 8 L1T bundle for this
reference calculation. This helper does not infer support for other product levels.
"""
import argparse
import faulthandler
from datetime import datetime as VerificationDateTime,timezone as VerificationTimezone
import hashlib
import json
import math
from pathlib import Path
import re
import sys
import time
import numpy as np
import rasterio

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))


def verify(scene,output,receipt,host='standalone',language='en',preview=False,existing=False):
    before={p.name:(p.stat().st_size,p.stat().st_mtime_ns) for p in scene.iterdir() if p.is_file()}
    metadata=next(scene.glob('*_MTL.txt'))
    text=metadata.read_text('utf-8')
    m=dict(re.findall(r'^\s*([A-Z0-9_]+)\s*=\s*"?([^"\r\n]+?)"?\s*$',text,re.M))
    if m.get('DATA_TYPE')!='L1T' or m.get('SPACECRAFT_ID')!='LANDSAT_8' or 'COLLECTION_NUMBER' in m:
        raise ValueError('Independent reference in this helper is restricted to pre-Collection Landsat 8 L1T')
    started=time.monotonic(); app=None
    if existing:
        result=dict(OUTPUT_RASTERS=[str(p) for p in sorted(output.rglob('*.tif')) if '_DISPLAY' not in p.stem and 'Source_Scene_ID' not in p.stem],
                    RUN_MANIFESTS=[str(p.parent) for p in output.rglob('Processing_Manifest.json')])
        if len(result['OUTPUT_RASTERS'])!=2: raise ValueError('Expected exactly two existing analytical products')
        version=sys.version
        host='artifact_readback_only'
    elif host=='qgis':
        sys.path.insert(0,str(ROOT/'QGIS Tools'))
        from qgis.core import QgsApplication,QgsProcessingContext,QgsProcessingFeedback
        app=QgsApplication([],False); app.initQgis()
        from atiaf.algorithms.geological_composites import GeologicalCompositesAlgorithm
        alg=GeologicalCompositesAlgorithm(); alg.language=language; alg.initAlgorithm()
        assert alg.parameterDefinitions()[0].name()=='SENSOR'
        assert alg.parameterDefinitions()[-1].name()=='OUTPUT_FOLDER'
        params=dict(INPUT_FOLDER=str(scene),OUTPUT_FOLDER=str(output),calc_DIRECT_RGB=True,calc_RATIO_RGB=True,
                    allow_toa=True,APPLY_QA=True,save_display=True,preview_only=preview)
        ok,message=alg.checkParameterValues(params,QgsProcessingContext())
        if not ok: raise ValueError(message)
        result=alg.processAlgorithm(params,QgsProcessingContext(),QgsProcessingFeedback())
        version=QgsApplication.qgisVersion() if hasattr(QgsApplication,'qgisVersion') else str(__import__('qgis.core',fromlist=['Qgis']).Qgis.QGIS_VERSION)
    elif host=='pro':
        faulthandler.enable()
        faulthandler.dump_traceback_later(90)
        output.mkdir(parents=True,exist_ok=True)
        print('Loading ArcGIS Pro runtime for local real-scene verification',flush=True)
        import arcpy
        print('ArcGIS runtime loaded',flush=True)
        arcpy.ImportToolbox(str(ROOT/'ArcGIS Pro Tools'/('ATIAF_AR.pyt' if language=='ar' else 'ATIAF.pyt')))
        alias='atiaf_ar' if language=='ar' else 'atiaf'
        params=arcpy.GetParameterInfo('GeologicalColorCompositesTool_'+alias)
        assert params[0].name=='sensor_product' and params[-1].name=='output_folder'
        getattr(arcpy,alias).GeologicalColorCompositesTool(input_folder=str(scene),output_folder=str(output),
            calc_DIRECT_RGB=True,calc_RATIO_RGB=True,allow_toa=True,apply_qa_mask=True,save_display=True,preview_only=preview)
        result=dict(OUTPUT_RASTERS=[str(p) for p in sorted(output.rglob('*.tif')) if '_DISPLAY' not in p.stem],
                    RUN_MANIFESTS=[str(p.parent) for p in output.rglob('Processing_Manifest.json')])
        version=arcpy.GetInstallInfo()
    else:
        from atiaf_core.workflow import run_tool
        result=run_tool('geological_composites',scene,['DIRECT_RGB','RATIO_RGB'],output_folder=output,
            options=dict(allow_toa=True,save_display=True,preview_only=preview),language=language,progress=lambda s:print(s,flush=True))
        version=sys.version
    observed=[]
    for path in result['OUTPUT_RASTERS']:
        path=Path(path)
        with rasterio.open(path) as ds:
            assert ds.count==3 and ds.crs and (ds.nodata==-9999 or np.isnan(ds.nodata))
            rng=np.random.default_rng(812345)
            # Find independent valid sample centers without reading a whole scene into memory.
            candidates=list(zip(rng.integers(0,ds.height,500),rng.integers(0,ds.width,500)))
            coords=[ds.xy(int(y),int(x)) for y,x in candidates]
            values=np.array(list(ds.sample(coords)))
            valid=np.all(values!=ds.nodata,axis=1)&np.all(np.isfinite(values),axis=1)
            coords=[c for c,v in zip(coords,valid) if v]; values=values[valid].astype('float64')
            assert len(coords)>50
            bands={}
            sine=math.sin(math.radians(float(m['SUN_ELEVATION'])))
            for n in (2,3,4,5,6,7):
                with rasterio.open(scene/m['FILE_NAME_BAND_'+str(n)]) as source:
                    raw=np.array(list(source.sample(coords)))[:,0].astype('float64')
                    bands[n]=(raw*float(m['REFLECTANCE_MULT_BAND_'+str(n)])+float(m['REFLECTANCE_ADD_BAND_'+str(n)]))/sine
            if 'DIRECT_RGB' in str(path.parent) or ds.descriptions==('B7','B5','B3'):
                expected=np.stack([bands[7],bands[5],bands[3]],axis=1)
            else:
                expected=np.stack([bands[6]/bands[7],bands[6]/bands[2],(bands[4]/bands[5])*(bands[6]/bands[5])],axis=1)
            np.testing.assert_allclose(values,expected,rtol=2e-5,atol=1e-5)
            observed.append(dict(path=str(path),width=ds.width,height=ds.height,crs=ds.crs.to_string(),cell_size=list(ds.res),
                dtype=ds.dtypes,channels=ds.descriptions,samples=len(coords),max_absolute_error=float(np.max(abs(values-expected))),
                grid=list(ds.transform),product=ds.tags().get('ATIAF_PRODUCT'),status='pass'))
    after={p.name:(p.stat().st_size,p.stat().st_mtime_ns) for p in scene.iterdir() if p.is_file()}
    assert before==after,'Source file size or modification time changed'
    payload=dict(date=VerificationDateTime.now(VerificationTimezone.utc).isoformat(),host=host,language=language,version=version,
        input_scene=scene.name,input_level='pre-Collection Landsat8 L1T; TOA reflectance; no atmospheric correction',
        source_metadata_sha256=hashlib.sha256(text.encode('utf-8')).hexdigest(),source_stat_unchanged=True,
        elapsed_seconds=time.monotonic()-started,outputs=observed,result=result,
        science='Independent sample arithmetic only; no field lithological classification or accuracy claim',status='pass')
    receipt.parent.mkdir(parents=True,exist_ok=True)
    with receipt.open('x',encoding='utf-8') as stream: json.dump(payload,stream,ensure_ascii=False,indent=2)
    print(json.dumps(dict(host=host,language=language,elapsed=payload['elapsed_seconds'],outputs=len(observed),receipt=str(receipt)),ensure_ascii=True),flush=True)
    if app: app.exitQgis()
    if host=='pro': faulthandler.cancel_dump_traceback_later()


if __name__=='__main__':
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--input',type=Path,required=True); ap.add_argument('--output',type=Path,required=True)
    ap.add_argument('--receipt',type=Path,required=True); ap.add_argument('--host',choices=['standalone','qgis','pro'],default='standalone')
    ap.add_argument('--language',choices=['en','ar'],default='en'); ap.add_argument('--preview',action='store_true')
    ap.add_argument('--verify-existing',action='store_true',help='Only independently read back exactly two existing products; does not prove host execution')
    args=ap.parse_args(); verify(args.input.resolve(),args.output.resolve(),args.receipt.resolve(),args.host,args.language,args.preview,args.verify_existing)

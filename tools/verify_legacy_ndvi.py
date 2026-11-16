"""Real legacy NDVI native operation plus independent full-resolution readback."""
import argparse,faulthandler,json,math,re,sys
from pathlib import Path
import numpy as np
import rasterio
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))


def verify(scene,output,receipt,host,language):
    before={p.name:(p.stat().st_size,p.stat().st_mtime_ns) for p in scene.iterdir() if p.is_file()}
    if host=='qgis':
        sys.path.insert(0,str(ROOT/'QGIS Tools'))
        from qgis.core import QgsApplication,QgsProcessingContext,QgsProcessingFeedback
        app=QgsApplication([],False);app.initQgis()
        from atiaf.algorithms.spectral_indices import SpectralIndicesAlgorithm
        alg=SpectralIndicesAlgorithm();alg.language=language;alg.initAlgorithm()
        result=alg.processAlgorithm(dict(INPUT_FOLDER=str(scene),OUTPUT_FOLDER=str(output),calc_NDVI=True,
            allow_toa=True,APPLY_QA=True),QgsProcessingContext(),QgsProcessingFeedback())
    elif host=='pro':
        faulthandler.enable();faulthandler.dump_traceback_later(90)
        print('Loading native ArcPy',flush=True)
        import arcpy
        arcpy.ImportToolbox(str(ROOT/'ArcGIS Pro Tools'/('ATIAF_AR.pyt' if language=='ar' else 'ATIAF.pyt')))
        output.mkdir(parents=True,exist_ok=False)
        alias='atiaf_ar' if language=='ar' else 'atiaf'
        getattr(arcpy,alias).SpectralIndicesTool(input_folder=str(scene),output_folder=str(output),calc_NDVI=True,
            allow_toa=True,apply_qa_mask=True)
        result=dict(OUTPUT_RASTERS=[str(p) for p in output.rglob('*.tif')])
    else:
        from atiaf_core.workflow import run_tool
        result=run_tool('spectral_indices',scene,['NDVI'],options={'allow_toa':True},output_folder=output,language=language)
    path=Path(result['OUTPUT_RASTERS'][0]);assert 'NDVI_TOA' in path.name
    m=dict(re.findall(r'^\s*([A-Z0-9_]+)\s*=\s*"?([^"\r\n]+?)"?\s*$',next(scene.glob('*_MTL.txt')).read_text('utf-8'),re.M))
    with rasterio.open(path) as ds:
        rng=np.random.default_rng(9814)
        coords=[ds.xy(int(y),int(x)) for y,x in zip(rng.integers(0,ds.height,400),rng.integers(0,ds.width,400))]
        values=np.array(list(ds.sample(coords,masked=True))).reshape(-1)
        valid=np.isfinite(values)&(values!=ds.nodata);coords=[c for c,v in zip(coords,valid) if v];values=values[valid]
        bands={}
        for n in (4,5):
            with rasterio.open(scene/m['FILE_NAME_BAND_'+str(n)]) as src:
                raw=np.array(list(src.sample(coords)))[:,0].astype('float64')
                bands[n]=(raw*float(m['REFLECTANCE_MULT_BAND_'+str(n)])+float(m['REFLECTANCE_ADD_BAND_'+str(n)]))/math.sin(math.radians(float(m['SUN_ELEVATION'])))
        expected=(bands[5]-bands[4])/(bands[5]+bands[4])
        assert len(expected)>50
        np.testing.assert_allclose(values,expected,atol=1e-6,rtol=2e-5)
        grid=dict(crs=ds.crs.to_string(),transform=list(ds.transform),width=ds.width,height=ds.height,nodata=ds.nodata)
    after={p.name:(p.stat().st_size,p.stat().st_mtime_ns) for p in scene.iterdir() if p.is_file()};assert before==after
    payload=dict(status='pass',host=host,language=language,path=str(path),grid=grid,samples=len(expected),
        max_absolute_error=float(np.max(abs(values-expected))),source_stat_unchanged=True,unit='diagnostic TOA NDVI; not SR NDVI',result=result)
    receipt.write_text(json.dumps(payload,indent=2),'utf-8')
    if host=='qgis':app.exitQgis()
    print(json.dumps(dict(status='pass',host=host,language=language,samples=len(expected))))


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--scene',type=Path,required=True);p.add_argument('--output',type=Path,required=True)
    p.add_argument('--receipt',type=Path,required=True);p.add_argument('--host',choices=['standalone','qgis','pro'],default='standalone')
    p.add_argument('--language',choices=['en','ar'],default='en');args=p.parse_args()
    verify(args.scene,args.output,args.receipt,args.host,args.language)

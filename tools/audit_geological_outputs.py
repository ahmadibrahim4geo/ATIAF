"""Read-only CRC1 audit, independent of ATIAF calculation/rendering functions.

Reference is deliberately limited to a metadata-confirmed pre-Collection L8 L1T.
Full raster moments/correlation and display masks; deterministic full-resolution
sample quantiles, histograms and independent arithmetic. No imagery downloads.
"""
import argparse
from contextlib import ExitStack
import csv
import hashlib
import json
import math
from pathlib import Path
import re
import time
import numpy as np
import rasterio


def digest(path):
    h=hashlib.sha256()
    with path.open('rb') as f:
        for block in iter(lambda:f.read(1024*1024),b''): h.update(block)
    return h.hexdigest()


def audit(scene, analytical, display, output):
    output.mkdir(parents=True,exist_ok=False)
    started=time.monotonic()
    metadata=next(scene.glob('*_MTL.txt'))
    text=metadata.read_text('utf-8')
    m=dict(re.findall(r'^\s*([A-Z0-9_]+)\s*=\s*"?([^"\r\n]+?)"?\s*$',text,re.M))
    if m.get('DATA_TYPE')!='L1T' or m.get('SPACECRAFT_ID')!='LANDSAT_8' or 'COLLECTION_NUMBER' in m:
        raise ValueError('Reference restricted to positively identified pre-Collection L8 L1T')
    before={str(p):(p.stat().st_size,p.stat().st_mtime_ns) for p in [*scene.iterdir(),analytical,display] if p.is_file()}
    hashes={str(p):digest(p) for p in (metadata,analytical,display)}
    count=0; nodata=0; nonfinite=0; mismatch=0
    sums=np.zeros(3); squares=np.zeros(3); cross=np.zeros((3,3))
    minima=np.full(3,np.inf); maxima=np.full(3,-np.inf)
    samples=[]; source_samples=[]; display_samples=[]; positions=[]
    with ExitStack() as stack:
        a=stack.enter_context(rasterio.open(analytical)); d=stack.enter_context(rasterio.open(display))
        sources={n:stack.enter_context(rasterio.open(scene/m['FILE_NAME_BAND_'+str(n)])) for n in (2,3,4,5,6,7)}
        qa=stack.enter_context(rasterio.open(next(scene.glob('*_BQA.TIF'))))
        for other in [d,*sources.values(),qa]:
            if (other.crs,other.transform,other.width,other.height)!=(a.crs,a.transform,a.width,a.height):
                raise ValueError('Audit requires exact common grids, no implicit reprojection')
        if a.count!=3 or a.descriptions!=('B6/B7','B6/B2','(B4/B5)*(B6/B5)') or d.dtypes!=('uint8',)*3:
            raise ValueError('Expected exact analytical CRC1 and separate UInt8 RGB display')
        for _,win in a.block_windows(1):
            values=a.read(window=win); mask=np.all(a.read_masks(window=win)>0,axis=0)
            finite=np.all(np.isfinite(values),axis=0)
            nonfinite+=int(np.count_nonzero(~finite & mask))
            valid=mask & finite; v=values[:,valid].astype('float64')
            count+=v.shape[1]; nodata+=int(valid.size-np.count_nonzero(valid))
            sums+=v.sum(axis=1); squares+=(v*v).sum(axis=1); cross+=v@v.T
            if v.size: minima=np.minimum(minima,v.min(axis=1)); maxima=np.maximum(maxima,v.max(axis=1))
            rgb=d.read(window=win)
            mismatch+=int(np.count_nonzero(np.all(rgb>0,axis=0)!=valid))
            # Every 32nd pixel in each tile, read at native resolution: no overviews.
            ys,xs=np.mgrid[0:int(win.height):32,0:int(win.width):32]
            good=valid[ys,xs]; ys=ys[good]; xs=xs[good]
            if not len(ys): continue
            raw=np.stack([ds.read(1,window=win)[ys,xs] for ds in sources.values()],axis=1)
            q=qa.read(1,window=win)[ys,xs]
            clear=(q&7)==0
            for shift in (10,12,14): clear &= ((q>>shift)&3)<2
            good=clear & np.all((raw>0)&(raw<65535),axis=1)
            ys=ys[good]; xs=xs[good]; raw=raw[good]
            if not len(raw): continue
            sine=math.sin(math.radians(float(m['SUN_ELEVATION'])))
            calibrated=np.stack([(raw[:,i].astype('float64')*float(m['REFLECTANCE_MULT_BAND_'+str(n)])+
                float(m['REFLECTANCE_ADD_BAND_'+str(n)]))/sine for i,n in enumerate(sources)],axis=1)
            samples.append(values[:,ys,xs].T); source_samples.append(calibrated)
            display_samples.append(rgb[:,ys,xs].T)
            positions.append(np.stack([ys+int(win.row_off),xs+int(win.col_off)],axis=1))
        grid=dict(crs=a.crs.to_string(),transform=list(a.transform),width=a.width,height=a.height,
                  resolution=list(a.res),nodata=a.nodata,descriptions=a.descriptions,dtype=a.dtypes)
    observed=np.concatenate(samples).astype('float64'); source=np.concatenate(source_samples)
    rgb=np.concatenate(display_samples); positions=np.concatenate(positions)
    b2,b3,b4,b5,b6,b7=source.T
    expected=np.stack([b6/b7,b6/b2,(b4/b5)*(b6/b5)],axis=1)
    errors=np.abs(observed-expected)
    stable=(np.minimum.reduce([np.abs(b7),np.abs(b2),np.abs(b5)])>.005)
    tolerance=1e-5+2e-5*np.abs(expected)
    passed=np.all(errors[stable]<=tolerance[stable])
    ndvi=(b5-b4)/(b5+b4); mndwi=(b3-b6)/(b3+b6)
    classes=np.full(len(source),'other',dtype='<U24')
    classes[ndvi>.3]='vegetation_proxy'
    classes[(mndwi>.2)&(ndvi<.1)]='water_proxy'
    classes[(ndvi>=0)&(ndvi<.2)&(mndwi<0)&(b6>.1)]='bare_candidate'
    groups={}
    for label in np.unique(classes):
        sel=classes==label; pixels=rgb[sel].astype(float)
        # Operational cyan criterion, not mineralogy/human color ground truth.
        cyan=(pixels[:,1]>pixels[:,0]+20)&(pixels[:,2]>pixels[:,0]+20)
        groups[label]=dict(sample_count=int(sel.sum()),median_toa_bands=np.median(source[sel],axis=0).tolist(),
            median_analytic=np.median(observed[sel],axis=0).tolist(),median_display_rgb=np.median(pixels,axis=0).tolist(),
            cyan_fraction=float(cyan.mean()))
    mean=sums/count; covariance=cross/count-np.outer(mean,mean)
    std=np.sqrt(np.maximum(0,squares/count-mean*mean))
    correlation=covariance/np.outer(std,std)
    quantiles=[0,1,2,5,25,50,75,95,98,99,100]
    config=json.loads(analytical.with_suffix('.json').read_text('utf-8'))['display']
    # Independently reproduce saved display on native-resolution sample points.
    normalized=np.stack([np.clip((observed[:,i]-lo)/(hi-lo),0,1) if hi>lo else np.full(len(observed),.5)
                         for i,(lo,hi) in enumerate(config['channel_limits'])],axis=1)
    normalized=normalized**(1/config['gamma'])
    luminance=normalized@np.array([.2126,.7152,.0722])
    reproduced=np.rint(np.clip(luminance[:,None]+config['saturation']*(normalized-luminance[:,None]),0,1)*254)+1
    display_error=np.max(np.abs(reproduced-rgb),axis=0)
    selected=[]
    for label in np.unique(classes):
        ids=np.flatnonzero(classes==label)
        selected.extend(ids[np.linspace(0,len(ids)-1,min(25,len(ids)),dtype=int)].tolist())
    with (output/'independent_pixels.csv').open('w',newline='',encoding='utf-8') as f:
        w=csv.writer(f); w.writerow(['row','column','proxy','B2_TOA','B3_TOA','B4_TOA','B5_TOA','B6_TOA','B7_TOA',
            'R_expected','G_expected','B_expected','R_saved','G_saved','B_saved','R_display','G_display','B_display','max_error'])
        for i in selected: w.writerow([*positions[i],classes[i],*source[i],*expected[i],*observed[i],*rgb[i],errors[i].max()])
    hist=[]
    for i in range(3):
        counts,edges=np.histogram(observed[:,i],bins=80)
        hist.append(dict(edges=edges.tolist(),counts=counts.tolist()))
    result=dict(scene_id=m['LANDSAT_SCENE_ID'],input_metadata=str(metadata),analytical=str(analytical),display=str(display),grid=grid,
        formulas=['B6/B7','B6/B2','(B4/B5)*(B6/B5)'],metadata_sha256=hashes[str(metadata)],
        full_statistics=dict(valid_pixels=count,nodata_pixels=nodata,nonfinite_unmasked=nonfinite,min=minima.tolist(),max=maxima.tolist(),
            mean=mean.tolist(),std_population=std.tolist(),correlation=correlation.tolist(),display_mask_mismatch_pixels=mismatch),
        sampled_statistics=dict(policy='Every 32nd native-resolution pixel in every raster block; QA and raw-range filtered; no overview',
            count=len(observed),quantile_percentages=quantiles,channel_quantiles=np.percentile(observed,quantiles,axis=0).T.tolist(),histograms=hist),
        independent_arithmetic=dict(stable_denominator_abs_min=.005,stable_samples=int(stable.sum()),
            stable_max_absolute_error=errors[stable].max(axis=0).tolist(),all_max_absolute_error=errors.max(axis=0).tolist(),
            stable_tolerance='1e-5 + 2e-5*abs(expected)',stable_pass=bool(passed),csv_pixels=len(selected)),
        display_reproduction_max_code_error=display_error.tolist(),display_config=config,groups=groups,
        class_policy='Nonexclusive diagnostic TOA NDVI/MNDWI rules resolved vegetation, water, then bare; proxies, no field labels or rock truth',
        exclusions='BQA fill/frame/terrain; snow/cirrus/cloud confidence >=2; raw zero/saturated65535. Legacy QA cannot remove cloud shadows/per-band saturation.',
        interpretation='TOA, not SR or atmosphere-corrected study replication; cyan condition G>R+20 and B>R+20 on display code values only',
        source_stat_unchanged=all((Path(p).stat().st_size,Path(p).stat().st_mtime_ns)==v for p,v in before.items()),
        protected_hashes_unchanged=all(digest(Path(p))==h for p,h in hashes.items()),protected_hashes=hashes,
        elapsed_seconds=time.monotonic()-started)
    (output/'numerical_audit.json').write_text(json.dumps(result,indent=2,allow_nan=False),'utf-8')
    if not passed or mismatch or nonfinite or not result['protected_hashes_unchanged'] or not result['source_stat_unchanged']:
        raise AssertionError('Audit failed; inspect numerical_audit.json')
    print(json.dumps({k:result[k] for k in ('full_statistics','independent_arithmetic','groups','elapsed_seconds')},indent=2))
    return result


if __name__=='__main__':
    p=argparse.ArgumentParser(); p.add_argument('--scene',type=Path,required=True)
    p.add_argument('--analytical',type=Path,required=True); p.add_argument('--display',type=Path,required=True)
    p.add_argument('--output',type=Path,required=True); args=p.parse_args()
    audit(args.scene,args.analytical,args.display,args.output)

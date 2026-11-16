"""Windowed RGB priority merge; a pixel's three channels always share one scene."""
import hashlib
import json
import math
from pathlib import Path
import uuid
from contextlib import ExitStack
import numpy as np
import rasterio
from rasterio.vrt import WarpedVRT
from rasterio.windows import Window
from rasterio.transform import from_origin
from rasterio.enums import Resampling, ColorInterp
from atiaf_core.raster.safe_io import atomic_raster


def merge_rgb(pairs,root,method,canceled=lambda:False):
    pairs=sorted(pairs,key=lambda p:(p[0].metadata.cloud_cover_percent if p[0].metadata.cloud_cover_percent is not None else 101,
                                    p[0].metadata.scene_id))
    set_id=hashlib.sha256(';'.join(s.metadata.scene_id for s,_ in pairs).encode()).hexdigest()[:10]
    directory=Path(root)/'Results'/('Mosaic_'+set_id)/'Geological_Color_Composites'/method
    directory.mkdir(parents=True,exist_ok=True)
    path=directory/f'RGB_{uuid.uuid4().hex}.tif'; source_path=path.with_name(path.stem+'_Source_Scene_ID.tif')
    with ExitStack() as stack:
        readers=[stack.enter_context(rasterio.open(p)) for _,p in pairs]
        ref=readers[0]
        if any(ds.crs!=ref.crs or ds.count!=3 for ds in readers):
            raise ValueError('Composite mosaic requires a common output CRS and three RGB channels')
        xres,yres=map(abs,ref.res)
        left=min(ds.bounds.left for ds in readers); right=max(ds.bounds.right for ds in readers)
        top=max(ds.bounds.top for ds in readers); bottom=min(ds.bounds.bottom for ds in readers)
        # Snap the union to the first selected scene's grid origin.
        left=ref.transform.c+math.floor((left-ref.transform.c)/xres)*xres
        top=ref.transform.f+math.ceil((top-ref.transform.f)/yres)*yres
        width,height=math.ceil((right-left)/xres),math.ceil((top-bottom)/yres)
        transform=from_origin(left,top,xres,yres)
        vrts=[stack.enter_context(WarpedVRT(ds,crs=ref.crs,transform=transform,width=width,height=height,
                                          resampling=Resampling.nearest,nodata=np.nan)) for ds in readers]
        profile=dict(driver='GTiff',width=width,height=height,count=3,dtype='float32',crs=ref.crs,transform=transform,
                     nodata=np.nan,compress='lzw',tiled=True,blockxsize=256,blockysize=256)
        with atomic_raster(path,**profile) as out, atomic_raster(source_path,**dict(profile,count=1,dtype='uint32',nodata=0)) as ids:
            for y in range(0,height,256):
                for x in range(0,width,256):
                    if canceled(): raise InterruptedError('Composite mosaic canceled; per-scene products preserved')
                    win=Window(x,y,min(256,width-x),min(256,height-y))
                    data=np.full((3,int(win.height),int(win.width)),np.nan,dtype='float32')
                    source=np.zeros(data.shape[1:],dtype='uint32')
                    for index,ds in enumerate(vrts,1):
                        values=ds.read(window=win,masked=True)
                        valid=~np.any(np.ma.getmaskarray(values),axis=0)&np.all(np.isfinite(values.data),axis=0)&(source==0)
                        data[:,valid]=values.data[:,valid]; source[valid]=index
                    out.write(data,window=win); ids.write(source,1,window=win)
            out.colorinterp=(ColorInterp.red,ColorInterp.green,ColorInterp.blue)
            out.update_tags(MOSAIC_POLICY='Priority: lowest scene cloud cover, then scene ID; first valid complete triplet. No averaging.')
    path.with_suffix('.json').write_text(json.dumps(dict(method=method,source_scene_id_raster=str(source_path),
        scene_table=[dict(code=i,scene_id=s.metadata.scene_id,date=s.metadata.acquisition_date.isoformat(),path=str(p))
                     for i,(s,p) in enumerate(pairs,1)],policy='Same sensor/level/day; QA-masked per-scene analytical results; first valid RGB triplet',
        field_validation='not claimed'),indent=2),'utf-8')
    return path

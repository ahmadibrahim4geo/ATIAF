"""Scientific diagnostic figures; reduced previews are not quantitative samples."""
import argparse,json,sys
from pathlib import Path
import numpy as np
import rasterio
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from atiaf_core.composites import render


def plot(receipt):
    data=json.loads(receipt.read_text('utf-8')); output=receipt.parent
    with rasterio.open(data['analytical']) as ds:
        factor=min(1.,640/max(ds.width,ds.height))
        sample=ds.read(out_shape=(3,round(ds.height*factor),round(ds.width*factor)),masked=True).astype('float32').filled(np.nan)
    fig,axes=plt.subplots(1,4,figsize=(16,5),layout='constrained')
    rows=[]
    for ax,(method,gamma) in zip(axes,[('linear',1),('percentile',1),('stddev',1),('percentile',.85)]):
        config=render.settings(dict(stretch_method=method,display_mode='custom',display_gamma=gamma))
        config['channel_limits']=render.limits(sample,config)
        rgba=np.moveaxis(np.concatenate([render.colorize(sample,config),np.where(np.all(np.isfinite(sample),axis=0),255,0)[None,:,:].astype('uint8')]),0,-1)
        ax.imshow(rgba); ax.set_title(method+'; gamma='+str(gamma)); ax.axis('off'); rows.append(config)
    fig.suptitle('CRC1: identical analytical channels; display settings only. Reduced preview, no rock classification.')
    fig.savefig(output/'stretch_comparison.png',dpi=140); plt.close(fig)
    (output/'stretch_comparison_settings.json').write_text(json.dumps(rows,indent=2),'utf-8')
    fig,axes=plt.subplots(1,3,figsize=(13,4),layout='constrained')
    for i,(ax,label,color) in enumerate(zip(axes,['R = B6/B7','G = B6/B2','B = (B4/B5)*(B6/B5)'],['red','green','blue'])):
        row=data['sampled_statistics']['histograms'][i]
        edges=np.array(row['edges']); ax.stairs(row['counts'],edges,color=color); ax.set_title(label)
        ax.set_xlabel('Dimensionless analytical ratio'); ax.set_ylabel('Native-resolution sample count')
    fig.savefig(output/'channel_histograms.png',dpi=140); plt.close(fig)


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('receipt',type=Path);plot(p.parse_args().receipt)

"""Reproducible sampled stretch; analytical values are never modified in place."""
from pathlib import Path
import base64
import html
import io
import json
import numpy as np
import rasterio
from rasterio.io import MemoryFile

MODES = {'quiet': (1., 1., .8), 'balanced': (2., 1., 1.), 'enhanced': (5., .85, 1.2)}


def settings(options):
    stretch=options.get('stretch_method') or 'percentile'
    deviations=float(options['display_stddev'] if options.get('display_stddev') is not None else 2)
    if stretch not in ('percentile','linear','stddev') or not np.isfinite(deviations) or not .1<=deviations<=10:
        raise ValueError('Composite stretch requires percentile/linear/stddev and .1<=standard deviations<=10')
    mode = options.get('display_mode') or 'balanced'
    clip, gamma, saturation = MODES.get(mode, (2., 1., 1.))
    if mode == 'custom':
        clip = float(options.get('display_clip', 2))
        gamma = float(options.get('display_gamma', 1))
        saturation = float(options.get('display_saturation', 1))
    elif mode not in MODES:
        raise ValueError('Composite unknown display mode')
    if not all(np.isfinite([clip,gamma,saturation])) or not 0 <= clip < 50 or not .05 <= gamma <= 10 or not 0 <= saturation <= 3:
        raise ValueError('Composite display requires 0<=clip<50, .05<=gamma<=10 and 0<=saturation<=3')
    manual=options.get('display_limits')
    fixed=None
    if manual:
        try:
            values=[float(v) for v in str(manual).split(',')]
            if len(values)!=6 or not np.all(np.isfinite(values)) or any(values[i]>values[i+1] for i in (0,2,4)):
                raise ValueError()
            fixed=[values[i:i+2] for i in (0,2,4)]
        except (TypeError,ValueError) as exc:
            raise ValueError('Composite fixed display limits need Rmin,Rmax,Gmin,Gmax,Bmin,Bmax, finite and ascending') from exc
    return dict(mode=mode, stretch_method=stretch,standard_deviations=deviations,
                clip_percent_each_tail=clip, gamma=gamma, saturation=saturation,fixed_limits=fixed,
                sample_policy='Deterministic nearest-neighbor grid, maximum 512 by 512; not full-scene exact quantiles',
                extent_policy='Fixed output footprint; never current map extent')


def limits(sample, config):
    valid = np.all(np.isfinite(sample), axis=0)
    if not np.any(valid):
        raise ValueError('Composite has no valid RGB pixels after masks and arithmetic')
    if config.get('fixed_limits'):
        return config['fixed_limits']
    result = []
    for band in sample:
        values=band[valid].astype('float64')
        method=config.get('stretch_method','percentile')
        if method=='linear': lo,hi=values.min(),values.max()
        elif method=='stddev':
            mean,std=values.mean(),values.std()
            lo,hi=mean-config['standard_deviations']*std,mean+config['standard_deviations']*std
        else: lo, hi = np.percentile(values, [config['clip_percent_each_tail'],100-config['clip_percent_each_tail']])
        # Constant channels remain visible, without inventing a physical range.
        result.append([float(lo),float(hi)])
    return result


def colorize(data, config):
    valid = np.all(np.isfinite(data), axis=0)
    out = np.zeros(data.shape, dtype='float32')
    for i,(lo,hi) in enumerate(config['channel_limits']):
        out[i] = np.clip((data[i]-lo)/(hi-lo),0,1) if hi>lo else .5
    out = np.power(out, 1/config['gamma'])
    luminance = (.2126*out[0]+.7152*out[1]+.0722*out[2])[None,:,:]
    out = np.clip(luminance + config['saturation']*(out-luminance),0,1)
    # Reserve zero for NoData, while preserving valid black as 1.
    return np.where(valid[None,:,:], np.rint(out*254)+1,0).astype('uint8')


def png_bytes(data, config):
    rgb = colorize(data,config)
    alpha = np.where(np.all(np.isfinite(data),axis=0),255,0).astype('uint8')
    rgba = np.concatenate([rgb,alpha[None,:,:]],axis=0)
    with MemoryFile() as mem:
        with mem.open(driver='PNG',count=4,width=rgba.shape[2],height=rgba.shape[1],dtype='uint8') as ds:
            ds.write(rgba)
        return mem.read()


def preview_html(sample, config, title, language='en'):
    baseline = settings(dict(display_mode='quiet'))
    baseline['channel_limits'] = limits(sample,baseline)
    def uri(c): return 'data:image/png;base64,'+base64.b64encode(png_bytes(sample,c)).decode('ascii')
    ar = language=='ar'
    labels = ['قبل التحسين المختار','بعد التحسين المختار'] if ar else ['Before selected enhancement','After selected enhancement']
    note = ('نفس القنوات التحليلية في الصورتين؛ الفرق في العرض فقط. معاينة مخفضة، وليست تصنيفًا أو إثباتًا لنوع الصخور.' if ar else
            'The same analytical channels in both views; only display changes. Reduced preview, not classification or proof of rock type.')
    interpretation=('السماوي يعني ارتفاع قناتي العرض الخضراء والزرقاء بالنسبة للحمراء بعد التمديد. يعتمد اللون على الوصفة والمعايرة والمشهد وإعدادات العرض؛ لا يدل وحده على معدن. المصدر العلمي:' if ar else
        'Cyan means stronger green and blue display channels relative to red after stretch. Color depends on recipe, calibration, scene and display; it does not identify a mineral. Scientific source:')
    return ('<!doctype html><html lang="'+language+'" dir="'+('rtl' if ar else 'ltr')+'"><meta charset="utf-8">'
        '<title>'+html.escape(title)+'</title><style>body{font:16px sans-serif;background:#13222d;color:#eee;padding:20px}'
        'main{display:flex;flex-wrap:wrap;gap:15px}figure{margin:0;flex:1;min-width:260px}img{width:100%;image-rendering:auto}'
        'pre{white-space:pre-wrap;direction:ltr;text-align:left}</style><h1>'+html.escape(title)+'</h1><p>'+note+'</p><main>'+
        ''.join('<figure><figcaption>'+label+'</figcaption><img alt="'+label+'" src="'+uri(c)+'"></figure>' for label,c in zip(labels,[baseline,config]))+
        '</main><p>'+interpretation+' '+html.escape(str(config.get('scientific_source','')))+
        '</p><pre>'+html.escape(json.dumps(config,ensure_ascii=False,indent=2))+'</pre></html>')


def raster_sample(path):
    with rasterio.open(path) as ds:
        factor = min(1.,512/max(ds.width,ds.height))
        return ds.read(out_shape=(3,max(1,round(ds.height*factor)),max(1,round(ds.width*factor))),masked=True).astype('float32').filled(np.nan)

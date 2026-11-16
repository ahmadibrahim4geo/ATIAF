"""Complete native output comparison, including every pixel and validity mask."""
import argparse,json
from pathlib import Path
import numpy as np
import rasterio


def compare(left,right):
    with rasterio.open(left) as a,rasterio.open(right) as b:
        assert (a.crs,a.transform,a.width,a.height,a.count)==(b.crs,b.transform,b.width,b.height,b.count)
        valid=0;total=0
        for _,window in a.block_windows(1):
            am=a.read_masks(window=window);bm=b.read_masks(window=window)
            np.testing.assert_array_equal(am,bm)
            mask=np.all(am>0,axis=0)
            np.testing.assert_array_equal(a.read(window=window)[:,mask],b.read(window=window)[:,mask])
            valid+=int(mask.sum());total+=int(mask.size)
        return dict(left=str(left),right=str(right),total_pixels_per_channel=total,valid_pixels_per_channel=valid,
            channels=a.count,crs=a.crs.to_string(),valid_values_exactly_equal=True,masks_exactly_equal=True)


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('left',type=Path);p.add_argument('right',type=Path);p.add_argument('receipt',type=Path)
    args=p.parse_args();a=json.loads(args.left.read_text('utf-8'));b=json.loads(args.right.read_text('utf-8'))
    if 'outputs' in a:
        pairs=[]
        for row in a['outputs']:
            other=next(x for x in b['outputs'] if x['channels']==row['channels'])
            pairs.append(compare(Path(row['path']),Path(other['path'])))
            def display_for(path):
                record=next((Path(path).parent.parent/'Metadata').glob('*.json'))
                return Path(json.loads(record.read_text('utf-8'))['display_path'])
            pairs.append(compare(display_for(row['path']),display_for(other['path'])))
    else: pairs=[compare(Path(a['path']),Path(b['path']))]
    args.receipt.write_text(json.dumps(dict(status='pass',comparisons=pairs),indent=2),'utf-8')
    print(json.dumps(dict(status='pass',comparisons=len(pairs))))

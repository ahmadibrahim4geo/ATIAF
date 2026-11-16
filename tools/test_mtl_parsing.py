import pathlib
import xml.etree.ElementTree as ET
from atiaf_core.discovery.landsat_profiles import parse_profile, BandRole, BandAsset, ProductLevel
import atiaf_core.discovery.landsat_profiles as lp

p1 = pathlib.Path('Testing Data/LC09_L2SP_174043_20261105_20261110_02_T1')
p2 = pathlib.Path('Testing Data/LC81760392014234LGN00')

def patched_read_file(path):
    text = lp._bounded(path)
    data = {}
    if path.suffix.lower() == '.json':
        return lp._read_file(path)
    elif path.suffix.lower() == '.xml':
        root = ET.fromstring(text)
        def _parse_xml(node, in_l1=False):
            tag = node.tag.split('}')[-1].upper()
            is_l1 = in_l1 or ('LEVEL1' in tag)
            if node.text and node.text.strip() and not list(node):
                val = node.text.strip()
                if is_l1:
                    data.setdefault('L1_' + tag, val)
                    data.setdefault(tag, val)
                else:
                    data[tag] = val
            for child in node:
                _parse_xml(child, is_l1)
        _parse_xml(root)
    else:
        stack = []
        for line in text.splitlines():
            line = line.strip()
            if line.startswith('GROUP =') or line.startswith('GROUP='):
                stack.append(line.split('=', 1)[1].strip())
            elif line.startswith('END_GROUP =') or line.startswith('END_GROUP='):
                if stack: stack.pop()
            elif '=' in line:
                key, value = line.split('=', 1)
                k = key.strip().upper()
                v = value.strip().strip('"')
                if k not in ('GROUP', 'END_GROUP'):
                    if any('LEVEL1' in g.upper() for g in stack):
                        data.setdefault('L1_' + k, v)
                        data.setdefault(k, v)
                    else:
                        data[k] = v
    return data, path

lp._read_file = patched_read_file

# Test parsing
s1 = lp.parse_profile(p1)
print('S1 Thermal:', s1.bands.get(BandRole.THERMAL_1))

s2 = lp.parse_profile(p2)
# Check L1 thermal
m = lp.read_metadata(p2)[0]
n = 10
filename = m.get(f'FILE_NAME_BAND_{n}')
source = lp._path(p2, filename) or lp._find(p2, f'_B{n}.TIF', f'_b{n}.tif')
print('S2 Thermal source:', source)
rm, ra = f'RADIANCE_MULT_BAND_{n}', f'RADIANCE_ADD_BAND_{n}'
print('S2 Radiance scale/offset:', m.get(rm), m.get(ra))
print('S2 K1/K2:', m.get(f'K1_CONSTANT_BAND_{n}'), m.get(f'K2_CONSTANT_BAND_{n}'))

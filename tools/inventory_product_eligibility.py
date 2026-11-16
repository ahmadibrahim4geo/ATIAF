"""Reproducible method-by-product gate inventory, distinct from execution proof."""
import csv,json,sys,tempfile
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path[:0]=[str(ROOT),str(ROOT/'tests')]
from test_legacy_profiles_and_audit import HistoricalProducts
from workflow_fixture import make_scene
from atiaf_core.workflow import discover,unavailable_reason
from atiaf_core.tool_contract import CATALOG,TITLES
from atiaf_core.composites.engine import validate_request


def inventory(output):
    output.mkdir(parents=True,exist_ok=True)
    fixture=HistoricalProducts(); fixture.setUp()
    profiles={
        'L8_PRE_L1T':fixture.landsat(name='pre'),
        'L8_C1_L1TP':fixture.landsat(collection=1,level='L1TP',name='c1l1'),
        'L8_C1_L2SR':fixture.landsat(collection=1,level='L2SR',name='c1sr'),
        'L8_C2_L1TP':fixture.landsat(collection=2,level='L1TP',name='c2l1'),
        'L8_C2_L2SP':make_scene(fixture.root/'official'),
        'L9_C2_L2SR':fixture.landsat(number=9,collection=2,level='L2SR',name='l9'),
        'L7_C1_L1_PRE_SLC':fixture.landsat(number=7,collection=1,date='2002-05-01',name='l7pre'),
        'L7_C1_L1_SLC_OFF':fixture.landsat(number=7,collection=1,date='2004-01-01',name='l7off'),
        'L5_TM_C1_L2SR':fixture.landsat(number=5,collection=1,level='L2SR',date='1994-08-22',name='tm5'),
        'L4_TM_C1_L2SR':fixture.landsat(number=4,collection=1,level='L2SR',date='1984-08-22',name='tm4'),
        'L4_MSS_L1':fixture.landsat(number=4,sensor='MSS',date='1984-08-22',name='mss'),
        'S2_L1C_PB04':fixture.sentinel(level='1C',name='s2l1'),
        'S2_L2A_PB04':fixture.sentinel(name='s2l2'),
        'S2_L2A_PB03':fixture.sentinel(baseline='03.01',offsets=False,name='s2old'),
    }
    real=ROOT/'Testing Data'/'LC81760392014234LGN00'
    if real.is_dir(): profiles['REAL_L8_2014_PRE_L1T']=real
    rows=[]; metadata={}
    try:
        for name,path in profiles.items():
            scene=discover(path)[0]; metadata[name]=scene.metadata.to_dict()
            for tool in TITLES:
                for calculation in CATALOG[tool]:
                    method=calculation['id']; options={'allow_toa':True}
                    if tool=='geological_composites':
                        try: validate_request(path,[method],options=options,apply_qa=False); reason=''
                        except ValueError as exc: reason=str(exc)
                    else: reason=unavailable_reason(tool,method,scene,options)
                    rows.append(dict(profile=name,tool=tool,method=method,
                        gate='INELIGIBLE' if reason else 'ELIGIBLE_BY_METHOD_GATE',reason=reason,
                        product_evidence='REAL_METADATA' if name.startswith('REAL') else 'SYNTHETIC_METADATA',
                        execution='NOT_RUN_BY_INVENTORY',
                        conditions='Diagnostic TOA allowed for NDVI/composites only; composites QA-independent inspection; no experimental opt-in. Temporal needs second date; thermal statistics need appropriate masks/reference.'))
        for name in ('ASTER_PRE_2008_REAL','ASTER_POST_2008_REAL','ROCKY_FIELD_REFERENCE_REAL','SAME_ACQUISITION_C2_REAL'):
            for tool in TITLES:
                for calculation in CATALOG[tool]:
                    rows.append(dict(profile=name,tool=tool,method=calculation['id'],gate='NOT_TESTED',reason='No supplied product/reference',
                        product_evidence='NOT_AVAILABLE',execution='NOT_RUN_BY_INVENTORY',conditions='No synthetic substitution for real-product acceptance'))
        with (output/'method_product_matrix.csv').open('w',newline='',encoding='utf-8') as f:
            writer=csv.DictWriter(f,fieldnames=list(rows[0]));writer.writeheader();writer.writerows(rows)
        payload=dict(policy='Method eligibility gates, not preflight, algorithm execution, real acquisition validation or release support',
            tools=TITLES,catalog=CATALOG,profiles=metadata,rows=rows)
        (output/'method_product_matrix.json').write_text(json.dumps(payload,indent=2,ensure_ascii=False),'utf-8')
        print(json.dumps(dict(tools=len(TITLES),method_entries=sum(len(CATALOG[t]) for t in TITLES),profiles=len(profiles)+4,cells=len(rows))))
    finally: fixture.tearDown()


if __name__=='__main__': inventory(Path(sys.argv[1]))

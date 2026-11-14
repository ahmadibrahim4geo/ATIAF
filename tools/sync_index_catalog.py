#!/usr/bin/env python3
"""Developer-only optional fetch: candidate MIT index catalog, NEVER an auto-enabled production registry.
Requires network on the developer machine. Catalog v1 is experimental: inspect/pin/validate before adoption.
"""
import argparse, datetime, hashlib, json, pathlib, urllib.request
ROOT=pathlib.Path(__file__).resolve().parents[1]
BASE='https://raw.githubusercontent.com/awesome-spectral-indices/awesome-spectral-indices/'
OUT=ROOT/'scientific_library'/'catalog_upstream'

def main():
 p=argparse.ArgumentParser();p.add_argument('--commit',required=True,help='Pin an immutable upstream Git SHA (not moving branch)');p.add_argument('--dry-run',action='store_true');a=p.parse_args()
 if len(a.commit)<40 or any(c not in '0123456789abcdefABCDEF' for c in a.commit):p.error('--commit must be full 40-character Git SHA')
 files={'spectral-indices-dict.json':'output/v1/spectral-indices-dict.json','LICENSE':'LICENSE'}
 if a.dry_run:
  for name,relative in files.items(): print(BASE+a.commit+'/'+relative,'->',OUT/name)
  return
 OUT.mkdir(parents=True,exist_ok=True)
 receipt={'source':'https://github.com/awesome-spectral-indices/awesome-spectral-indices','commit':a.commit,'retrieved_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'status':'UNREVIEWED_CANDIDATES','files':{}}
 for name,relative in files.items():
  req=urllib.request.Request(BASE+a.commit+'/'+relative,headers={'User-Agent':'ATIAF-dev-catalog-sync/0.1'})
  with urllib.request.urlopen(req,timeout=35) as r:data=r.read(15_000_000)
  if not data:raise RuntimeError('Empty download: '+name)
  (OUT/name).write_bytes(data)
  receipt['files'][name]={'bytes':len(data),'sha256':hashlib.sha256(data).hexdigest()}
 json.loads((OUT/'spectral-indices-dict.json').read_text('utf-8'))
 (OUT/'UPSTREAM_RECEIPT.json').write_text(json.dumps(receipt,ensure_ascii=False,indent=2)+'\n','utf-8')
 print('Catalog downloaded but NOT scientifically reviewed, installed or enabled: ',OUT)
if __name__=='__main__':main()

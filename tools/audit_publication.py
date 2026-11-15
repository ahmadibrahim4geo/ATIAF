"""Conservative local audit of Git's intended project files; never prints secret values.

This narrow check is not a comprehensive SAST/secret-scanning certification.
It uses the current Git file selection, skips deleted paths and does not upload anything.
"""
from pathlib import Path
import argparse
import hashlib
import json
import re
import subprocess

ROOT = Path(__file__).resolve().parents[1]
DATA_SUFFIXES = {'.tif','.tiff','.jp2','.hdf','.h5','.nc','.zip','.tar','.gz','.7z','.whl','.pyc'}
FORBIDDEN_PARTS = {'.agent_resources','Work','Results','__pycache__','.venv','dist','build'}
PATTERNS = {
    'private_key': re.compile(rb'-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----'),
    'github_token': re.compile(rb'\bgh[pousr]_[A-Za-z0-9]{30,}\b|\bgithub_pat_[A-Za-z0-9_]{50,}\b'),
    'aws_access_id': re.compile(rb'\bAKIA[A-Z0-9]{16}\b'),
    'credential_url': re.compile(rb'https?://[^\s/:@]+:[^\s/@]+@'),
}

def audit(staged=False):
    arguments = ['git','ls-files','-z','--cached']
    if not staged:
        arguments += ['--others','--exclude-standard']
    raw = subprocess.check_output(arguments,cwd=ROOT)
    names = sorted(set(x.decode('utf-8') for x in raw.split(b'\0') if x))
    errors, inventory = [], []
    for name in names:
        path = ROOT/name
        if not path.is_file():
            continue
        if not path.resolve().is_relative_to(ROOT):
            errors.append({'path':name,'reason':'outside authorized root'})
            continue
        if any(part in FORBIDDEN_PARTS for part in path.relative_to(ROOT).parts) or path.suffix.lower() in DATA_SUFFIXES:
            errors.append({'path':name,'reason':'data/cache/build artifact in publication selection'})
        if path.name.startswith('.env') or path.suffix.lower() in ('.key','.pem') or path.name.endswith('.pyt.xml'):
            errors.append({'path':name,'reason':'local credential/environment or host-generated file'})
        data = path.read_bytes()
        if len(data)>20*1024*1024:
            errors.append({'path':name,'reason':'file exceeds 20 MiB publication review limit'})
        if path.suffix.lower() not in ('.png','.jpg','.jpeg','.gif','.ico'):
            for label,pattern in PATTERNS.items():
                if pattern.search(data):
                    errors.append({'path':name,'reason':label+' pattern; inspect locally'})
        inventory.append({'path':name,'bytes':len(data),'sha256':hashlib.sha256(data).hexdigest()})
    return dict(status='FAIL' if errors else 'PASS',selection='staged' if staged else 'current tracked + unignored files',
                files=len(inventory),bytes=sum(x['bytes'] for x in inventory),findings=errors,inventory=inventory,
                limitation='Narrow file/secret-pattern audit, not exhaustive security certification')

if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--staged',action='store_true')
    parser.add_argument('--output')
    options=parser.parse_args()
    result=audit(options.staged)
    if options.output:
        target=(ROOT/options.output).resolve()
        if not target.is_relative_to(ROOT):
            raise ValueError('Audit output must stay within ATIAF')
        target.parent.mkdir(parents=True,exist_ok=True)
        with target.open('x',encoding='utf-8') as stream:
            json.dump(result,stream,indent=2)
    print(json.dumps({k:v for k,v in result.items() if k!='inventory'},indent=2))
    raise SystemExit(0 if result['status']=='PASS' else 1)

#!/usr/bin/env python3
"""Clone user-owned GIS skills into project-local .agent_resources without executing external code.
Explicit instructions in AGENTS.md tell agents to READ the actual SKILL.md and references.
"""
import argparse, datetime, json, pathlib, subprocess, sys
ROOT=pathlib.Path(__file__).resolve().parents[1]
REPO='https://github.com/ahmadibrahim4geo/GIS-Development-Skills.git'
DEST=ROOT/'.agent_resources'/'GIS-Development-Skills'
MANIFEST=ROOT/'development_resources'/'skills_manifest.json'

def git(*args, check=True):
    return subprocess.run(['git',*map(str,args)],text=True,capture_output=True,check=check,timeout=180)

def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--verify',action='store_true',help='Verify locally available skills; do not connect')
    a=ap.parse_args()
    m=json.loads(MANIFEST.read_text('utf-8'))
    if not DEST.exists():
        if a.verify: print('NOT INSTALLED:',DEST);return 2
        DEST.parent.mkdir(exist_ok=True)
        print('Cloning approved skills into',DEST)
        try:r=git('clone','--depth','1','--single-branch',REPO,DEST)
        except (OSError,subprocess.CalledProcessError,subprocess.TimeoutExpired) as e:
            print('FAILED TO INSTALL (no fake success):',str(e)[:600]);return 3
    if not (DEST/'.git').exists():print('Directory exists but is not a git checkout:',DEST);return 4
    try: sha=git('-C',DEST,'rev-parse','HEAD').stdout.strip()
    except Exception as e:print('Cannot verify checkout SHA',e);return 5
    missing=[]
    for skill in m['mandatory']:
        p=DEST/'skills'/skill/'SKILL.md'
        if not p.is_file():missing.append(str(p.relative_to(DEST)))
    if missing:
        print('Mandatory skill files missing:',*missing,sep='\n  ')
        return 6
    print('Verified source:',REPO,'\nCommit SHA:',sha,'\nMandatory skill files:',len(m['mandatory']))
    print('Agent must read files and references from:',DEST)
    if not a.verify:
        record={'source_url':REPO,'commit_sha':sha,'installed_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'local_root':str(DEST),'mandatory_skills':m['mandatory'],'execution':'none; content was not executed'}
        (DEST.parent/'skills_install_receipt.json').write_text(json.dumps(record,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
    return 0
if __name__=='__main__':sys.exit(main())

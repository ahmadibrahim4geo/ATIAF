#!/usr/bin/env python3
"""Structural QA for the *documentation handoff*, not a GIS processing engine test."""
import json, pathlib, re, sys, urllib.parse
root=pathlib.Path(__file__).resolve().parents[1]
required=['AGENTS.md','START_AGENT_PROMPT.txt','PROJECT_STATE.md','DECISIONS.md','PROJECT_SPECIFICATION.md','PROJECT_SPECIFICATION_AR.md','DEVELOPMENT_ROADMAP.md','DEVELOPMENT_ROADMAP_AR.md','README.md','README.ar.md','LICENSE','Development_Plans/INDEX.md','Reports/INDEX.md','development_resources/REPOSITORIES.md','development_resources/SKILLS_REGISTRY.md','development_resources/SOURCES.md','scientific_library/sensors/sensor_registry.json','scientific_library/indices/candidate_indices.json','docs/ar/SENSORS_AND_DOWNLOADS.md','docs/en/SENSORS_AND_DOWNLOADS.md','docs/ar/SCIENTIFIC_METHODS.md','docs/en/SCIENTIFIC_METHODS.md']
err=[]
for f in required:
 if not (root/f).is_file():err.append('Missing '+f)
json_files=list(root.rglob('*.json'))
for file in json_files:
 try:json.loads(file.read_text(encoding='utf-8'))
 except Exception as e:err.append('Bad JSON '+str(file.relative_to(root))+': '+str(e))
try:
 data=json.loads((root/'scientific_library/indices/candidate_indices.json').read_text('utf-8'))
 ids=[x['id'] for x in data['items']]
 if len(ids)!=len(set(ids)):err.append('Duplicate index IDs')
 if any(x.get('status')!='CANDIDATE_UNVERIFIED' for x in data['items']):err.append('Candidate index claimed verified')
 print('Candidate indices:',len(ids))
 s=json.loads((root/'scientific_library/sensors/sensor_registry.json').read_text('utf-8'))['sensors']
 if any(x['implementation_status']!='PLANNED_NOT_TESTED' for x in s):err.append('Sensor falsely claimed implemented')
 print('Planned sensors:',len(s))
except Exception as e:err.append(str(e))
# Check relative Markdown links to locally stored files (ignore http and anchors)
for file in root.rglob('*.md'):
 if '.agent_resources' in file.parts:continue
 t=file.read_text(encoding='utf-8')
 for target in re.findall(r'\]\(([^)]+)\)',t):
  if target.startswith(('http://','https://','mailto:','#')):continue
  target=urllib.parse.unquote(target.split('#')[0].strip())
  if not target:continue
  if not (file.parent/target).exists():err.append('Broken local link '+str(file.relative_to(root))+' -> '+target)
print('Markdown files:',len(list(root.rglob('*.md'))),'JSON:',len(json_files))
if err:
 print('STRUCTURAL VALIDATION FAILED:');print('\n'.join(err));sys.exit(1)
print('STRUCTURAL VALIDATION PASS — documentation only. Native ArcGIS/QGIS tests NOT RUN.')

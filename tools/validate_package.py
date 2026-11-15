#!/usr/bin/env python3
"""Structural QA for the *documentation handoff*, not a GIS processing engine test."""
import json, pathlib, re, sys, urllib.parse
root=pathlib.Path(__file__).resolve().parents[1]
required=['AGENTS.md','documentation/project/START_AGENT_PROMPT.txt','PROJECT_STATE.md','documentation/project/DECISIONS.md','documentation/project/PROJECT_SPECIFICATION.md','documentation/project/PROJECT_SPECIFICATION_AR.md','documentation/project/DEVELOPMENT_ROADMAP.md','documentation/project/DEVELOPMENT_ROADMAP_AR.md','README.md','README.ar.md','LICENSE','Development_Plans/INDEX.md','Reports/INDEX.md','development_resources/REPOSITORIES.md','development_resources/SKILLS_REGISTRY.md','development_resources/SOURCES.md','scientific_library/sensors/sensor_registry.json','scientific_library/indices/candidate_indices.json','documentation/ar/SENSORS_AND_DOWNLOADS.md','documentation/en/SENSORS_AND_DOWNLOADS.md','documentation/ar/SCIENTIFIC_METHODS.md','documentation/en/SCIENTIFIC_METHODS.md']
err=[]
for f in required:
 if not (root/f).is_file():err.append('Missing '+f)
json_files=[p for p in root.rglob('*.json') if '.agent_resources' not in p.relative_to(root).parts and 'build' not in p.relative_to(root).parts]
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
from link_validation import broken_links
err.extend('Broken local link ' + message for message in broken_links())
print('Markdown files:',len(list(root.rglob('*.md'))),'JSON:',len(json_files))
if err:
 print('STRUCTURAL VALIDATION FAILED:');print('\n'.join(err));sys.exit(1)
print('STRUCTURAL VALIDATION PASS — documentation only. Native ArcGIS/QGIS tests NOT RUN.')

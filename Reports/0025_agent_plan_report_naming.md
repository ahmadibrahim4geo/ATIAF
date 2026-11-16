# 0025 — Descriptive plan and report naming

- Date: 2026-11-15. Plan: **PLAN-0017 r1**. Status: **VERIFIED for instruction/documentation scope**.
- Source: direct user request to preserve or derive a descriptive plan name and add its sequential number; reports need an independent sequential number and descriptive name.
- Baseline: `main`, commit `1d15bad`. Local, uncommitted change. The geological source plan remains unchanged.

## Acceptance evidence

| Criterion | Status / evidence |
|---|---|
| Any plan filename or conversational development request | VERIFIED: AGENTS.md step 8, indexes and startup prompt explicitly cover both; filename patterns are examples, and discussion alone does not authorize implementation. |
| Plan number plus descriptive name, source retention, stable revisions | VERIFIED: reviewed lifecycle rules preserve/derive titles, require an English safe numbered filename, retain original title/request, copy supplied files unchanged and record source, check all lifecycle folders/index for IDs, and retain IDs on revision. This plan demonstrates conversational intake. |
| Report number plus descriptive name | VERIFIED: AGENTS.md and report index require independent sequence, descriptive filename and matching heading, plan/revision link and no overwrite/reuse. Report 0025 references plan 0017. |
| Synchronized records and validation | VERIFIED: startup/registry/indexes, EN/AR specifications and changelog agree. Existing structure/link validation and whitespace check passed. Delivery report precedes archive; final recovery records and Journal handoff accompany delivery. |

## Files changed

AGENTS.md; plan/report indexes; startup prompt; skills registry; both project specifications; CHANGELOG.md; PROJECT_STATE.md; PLAN-0017 working/archive record; this report; Journal request/handoff and derived index/state. No runtime source changed.

## Commands and observed results

Python executable: `C:/Users/ahmad/AppData/Local/Python/pythoncore-3.14-64/python.exe`.

- `python tools/validate_package.py`: exit 0; 26 candidate indices, 19 planned sensors; `STRUCTURAL VALIDATION PASS`, including JSON and local Markdown/HTML links. Pre-delivery count: 885 Markdown / 96 JSON; final records add files.
- `git diff --check`: exit 0, no whitespace errors; CRLF-to-LF normalization notices only.
- `git diff -- AGENTS.md Development_Plans/INDEX.md Reports/INDEX.md documentation/project/START_AGENT_PROMPT.txt`: reviewed naming, intake, source/revision and independent sequence clauses.
- `python .agent_resources/GIS-Development-Skills/scripts/development_journal.py verify --project .`: 46 existing records valid before request. Authorized elevated helper append succeeded as **#0047**, resolving the earlier WinError 5 logging gap. Delivery handoff/final verification follow; no old history invented.
- `Get-FileHash -LiteralPath ATIAF_Geological_Color_Composites_Agent_Plan.md -Algorithm SHA256`: `07A9D78B226DCD82F56B24096D1B7E61DAEE0CE65546833EAC5C8D9709B23BE8`; file not edited or moved.
- One delivery patch failed context matching against a long state line and applied no changes; corrected with the exact line. No lost user content.

GIS host: **none**. Scientific/native tests: **NOT RUN / not applicable**, instruction-only scope. No automated plan mover, environment install, package build, commit or upload. Original code/docs remain MIT; no third-party code/data/assets added. This is evidence for instructions, not an automatic enforcement service.

## Handoff

Archive PLAN-0017 after this verified report, then confirm final links/whitespace and Journal integrity. Update state and indexes. PLAN-0015 remains Active/partial; PLAN-0016 remains complete. The geological source is unchanged and unregistered for implementation. Recheck IDs at its eventual authorized intake; 0017 is now allocated to this governance change. No blocker remains for this instruction change; existing scientific/native/clean-install gaps remain.

## التسليم بالعربية

عُدلت التعليمات لاستقبال الخطة بأي اسم أو أمر التطوير في المحادثة. يُحفظ الاسم الوصفي أو يوضع اسم عند غيابه، ثم يُضاف رقم الخطة وتحفظ نسخة العمل مع إبقاء الأصل. لكل تقرير رقم مستقل واسم واضح وعنوان مطابق وربط بالخطة ومراجعتها. تزامنت التعليمات والفهارس والمواصفات باللغتين ونجحت فحوص التوثيق والروابط والمسافات. لم يبدأ تنفيذ الخطة الجيولوجية.

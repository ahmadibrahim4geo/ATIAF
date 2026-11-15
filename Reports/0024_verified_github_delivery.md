# 0024 — Verified GitHub delivery

- Date: 2026-11-15. **PLAN-0016 r1: VERIFIED / COMPLETE.** PLAN-0015 r6 remains Active/partial.
- [Published repository](https://github.com/ahmadibrahim4geo/ATIAF) and [live bilingual Index](https://ahmadibrahim4geo.github.io/ATIAF/).
- Verified runtime/presentation source: `31794beb5c58b59b997d862d4689cb4001b56432`. This report and state/journal/archive are a subsequent records-only handoff commit; read its SHA from Git history. No force push or history rewrite.

## Acceptance and actual evidence

| Criterion | Result / observed evidence |
|---|---|
| Professional EN/AR README and offline Index, supplied logo then banner, tools/install/manual/interpretation/development scope | VERIFIED. Desktop/mobile browser checks and inspected screenshots in [publication evidence](evidence/PLAN-0016/desktop.json). Five key published files/assets have matching local/remote Git blob IDs. Live page HTTP 200; actual `img` element order is logo then banner. |
| Portable files and safe publication content | VERIFIED within declared scope. Contribution/security/citation/Git files present; original PNG inputs and scenes/build/skills caches preserved locally and excluded. Narrow publication audit PASS (415 staged files before subsequent records, then 418 current files); no security certification claimed. Original commit history preserved. |
| Documentation, regression, render checks, CI build and install artifacts | VERIFIED. Final hosted [headless/package run 43733305094](https://github.com/ahmadibrahim4geo/ATIAF/actions/runs/43733305094) **success**: docs/links/JSON, **141 tests PASS in 4.236 s**, QGIS ZIP and wheel build, source identity and isolated wheel import, both artifact uploads. Native GIS scope remains report 0021's bounded fixture checks. |
| Actual normal push and independent remote readback | VERIFIED. `git push origin main` succeeded; `git ls-remote` matched `31794be`; GitHub Contents API blob IDs matched `git hash-object` for README EN/AR, Index, logo and banner. Existing Pages configuration automatically deployed; [run 43733304028](https://github.com/ahmadibrahim4geo/ATIAF/actions/runs/43733304028) **success**. No Pages settings changed. |
| Permanent report/state/index/journal and correct plan status | VERIFIED through this delivery report, updated indexes/state, canonical journal verification and plan-bound DoneProof. Archive PLAN-0016 after this report; preserve PLAN-0015 Active and every earlier report/failure. |

Machine-readable [provider receipt](evidence/PLAN-0016/github_publication_receipt.json), [successful hosted log excerpts](evidence/PLAN-0016/hosted_success_excerpts.json), [retained hosted failures](evidence/PLAN-0016/hosted_failure_excerpts.json), [final clean-source check](evidence/PLAN-0016/clean_checkout_final.json) and [asset-order verification](evidence/PLAN-0016/site_asset_order_verification.json). The raw string-position field in the first receipt is false because social-image metadata mentions the banner first; corrected HTML-element parsing confirms displayed image order. Neither raw evidence was overwritten.

## Corrections, files and limits

Reports 0022 and 0023 remain immutable. Clean-source discovery exposed absent ignored parser placeholders and parent-path exclusions; tests now generate temporary synthetic stubs and validate relative paths. Fifty-five old local skills links now point to the reviewed MIT source SHA, without changing historical plan requirements. Hosted Windows TEMP short-name differences were fixed in test expectations. Hosted run 43733059500 then passed 141 tests but failed wheel creation because setuptools was absent; CI now explicitly installs `setuptools==84.0.0` and `wheel==0.48.0`. The next run passed the full pipeline. No processing algorithm changed in these publication fixes.

Artifacts are available on the successful run under **ATIAF-QGIS-development** and **ATIAF-core-development** (30-day CI retention; GitHub sign-in required). Unwrap the downloaded artifact archive to get the inner installable QGIS ZIP. These are development packages, not a stable GitHub release. Artifact IDs `14169342634` and `14168829836`; recorded digests in the receipt identify the outer CI archives, not the inner ZIP/wheel. Existing local dev0/dev1 build history remains preserved.

Original code remains MIT; supplied brand assets used with user authorization. No new imagery, restricted IDB catalog, third-party implementation or upstream skills changes. No paid APIs, local-processing downloads or runtime credentials introduced. Earlier auto-review usage-limit failure executed no action; subsequent authorized retry succeeded.

**NOT RUN / retained in PLAN-0015:** real L1/L2 acquisitions/independent calibration, clean-machine native installation, all-six interactive bilingual Pro/QGIS journeys, complete CRS/concurrency/crash-resume acceptance and proposed scientific/radar capabilities. Publication/CI does not certify these. Exact next step: continue PLAN-0015 r6 from its 21-criterion partial DoneProof using locally supplied real products and the matching current checkout/packages. No further publication permission is required for the already-authorized handoff commit.

## التسليم بالعربية

تم تجهيز المشروع ورفعه والتحقق منه فعليًا: README باللغتين وIndex مع الشعار ثم البانر، وأدلة التثبيت والتعيين اليدوي والحرارة وتفسير النتائج، وملفات المساهمة والاستشهاد. نجح فحص GitHub الكامل و141 اختبارًا وبناء الحزم وتطابق المصدر، وأصبحت الصفحة وملفات التنزيل متاحة. أُصلحت المشكلات التي كشفتها البيئة النظيفة وحُفظت نتائج الفشل السابقة. اكتملت خطة العرض والنشر فقط؛ خطة التحقق العلمي والواجهات الأصلية ما زالت نشطة، ولا يُعلن إصدار مستقر أو دعم رادار مكتمل.

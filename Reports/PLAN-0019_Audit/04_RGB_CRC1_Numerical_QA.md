# PLAN-0019 r1 — 04 CRC1 numerical/color audit

Audited **the exact** screenshot-referenced `...dad2439d6ee5_DISPLAY.tif` and its corresponding analytical TIFF/JSON under `Testing Results/PLAN-0018/standalone/.../Band_Ratio_RGB/`. All inspected source/output hashes and file size/time checks remained unchanged. Reproduce using `tools/audit_geological_outputs.py` with the explicit scene, analytical, display and a NEW output directory. Independent reference uses literal Float64 MTL calibration/formulas, not the project's arithmetic or rendering functions.

[Machine receipt](../evidence/PLAN-0019/exact_crc1_audit/numerical_audit.json), [100 selected pixels CSV](../evidence/PLAN-0019/exact_crc1_audit/independent_pixels.csv), [full invocation log](../evidence/PLAN-0019/exact_crc1_audit_command.txt). Every full-resolution pixel was examined for analytical moments, correlations and display mask agreement. Quantiles/histograms/arithmetic use **39,442 deterministic native-resolution samples** (39,440 stable-denominator points); see receipt for exact sample count. Samples read native windows, avoiding existing overviews. The CSV holds 25 spatially distributed samples per diagnostic group, not 100 confirmed rock sites.

| Full-resolution statistic | R=B6/B7 | G=B6/B2 | B=(B4/B5)×(B6/B5) |
|---|---:|---:|---:|
| Minimum | -75.79977 | -0.0345702 | -0.262787 |
| Maximum | 19.61924 | 8.118957 | 6.237548 |
| Mean | 1.410441 | 1.930752 | 0.706321 |
| Population std | 0.346589 | 0.662050 | 0.342878 |
| Stored display lower bound | 1.142607 | 0.266891 | 0.0458214 |
| Stored display upper bound | 2.352416 | 2.852600 | 1.030348 |

**40,394,219 valid pixels and 20,221,952 NoData pixels per channel**, total60,616,171. Unmasked nonfinite0; display/analytical validity disagreements0. Full correlations R/G=-0.5260, R/B=-0.9107, G/B=0.5379. Analytical Float32 vs separate display UInt8; display0 is NoData and valid black is1. Padding was excluded from stretch. Valid negative/outlier ratios are retained; small signed TOA denominators can produce long tails, so min/max is not a universal geological range. No unbounded-ratio clipping was introduced to make colors attractive.

Independent stable-sample max errors R≈1.60e-6, G≈5.43e-7, B≈9.81e-7; acceptance `abs(error)<=1e-5+2e-5*abs(reference)` with all denominators >0.005. All stable samples pass; receipt also records all-sample maxima. Independent Float64 reproduction of saved display is within **one UInt8 code** for R/G and exact for B, consistent with Float32 rounding, not a channel swap.

| Diagnostic group | Samples | Median analytical RGB | Median saved display RGB | Operational cyan fraction |
|---|---:|---|---|---:|
| Bare candidate | 24,296 | 1.204,2.369,0.936 | 14,207,231 | 99.72% |
| Vegetation proxy | 10,391 | 1.901,1.412,0.139 | 160,113,25 | 8.47% |
| Water proxy | 2,506 | 1.255,0.348,0.929 | 25,9,229 | 0.16% |
| Other | 2,249 | 1.333,1.779,0.589 | 41,150,141 | 83.86% |

Rules: vegetation TOA NDVI>0.3; water MNDWI>0.2 and NDVI<0.1; bare candidate 0≤NDVI<0.2, MNDWI<0, SWIR1>0.1, with documented precedence. These are **proxies**, not independent labels. Cyan operationally means G>R+20 and B>R+20 in saved display codes. **Inference from measured channels:** bare candidates occupy the low end of stretched R and high ends of G/B, explaining the cyan. That does not identify a rock or prove atmospheric correctness. No independently mapped rocky reference exists here.

[Stretch comparison](../evidence/PLAN-0019/exact_crc1_audit/stretch_comparison.png) and [settings](../evidence/PLAN-0019/exact_crc1_audit/stretch_comparison_settings.json) compare linear, percentile, stddev and gamma on identical analytical channels. These reduced previews may use source overviews and are not quantitative native-resolution samples. [Histograms](../evidence/PLAN-0019/exact_crc1_audit/channel_histograms.png) use the receipt's declared native sample. New display choices never modify analytic TIFFs. UI notes now explain cyan/channel dependence and show the recipe's scientific source in separate EN/AR text.

اللون السماوي مثبت من توزيع القنوات والتمديد، وليس علامة كافية على خطأ أو معدن. الأرقام والملفات والأقنعة صحيحة ضمن الاختبارات المعلنة؛ جودة التفسير الجيولوجي تحتاج مرجعًا مستقلاً.

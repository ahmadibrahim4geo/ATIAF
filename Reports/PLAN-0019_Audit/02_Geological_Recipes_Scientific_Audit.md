# PLAN-0019 r1 — 02 Scientific recipe audit

The screenshot appearance is not evidence of a wrong equation. The exact saved TIFF band descriptions, JSON and implementation agree on **R=B6/B7; G=B6/B2; B=(B4/B5)×(B6/B5)**. No channel was swapped and no recipe was changed in this audit.

| Stable recipe ID | R ; G ; B | Source/status |
|---|---|---|
| L89_753 | B7 ; B5 ; B3 | [Duwi 2024](https://www.nature.com/articles/s41598-024-66199-3), Fig.3, formula/order checked |
| L89_CRC1 | B6/B7 ; B6/B2 ; (B4/B5)×(B6/B5) | Same paper, Fig.10, checked |
| L89_CRC2 | B4/B6 ; B4/B2 ; B6/B7 | Same paper, Fig.11, checked |
| L89_762 | B7 ; B6 ; B2 | User proposal, experimental |
| S2_12114 | B12 ; B11 ; B4 | User proposal, experimental |
| S2_12112 | B12 ; B11 ; B2 | User proposal, experimental |
| ASTER_468 | B4 ; B6 ; B8 | User proposal; historical SWIR/date/explicit calibration gate, experimental |
| ASTER_FAWAKHEIR | (B2+B4)/B3N ; (B5+B7)/B6 ; (B7+B9)/B8 | Plan transcription; original full-text verification remains pending, experimental |

[Minerals 2022, 12(12),1577](https://www.mdpi.com/2075-163X/12/12/1577), section 4.2.1/Fig.4a, also describes 6/7, 6/2, (6/5)×(4/5). The blue multiplication is commutative, so it agrees algebraically. That corroborates the expression; it does not justify changing the existing Duwi attribution or importing another site's lithological color legend. Duwi's corrected processing context is not reproduced by this scene's TOA calibration. [Abu Ghalaga 2022](https://www.mdpi.com/2072-4292/14/14/3456) and [S2/L8 geological continuity 2016](https://www.mdpi.com/2072-4292/8/11/883) are comparison references, not blanket coefficients or validation of every experimental composition. The PMC10163254 fetch was blocked; no unreviewed formula was promoted from it.

For Landsat8 the nominal centers in the registry are B2 blue≈482 nm, B4 red≈655, B5 NIR≈865, B6 SWIR1≈1609, B7 SWIR2≈2201. These are reference nominal wavelengths, not wavelengths measured/extracted from this MTL. Physical TM/ETM+ SWIR1 is B5, not thermal B6; matching a numeric band label across missions is unsafe. T05's separate existing role-based ratios are Red/Blue, Red/Green, SWIR1/NIR, SWIR1/SWIR2 and SWIR1/Red. Proposed exact ASTER thermal mineral formulas remain gated in the normal workflow because automatic band semantics/product validation is incomplete; catalog presence is not executable support.

The [USGS Spectral Library v7](https://pubs.usgs.gov/publication/ds1035) provides measured spectral/reference context, including sample/instrument limitations. **Inference:** a broad multispectral ratio is not a mineral assay; mixed pixels, atmosphere, vegetation, moisture and display normalization make colors nonunique. No spectral library data, study image, geological map or third-party code was downloaded or redistributed here.

Code establishes bounded arithmetic/no eval, calibration and masks; saved raster arithmetic is measured in audit04. The visual preview remains continuous imagery. Bare/vegetation/water rules are diagnostic spectral proxies, not verified geological or land-cover classes. لا يوجد مفتاح عالمي يربط السماوي بمعدن؛ مراجعة المعادلة لا تعني تحققًا حقليًا.

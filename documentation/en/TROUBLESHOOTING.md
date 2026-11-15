# Troubleshooting

| Symptom | Action |
|---|---|
| Old order / absent controls | Close tool, Refresh toolbox/restart Pro. Open this complete checkout, not an old isolated copy. |
| Missing scientific library | Controls remain visible. Check the exact active host Python using the read-only helper, repair a compatible cloned environment and restart. |
| Empty selection | Check a calculation; open the multi-select list in QGIS. |
| Sensor mismatch / missing bands | Choose AUTO or correct metadata level; supply complete assets or reviewed expert mapping. |
| Missing QA | Restore actual mask or explicitly disable QA after assessing limitations. |
| Invalid CRS | Use native projected metre picker. Correctly define unknown source CRS first. |
| TVDI / SUHI / historical models gated | Required dry/wet edges, urban/rural references or historical baseline are not implemented as validated inputs yet. |
| AOI error | Supply valid nonempty polygon with known CRS. |
| Raster saved / no map layer | Open it manually; inspect native map warnings. Saved outputs remain independent of rendering. |

Record tool, selected methods, product level, host/environment and exact error. Do not upload imagery or private paths without consent. [Current evidence](../../PROJECT_STATE.md).

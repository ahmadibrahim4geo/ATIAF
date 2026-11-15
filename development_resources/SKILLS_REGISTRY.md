# Agent skills registry — approved sources, loading and reuse
**PRIMARY repository:** https://github.com/ahmadibrahim4geo/GIS-Development-Skills (user-owned). **Use the actual checked-out `SKILL.md` and its linked references**, not merely the name here. Source access uses `python tools/bootstrap_skills.py`, which clones a complete read-only snapshot to `.agent_resources/GIS-Development-Skills` and records a commit SHA. Installing a skill does not make it an executable plugin or cause automatic execution on every host; root `AGENTS.md` instructs each agent to load it explicitly.

| Task | Skill path inside GIS-Development-Skills | Status |
|---|---|---|
| GIS master router | `skills/gis-development/SKILL.md` | Core |
| User requirement interpretation | `skills/prompt-intent-orchestrator/SKILL.md` | Core |
| Permanent development logs / handoff | `skills/agent-development-journal/SKILL.md` | Core |
| Proof before done | `skills/completion-evidence/SKILL.md` | Core |
| ArcGIS Pro Python Toolbox + ArcPy | `skills/arcgis-toolbox-engineering/SKILL.md` | ArcGIS |
| Remote-sensing science and pipeline | `skills/remote-sensing-pipelines/SKILL.md` | Core |
| Raster GIS and GDAL | `skills/geospatial-data-processing/SKILL.md` | Core |
| QGIS Processing plugin | `skills/qgis-plugin-development/SKILL.md` | QGIS |
| Arabic/English RTL & translations | `skills/gis-internationalization-arabic/SKILL.md` | Core |
| Output coordinate systems | `skills/coordinate-reference-systems/SKILL.md` | Core |
| GIS data flow and provenance | `skills/gis-data-flow-diagnostics/SKILL.md` | Core |
| UI/UX design and tests | `skills/gis-ui-ux-design-testing/SKILL.md` | Tool UI |
| GIS native security | `skills/gis-security-guardian/SKILL.md` | Core |
| Scientific provider integrations | `skills/geospatial-api-integration/SKILL.md` | Optional |
| Satellite/STAC catalogs | `skills/geospatial-data-catalogs/SKILL.md` | Optional |
| GIS code reference discovery | `skills/gis-code-discovery/SKILL.md` | Optional |
| Cartographic layer symbology | `skills/gis-cartography-symbology/SKILL.md` | Map output |
| Additional agent coordination | `skills/geospatial-ai-agents/SKILL.md` | Agent design only |

**Mandatory read order on every new agent:** `AGENTS.md` -> `PROJECT_STATE.md` -> plan/report indexes & latest -> official specification -> this registry -> selected skill files and their references. `agent-development-journal` and `completion-evidence` are mandatory when available; if unavailable record the limitation in a numbered report.

## Safe setup
```bash
python tools/bootstrap_skills.py
# prints commit SHA and local location; does not run code from the cloned repository
python tools/bootstrap_skills.py --verify
```
If network or Git fails, do not claim skills installed. Clone must remain outside versioned source (`.agent_resources/` ignored), while the source URLs, selected skill paths, SHA and license review remain in reports for audit. Agents running in environments without automatic skills discovery should **read** `.agent_resources/GIS-Development-Skills/<relative SKILL.md>` directly, including `../../references` pages.

## Needed additions to YOUR skills repository (proposals, not automatically installed)
1. **Project Development Lifecycle Management**: import `PLAN_*.md` in root, stable plan IDs/revisions, active/blocked/completed archive, numbered reports and handoff. Integrate existing `agent-development-journal` and DoneProof, don't fork their canonical logs.
2. **Spectral Index Engineering**: original DOI/formula/variant verification, wavelength constraints, unit tests, QA/NoData and locale parity.
3. **Satellite Sensor Compatibility**: mission/product/level/date/band/metadata and instrument physics; ABI interfaces for discovery and method gating.
4. **Scientific Processing Reports & Provenance**: per-output formula, precise metadata key/value source, QA, raster readback, and multilingual report generation.
5. **GIS Raster Performance & Workspaces**: streaming processing, cache fingerprinting, atomic writes and non-destructive resuming.

Make skill contribution proposals under `documentation/skill_backport_proposals/`, with tested generic examples and MIT-compatible source. Only modify https://github.com/ahmadibrahim4geo/GIS-Development-Skills upon a separate explicit authorisation; ATIAF repo code does not automatically backport.

## Optional GENERAL software-engineering skill sources
- [AI Development Skills](https://github.com/VelimirMueller/ai-development-skills) — Claude Code-oriented engineering judgement; supplementary, not mission-critical. Do NOT bulk-install; review each plugin, platform suitability, and security.
- [Superpowers](https://github.com/obra/superpowers) — design/plan/test methodology reference; do not duplicate the accepted journal and completed-plan lifecycle.
- [OpenGeoS geoai-skills](https://github.com/opengeos/geoai-skills) — specialized ideas for geospatial AI; model/data licenses and runtime resources need separate checks.

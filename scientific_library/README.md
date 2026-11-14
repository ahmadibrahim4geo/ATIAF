# Scientific registry
- `sensors/sensor_registry.json` — source-linked *candidate* sensor/product and download knowledge. Real parser validation required before marking support.
- `indices/candidate_indices.json` — hand-picked index/method candidates; **not executable validated implementations**.
- `schemas/index.schema.json` — minimum shape for an index; independent scientific reference and test are mandatory.
- `catalog_upstream/` — intentionally empty initially. `python tools/sync_index_catalog.py` downloads an MIT catalog and its license into this directory on a development machine (network required). The agent must pin a commit and review license and schema before shipping it.
- `references/reference_registry.json` — stable source links and usage policies.

No bulk Index DataBase export is included or permitted under current API terms.

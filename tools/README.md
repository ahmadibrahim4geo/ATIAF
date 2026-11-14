# Developer utilities
- `python tools/validate_package.py` checks docs/JSON/internal links and explicit unimplemented status; it does **not** test GIS calculations.
- `python tools/bootstrap_skills.py` downloads the approved GIS-Development-Skills repo into `.agent_resources/GIS-Development-Skills` and verifies mandatory files + commit SHA. Does NOT execute remote scripts. On a disconnected machine it may fail, which must be documented.
- `python tools/bootstrap_skills.py --verify` verifies an existing installation locally, without network.
- `python tools/sync_index_catalog.py --commit FULL_40_HEX_SHA` optionally downloads an MIT index catalog + LICENSE on a developer host. The experimental v1 catalog is **unreviewed** and is NOT directly enabled for users; citation/license/formula/QA validation comes first. `--dry-run` to print URLs.

Both network operations are developer-only; final user tools must function from already-downloaded local imagery and approved packaged scientific definitions.

# Shared ATIAF engine

`atiaf_core` is the sole implementation package with I. Both hosts call `workflow.run_tool`; adapters are separate and thin. Old Y imports require migration to `atiaf_core`. Dependency-free `tool_contract.py` keeps choices visible when raster dependencies are missing. `data/` definitions ship in wheels and plugin ZIPs. [Current usage](../documentation/en/QUICK_START.md).

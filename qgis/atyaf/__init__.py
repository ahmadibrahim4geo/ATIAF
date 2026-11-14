# -*- coding: utf-8 -*-
"""ATIAF QGIS Processing Plugin entry point.

Author: ATIAF Open Source Geospatial Project
License: MIT
"""

import sys
from pathlib import Path

# Ensure project root is on sys.path for atyaf_core imports
PLUGIN_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = PLUGIN_DIR.parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))


def classFactory(iface):
    """Load ATIAFPlugin from atyaf_plugin."""
    from .atyaf_plugin import ATIAFPlugin
    return ATIAFPlugin(iface)

# -*- coding: utf-8 -*-
"""ATIAF Core — Advanced Thematic Imagery Analysis Framework (أطياف)
Pure-Python geospatial engine for satellite imagery analysis.
Canonical package: atiaf_core
"""

import sys
import atyaf_core
from atyaf_core import (
    discovery,
    raster,
    indices,
    temperature,
    urban,
    environment,
    geology,
    mosaic,
    temporal,
    modalities,
)

__version__ = "1.0.0"
__author__ = "ATIAF Development Team"
__license__ = "MIT"

# Register canonical submodules under atiaf_core
sys.modules["atiaf_core.discovery"] = discovery
sys.modules["atiaf_core.raster"] = raster
sys.modules["atiaf_core.indices"] = indices
sys.modules["atiaf_core.temperature"] = temperature
sys.modules["atiaf_core.urban"] = urban
sys.modules["atiaf_core.environment"] = environment
sys.modules["atiaf_core.geology"] = geology
sys.modules["atiaf_core.mosaic"] = mosaic
sys.modules["atiaf_core.temporal"] = temporal
sys.modules["atiaf_core.modalities"] = modalities

__all__ = [
    "discovery",
    "raster",
    "indices",
    "temperature",
    "urban",
    "environment",
    "geology",
    "mosaic",
    "temporal",
    "modalities",
]

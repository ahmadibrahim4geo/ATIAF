#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Independent installation verification script for ATIAF."""

import sys
from pathlib import Path

# Ensure project root is in sys.path
ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from atiaf_core.cli import run_diagnostics

if __name__ == "__main__":
    sys.exit(run_diagnostics(verbose=True))

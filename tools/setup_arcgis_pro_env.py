# -*- coding: utf-8 -*-
"""ATIAF — ArcGIS Pro Python Environment Setup & Dependency Installer
Locates the active ArcGIS Pro Python runtime and installs required scientific
dependencies (rasterio, shapely, pyproj) into user site-packages.
"""

from pathlib import Path
import subprocess
import sys


def find_arcgis_pro_python():
    """Finds the ArcGIS Pro python.exe path."""
    candidates = [
        Path(r"C:\Program Files\ArcGIS\Pro\bin\Python\envs\arcgispro-py3\python.exe"),
        Path(r"C:\Program Files\ArcGIS\Pro\bin\Python\scripts\propy.bat"),
        Path.home() / r"AppData\Local\ESRI\conda\envs\arcgispro-py3\python.exe",
    ]
    for c in candidates:
        if c.is_file():
            return c
    return None


def setup_env():
    print("=" * 70)
    print("  ATIAF — ArcGIS Pro Python Environment Configuration (أطياف)")
    print("=" * 70)

    pro_py = find_arcgis_pro_python()
    if not pro_py:
        print("[ERROR] Could not locate ArcGIS Pro Python installation.")
        print("Please ensure ArcGIS Pro is installed at standard location or run manually:")
        print("  <ArcGIS_Pro_Python> -m pip install --user rasterio shapely pyproj")
        return 1

    print(f"Found ArcGIS Pro Python: {pro_py}")
    print("Installing scientific dependencies into user site-packages...")

    packages = ["rasterio", "shapely", "pyproj"]
    cmd = [str(pro_py), "-m", "pip", "install", "--user"] + packages
    print(f"Executing: {' '.join(cmd)}")

    res = subprocess.run(cmd, capture_output=True, text=True)
    if res.returncode != 0:
        print("[WARNING] Pip installation encountered an issue:")
        print(res.stderr)
        return res.returncode

    print(res.stdout)

    # Verification
    verify_cmd = [str(pro_py), "-c", "import rasterio, shapely, pyproj; print('ALL REQUIRED PACKAGES VERIFIED!')"]
    ver = subprocess.run(verify_cmd, capture_output=True, text=True)
    if ver.returncode == 0:
        print("=" * 70)
        print("  SUCCESS: ArcGIS Pro environment is fully configured for ATIAF!")
        print("  تم تهيئة بيئة بايثون لـ ArcGIS Pro بنجاح وجاهزة لتشغيل أدوات أطياف.")
        print("=" * 70)
        return 0
    else:
        print("[ERROR] Verification failed:")
        print(ver.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(setup_env())

@echo off
title ATIAF - Setup ArcGIS Pro Python Environment
echo ======================================================================
echo   ATIAF (أطياف) - Configuring Python Environment for ArcGIS Pro
echo ======================================================================
echo.

set PRO_PY="C:\Program Files\ArcGIS\Pro\bin\Python\envs\arcgispro-py3\python.exe"

if not exist %PRO_PY% (
    echo [ERROR] Could not find ArcGIS Pro Python at %PRO_PY%
    echo Please locate python.exe inside your ArcGIS Pro conda directory.
    pause
    exit /b 1
)

echo Found ArcGIS Pro Python: %PRO_PY%
echo Installing rasterio, shapely, pyproj into user site-packages...
echo.

%PRO_PY% -m pip install --user rasterio shapely pyproj

echo.
echo Verifying installation...
%PRO_PY% -c "import rasterio, shapely, pyproj; print('>>> ALL DEPENDENCIES SUCCESSFULLY LOADED IN ARCGIS PRO! <<<')"

if %ERRORLEVEL% equ 0 (
    echo.
    echo ======================================================================
    echo   SUCCESS! ArcGIS Pro is now 100%% ready to run ATIAF.pyt!
    echo   تمت التهيئة بنجاح! يمكنك الآن فتح واستخدام صندوق أدوات أطياف في ArcGIS Pro.
    echo ======================================================================
) else (
    echo.
    echo [ERROR] Verification failed.
)

echo.
pause

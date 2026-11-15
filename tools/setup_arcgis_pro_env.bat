@echo off
if "%~1"=="" (
  echo Pass the path to propy.bat from your ArcGIS Pro installation as the first argument.
  echo This check does not install packages.
  exit /b 2
)
call "%~1" "%~dp0setup_arcgis_pro_env.py"
exit /b %ERRORLEVEL%

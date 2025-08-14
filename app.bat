@echo off
setlocal
cd /d %~dp0
set PYTHONPATH=%CD%

REM If packaged exe exists, run it
if exist "dist\parts_counter.exe" (
	start "" "dist\parts_counter.exe"
	exit /b 0
)

REM Fallback: run via Python launcher
set "PY=py"
where %PY% >NUL 2>&1
if errorlevel 1 set "PY=python"
%PY% run_app.py
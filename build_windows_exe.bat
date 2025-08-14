@echo off
setlocal
cd /d %~dp0

REM Detect Python launcher
set "PY=py"
%PY% -V >NUL 2>&1 || set "PY=python"

REM Ensure pip and dependencies
%PY% -m pip install --upgrade pip
%PY% -m pip install -r requirements.txt
%PY% -m pip install pyinstaller

REM Build one-file exe, include frontend assets (Windows uses semicolon in --add-data)
set "ADDDATA=frontend;frontend"
%PY% -m PyInstaller --noconfirm --onefile --name parts_counter --add-data "%ADDDATA%" run_app.py

echo.
echo Built: dist\parts_counter.exe
echo Double-click dist\parts_counter.exe to run the server on http://127.0.0.1:8000
pause
Param(
    [string]$Python = "py"
)

Set-Location -Path $PSScriptRoot

# Ensure pip and dependencies
& $Python -m pip install --upgrade pip
& $Python -m pip install -r requirements.txt
& $Python -m pip install pyinstaller

# Build one-file exe, include frontend assets (semicolon on Windows)
$addData = 'frontend;frontend'
& $Python -m PyInstaller --noconfirm --onefile --name parts_counter --add-data $addData run_app.py

Write-Host "Built: dist/parts_counter.exe"
Write-Host "Run dist/parts_counter.exe and open http://127.0.0.1:8000"
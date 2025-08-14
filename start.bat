@echo off
setlocal
set PYTHONPATH=%CD%
python -m uvicorn backend.app:app --host 0.0.0.0 --port 8000
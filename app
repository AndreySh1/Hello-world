#!/usr/bin/env bash
set -e
cd "$(dirname "$0")"
export PYTHONPATH=$(pwd)
: "${HOST:=0.0.0.0}"
: "${PORT:=8000}"
if [ -x "./dist/parts_app" ]; then
	./dist/parts_app
else
	python3 run_app.py
fi
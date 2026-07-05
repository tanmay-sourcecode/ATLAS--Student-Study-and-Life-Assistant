#!/bin/bash
# Always runs Atlas with the project's Python 3.11 venv (never the system 3.9).
# Usage:  ./run.sh
cd "$(dirname "$0")"

if [ ! -x ".venv/bin/python" ]; then
  echo "No .venv found. Create it first:"
  echo "  ~/.pyenv/versions/3.11.9/bin/python -m venv .venv"
  echo "  .venv/bin/python -m pip install -r requirements.txt"
  exit 1
fi

echo "Using: $(.venv/bin/python --version)"
.venv/bin/python app.py

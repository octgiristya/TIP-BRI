#!/bin/bash
source .venv/bin/activate

echo "Installing requirements (Normal Setup)..."
pip install -r requirements.txt

echo "Requirements installed. Running import..."
python scripts/initial_import.py

echo "Starting Uvicorn..."
python -m uvicorn app.main:app --reload --host 127.0.0.1 --port 8000

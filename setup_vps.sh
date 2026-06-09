#!/bin/bash
# Run this once on your VPS to set everything up
set -e

echo "=== Installing system dependencies ==="
sudo apt-get update -y
sudo apt-get install -y python3 python3-pip python3-venv

echo "=== Creating virtual environment ==="
python3 -m venv venv
source venv/bin/activate

echo "=== Installing Python packages ==="
pip install -r requirements.txt

echo "=== Installing Playwright browsers ==="
playwright install chromium
playwright install-deps chromium

echo "=== Setup complete! ==="
echo ""
echo "To run the app:"
echo "  source venv/bin/activate"
echo "  uvicorn main:app --host 0.0.0.0 --port 8000"

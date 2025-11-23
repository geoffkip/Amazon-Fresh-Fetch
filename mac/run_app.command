#!/bin/bash
cd "$(dirname "$0")/.."
echo "Installing dependencies..."
pip install -r requirements.txt
playwright install
echo "Starting Fresh Fetch..."
streamlit run amazon_fresh_fetch.py

@echo off
cd /d "%~dp0"
cd ..
echo Installing dependencies...
pip install -r requirements.txt
playwright install
echo Starting Fresh Fetch...
streamlit run amazon_fresh_fetch.py
pause

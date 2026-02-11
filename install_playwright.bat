@echo off
echo Installing Playwright and Chromium...
cd backend
call venv\Scripts\activate
pip install playwright
python -m playwright install chromium
echo Playwright installation complete!
pause

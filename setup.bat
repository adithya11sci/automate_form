@echo off
echo Setting up AutoFill-GForm Pro...

cd backend
python -m venv venv
call venv\Scripts\activate

echo Installing dependencies...
pip install -r requirements.txt

echo Installing Playwright browsers...
playwright install chromium

echo Setup Complete! Run launch.bat to start.
pause

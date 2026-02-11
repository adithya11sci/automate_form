@echo off
echo Starting AutoFill-GForm Pro Manual Setup...

cd backend
python -m venv venv
call venv\Scripts\activate

echo Installing Core Dependencies...
pip install fastapi uvicorn[standard] sqlalchemy python-jose[cryptography] passlib[bcrypt] python-multipart pydantic pydantic-settings python-dotenv

echo Installing AI Dependencies (This may take a while)...
pip install sentence-transformers scikit-learn numpy aiofiles httpx

echo Installing Playwright...
pip install playwright
playwright install chromium

echo Setup Complete! Run verify_setup.py to check installation.
pause

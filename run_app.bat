@echo off
echo ==========================================
echo 🚀 AutoFill-GForm Pro - Launcher
echo ==========================================
echo.

cd backend
call venv\Scripts\activate

echo ⚡ Starting Server...
echo ------------------------------------------
echo Local URL: http://localhost:8000
echo ------------------------------------------
echo Press Ctrl+C to stop.
echo.

uvicorn app.main:app --reload --port 8000
pause

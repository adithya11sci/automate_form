@echo off
echo Starting AutoFill-GForm Pro...
cd backend
call venv\Scripts\activate
start http://localhost:8000
uvicorn app.main:app --reload --port 8000
pause

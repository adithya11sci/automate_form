@echo off
echo Starting AutoFill-GForm Pro on Port 5000...
cd backend
call venv\Scripts\activate
# Start browser at port 5000
start http://localhost:5000
uvicorn app.main:app --reload --port 5000
pause

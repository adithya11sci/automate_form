@echo off
echo.
echo ==================================================
echo   🔧 Fixing SQLite DLL for Conda Environments
echo ==================================================
echo.

set VENV_PATH=backend\venv
set CONDA_BASE=C:\Users\adith\miniconda3

if not exist "%CONDA_BASE%\Library\bin\sqlite3.dll" (
    echo ❌ Could not find sqlite3.dll in %CONDA_BASE%
    echo Please check your Miniconda installation path.
    pause
    exit /b
)

echo Found sqlite3.dll at %CONDA_BASE%
echo Copying to venv...

copy "%CONDA_BASE%\Library\bin\sqlite3.dll" "%VENV_PATH%\Scripts\" /Y
copy "%CONDA_BASE%\Library\bin\sqlite3.dll" "%VENV_PATH%\DLLs\" /Y

echo.
echo ✅ Fix applied! Try running launch.bat again.
echo ==================================================
pause

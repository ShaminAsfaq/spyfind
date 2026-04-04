@echo off
SET DIR=%~dp0
cd /d "%DIR%"

echo [INFO] Starting Spyfind Dual-Server Architecture...

IF EXIST ".venv\Scripts\activate.bat" (
    SET VENV_ACTIVATE=.venv\Scripts\activate.bat
) ELSE IF EXIST "venv\Scripts\activate.bat" (
    SET VENV_ACTIVATE=venv\Scripts\activate.bat
) ELSE (
    echo [ERROR] Virtual environment not found. Please create one first.
    exit /b 1
)

echo [INFO] Starting Backend (Port 8000)...
start "Spyfind Backend" cmd /k "call %VENV_ACTIVATE% && uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload"

echo [INFO] Starting Frontend (Port 3000)...
start "Spyfind Frontend" cmd /k "call %VENV_ACTIVATE% && uvicorn frontend.main:app --host 0.0.0.0 --port 3000 --reload"

echo [SUCCESS] Both servers are starting in separate windows.
echo - Backend: http://localhost:8000/docs
echo - Frontend: http://localhost:3000/
pause

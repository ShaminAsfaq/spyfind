@echo off
SET DIR=%~dp0
cd /d "%DIR%"

IF EXIST ".venv\Scripts\activate.bat" (
    CALL .venv\Scripts\activate.bat
) ELSE IF EXIST "venv\Scripts\activate.bat" (
    CALL venv\Scripts\activate.bat
) ELSE (
    echo Virtual environment not found. Please create one first.
    exit /b 1
)

python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload

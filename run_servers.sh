#!/bin/bash

# Spyfind Dual-Server Runner (Linux/macOS)

echo "[INFO] Starting Spyfind Dual-Server Architecture..."

if [ -f ".venv/bin/activate" ]; then
    VENV_ACTIVATE=".venv/bin/activate"
elif [ -f "venv/bin/activate" ]; then
    VENV_ACTIVATE="venv/bin/activate"
else
    echo "[ERROR] Virtual environment not found."
    exit 1
fi

source "$VENV_ACTIVATE"

# Run Backend in background
echo "[INFO] Starting Backend (Port 8000)..."
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload &
BACKEND_PID=$!

# Run Frontend
echo "[INFO] Starting Frontend (Port 3000)..."
uvicorn frontend.main:app --host 0.0.0.0 --port 3000 --reload

# When frontend stops, kill backend
kill $BACKEND_PID

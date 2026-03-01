@echo off
title Stock Market Automation Launcher

echo ===================================================
echo   Stock Market Automation - One-Click Launcher
echo ===================================================
echo.

:: 1. Install Python Dependencies
echo [1/4] Installing Python dependencies...
pip install -r requirements.txt
if %errorlevel% neq 0 (
    echo Error installing requirements. Check Python installation.
    pause
    exit /b
)

:: 2. Seed Database
echo.
echo [2/4] Seeding database with dummy data...
python seed_db.py

:: 3. Start Backend
echo.
echo [3/4] Starting Backend Server (API)...
start "Backend API (Do Not Close)" cmd /k "python -m uvicorn backend.main:app --host 0.0.0.0 --port 8000 --reload"

:: 4. Start Frontend
echo.
echo [4/4] Starting Frontend Dashboard...
cd frontend
call npm install
start "Frontend Dashboard (Do Not Close)" cmd /k "npm run dev"

echo.
echo ===================================================
echo   SUCCESS! 
echo   1. Backend is running on http://localhost:8000
echo   2. Frontend will open at http://localhost:5173
echo ===================================================
pause

@echo off
TITLE AI SOC - LAUNCHER
color 0A

:: 1. Database Setup
echo [1/5] Checking Database...
python backend/db_setup.py

:: 2. Log Generator
echo [2/5] Launching Traffic Generator...
start "1. LOG GENERATOR" cmd /k "color 0E && python agents/log_generator.py"

:: 3. Detective
echo [3/5] Launching Detection Engine...
start "2. DETECTIVE" cmd /k "color 0B && python backend/detection.py"

:: 4. AI Worker
echo [4/5] Launching AI Analyst...
start "3. AI WORKER" cmd /k "color 0D && python backend/ai_worker.py"

:: 5. Dashboard
echo [5/5] Launching Dashboard...
:: Note: Streamlit needs to know where the file is
start "4. DASHBOARD" cmd /k "color 0F && streamlit run dashboard/dashboard.py"

echo.
echo    ✅ SYSTEM ONLINE.
pause
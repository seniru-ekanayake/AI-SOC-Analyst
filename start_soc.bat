@echo off
TITLE AI SOC - LAUNCHER
color 0A
echo ========================================================
echo       🛡️  STARTING AI SECURITY OPERATIONS CENTER
echo ========================================================
echo.

:: 1. Database Setup 
echo [1/5] Checking Database...
python db_setup.py

:: 2. Start the Log Generator 
echo [2/5] Launching Traffic Generator...
start "1. LOG GENERATOR (Traffic)" cmd /k "color 0E && python log_generator.py"

:: 3. Start the Detection Tool
echo [3/5] Launching Detection Engine...
start "2. DETECTIVE (Triage)" cmd /k "color 0B && python detection.py"

:: 4. Start the AI Worker 
echo [4/5] Launching AI Analyst...
start "3. AI WORKER (Gemini)" cmd /k "color 0D && python ai_worker.py"

:: 5. Start the Dashboard 
echo [5/5] Launching Executive Dashboard...
start "4. DASHBOARD" cmd /k "color 0F && streamlit run dashboard.py"

echo.
echo ========================================================
echo    ✅ SYSTEM ONLINE. MINIMIZE THIS WINDOW, DON'T CLOSE IT.
echo ========================================================
pause
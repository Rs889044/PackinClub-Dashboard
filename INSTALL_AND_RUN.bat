@echo off
title PackinClub Dashboard - First Time Setup
color 0A

echo ============================================
echo   PackinClub Dashboard - First Time Setup
echo ============================================
echo.

:: Check if Python is installed
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [!] Python is NOT installed on this computer.
    echo.
    echo Please follow these steps:
    echo   1. Go to https://www.python.org/downloads/
    echo   2. Click "Download Python 3.12" (or latest)
    echo   3. IMPORTANT: Check the box "Add Python to PATH" at the bottom!
    echo   4. Click "Install Now"
    echo   5. After installation, close this window and double-click this file again.
    echo.
    echo Opening Python download page for you...
    start https://www.python.org/downloads/
    pause
    exit /b
)

echo [OK] Python found!
python --version
echo.

:: Install required packages
echo [*] Installing required packages (one-time setup)...
echo     This may take 1-2 minutes...
echo.
pip install streamlit pandas fpdf2 openpyxl Pillow --quiet
if %errorlevel% neq 0 (
    echo [!] Error installing packages. Trying with --user flag...
    pip install streamlit pandas fpdf2 openpyxl Pillow --user --quiet
)

echo.
echo [OK] All packages installed!
echo.

:: Create the launcher shortcut for future use
echo [*] Setup complete! Launching the dashboard...
echo.
echo ============================================
echo   TIP: Next time, just double-click
echo   "START_Dashboard.bat" to launch directly!
echo ============================================
echo.

:: Launch the app
cd /d "%~dp0"
start http://localhost:8501
streamlit run app.py --server.headless true

pause

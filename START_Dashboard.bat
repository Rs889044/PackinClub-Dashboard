@echo off
title PackinClub Dashboard
color 0A

echo ========================================
echo   PackinClub Dashboard - Starting...
echo ========================================
echo.
echo   Your browser will open automatically.
echo   Keep this window OPEN while using the app.
echo   To stop, close this window or press Ctrl+C.
echo.
echo ========================================

cd /d "%~dp0"
start http://localhost:8501
streamlit run app.py --server.headless true

pause

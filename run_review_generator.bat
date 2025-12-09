@echo off
echo ============================================
echo   Starting AI Review Generator
echo ============================================
echo.

REM Activate virtual environment
call venv\Scripts\activate.bat

REM Run the Python script
python review_generator.py

REM Keep the window open if there's an error
if errorlevel 1 pause

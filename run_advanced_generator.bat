@echo off
echo ============================================
echo   Advanced AI Review Generator
echo   Powered by Sarvam AI
echo ============================================
echo.

REM Activate virtual environment
call venv\Scripts\activate.bat

REM Run the advanced Python script
python advanced_review_generator.py

REM Keep the window open if there's an error
if errorlevel 1 pause

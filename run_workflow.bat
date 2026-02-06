@echo off
REM ========================================
REM  Gold Price Automation Workflow
REM ========================================

echo.
echo ========================================
echo   GOLD PRICE AUTOMATION WORKFLOW
echo ========================================
echo.

REM Change to project directory
cd /d "%~dp0"

REM Run the main workflow
where py >nul 2>nul && (
    py -u main_workflow.py
) || (
    python -u main_workflow.py
)

REM Check exit code
if errorlevel 1 (
    echo.
    echo ========================================
    echo   WORKFLOW FAILED (Exit Code: %errorlevel%)
    echo ========================================
    pause
    exit /b %errorlevel%
) else (
    echo.
    echo ========================================
    echo   WORKFLOW COMPLETED SUCCESSFULLY
    echo ========================================
)

REM Optional: Uncomment to keep window open
REM pause

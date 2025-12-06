@echo off
REM Run C:\py\pygold\app.py with Python

REM Change to the app’s folder (so relative paths work)
pushd "C:\py\pygold"

REM Use the Python launcher (preferred). Falls back to python if needed.
where py >nul 2>nul && (
    py -u app.py
) || (
    python -u app.py
)

REM Keep window open if there’s an error
if errorlevel 1 (
    echo.
    echo === The script exited with an error (code %errorlevel%). ===
    pause
)

popd

@echo off
REM --- Step 1 ---
where py >nul 2>nul && (
    py -u "C:\py\pygold\app.py"
) || (
    python -u "C:\py\pygold\app.py"
)
IF ERRORLEVEL 1 (
    echo.
    echo ✗ ขั้นตอนที่ 1 ล้มเหลว (exit code %ERRORLEVEL%)
    pause
    exit /b %ERRORLEVEL%
)

echo.
echo ✓ ขั้นตอนที่ 1 สำเร็จ — ไปขั้นตอนที่ 2

REM --- Step 2 ---
where py >nul 2>nul && (
    py -u "E:\gold_vertical_panel\app.py"
) || (
    python -u "E:\gold_vertical_panel\app.py"
)

SET "EC=%ERRORLEVEL%"
echo.
IF "%EC%"=="0" (
    echo ✓ ทั้งหมดสำเร็จ
) ELSE (
    echo ✗ ขั้นตอนที่ 2 ล้มเหลว (exit code %EC%)
)
pause
exit /b %EC%

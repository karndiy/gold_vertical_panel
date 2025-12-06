@echo off
setlocal EnableExtensions

REM เลือกตัวรัน Python
where py >nul 2>nul
if %errorlevel%==0 ( set "PYRUN=py -u" ) else ( set "PYRUN=python -u" )

REM --- Step 1 ---
echo( | %PYRUN% "E:\gold_vertical_panel\getgold.py"
if errorlevel 1 (
  echo ✗ ขั้นตอนที่ 1 ล้มเหลว (exit code %errorlevel%)
  pause & endlocal & exit /b %errorlevel%
)

echo ✓ ขั้นตอนที่ 1 สำเร็จ — ไปขั้นตอนที่ 2

REM --- Step 2: เปลี่ยนโฟลเดอร์ให้ path assets ทำงานได้ ---
pushd "E:\gold_vertical_panel"
%PYRUN% app.py
set "EC=%ERRORLEVEL%"
popd

echo(
if "%EC%"=="0" ( echo ✓ ทั้งหมดสำเร็จ ) else ( echo ✗ ขั้นตอนที่ 2 ล้มเหลว (exit code %EC%) )
pause
endlocal & exit /b %EC%


@echo off
setlocal EnableExtensions

where py >nul 2>nul
if %errorlevel%==0 ( set "PYRUN=py -u" ) else ( set "PYRUN=python -u" )

REM --- Step 1: getgold.py (auto-send Enter ถ้าโค้ดตัวอื่นยัง pause) ---
pushd "E:\gold_vertical_panel"
echo( | %PYRUN% getgold.py
set "EC=%ERRORLEVEL%"
popd
if not "%EC%"=="0" (
  echo ✗ Step 1 failed (exit %EC%)
  pause & endlocal & exit /b %EC%
)

echo ✓ Step 1 OK → Step 2

REM --- Step 2: gold_vertical_panel ---
pushd "E:\gold_vertical_panel"
%PYRUN% app.py
set "EC=%ERRORLEVEL%"
popd

if "%EC%"=="0" ( echo ✓ All done ) else ( echo ✗ Step 2 failed (exit %EC%) )
pause
endlocal & exit /b %EC%


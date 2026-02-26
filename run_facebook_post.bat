@echo off
REM =====================================================
REM Facebook Post Generator - Quick Run
REM สร้างโพสต์ Facebook สำหรับราคาทองคำ
REM =====================================================

echo ========================================
echo  Facebook Post Generator
echo ========================================
echo.

cd /d %~dp0

echo [1/2] กำลังสร้างโพสต์ข้อความ...
python facebook_post.py

echo.
echo [2/2] กำลังสร้างรูปภาพโพสต์...
python facebook_image_post.py

echo.
echo ========================================
echo  เสร็จสิ้น!
echo ========================================
echo.
echo ไฟล์ที่สร้าง:
echo - out\facebook_post_*.txt
echo - out\facebook_gold_*.jpg
echo.

pause

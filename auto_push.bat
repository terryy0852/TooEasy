@echo off
echo ================================
echo  Automatic GitHub Push Script
echo ================================
echo.

python auto_push.py

if %errorlevel% equ 0 (
    echo.
    echo ✅ Automatic push completed successfully!
    echo.
) else (
    echo.
    echo ❌ Automatic push failed!
    echo.
)

pause
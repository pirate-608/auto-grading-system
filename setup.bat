@echo off
chcp 65001 > nul
setlocal

echo ==========================================
echo      Auto Grading System - Quick Setup
echo ==========================================

:: 1. Check Python
python --version > nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Python not found! Please install Python 3.8+ and add it to PATH.
    pause
    exit /b 1
)
echo [OK] Python found.

:: 2. Build C Project
echo.
echo [1/4] Building C Core...
make --version > nul 2>&1
if %errorlevel% neq 0 (
    echo [WARNING] 'make' command not found.
    echo Please ensure MinGW/GCC is installed and 'make' is in PATH.
    echo If you have already built the project manually, you can continue.
    echo.
    set /p continue_build="Continue without make? (Y/N): "
    if /i "%continue_build%" neq "Y" exit /b 1
) else (
    make
    if %errorlevel% neq 0 (
        echo [ERROR] Build failed.
        pause
        exit /b 1
    )
    echo [OK] Build successful.
)

:: 3. Setup Virtual Environment
echo.
echo [2/4] Setting up Python Virtual Environment...
if not exist .venv (
    echo Creating .venv...
    python -m venv .venv
) else (
    echo .venv already exists.
)

:: 4. Install Dependencies
echo.
echo [3/4] Installing Dependencies...
call .venv\Scripts\activate
pip install -r web/requirements.txt
if %errorlevel% neq 0 (
    echo [ERROR] Failed to install dependencies.
    pause
    exit /b 1
)
echo [OK] Dependencies installed.

:: 5. Menu
:menu
cls
echo ==========================================
echo      Auto Grading System - Launcher
echo ==========================================
echo 1. Run Web Interface (Browser)
echo 2. Run CLI Mode (Command Line)
echo 3. Rebuild C Core
echo 4. Exit
echo ==========================================
set /p choice="Please select (1-4): "

if "%choice%"=="1" goto run_web
if "%choice%"=="2" goto run_cli
if "%choice%"=="3" goto rebuild
if "%choice%"=="4" goto end

goto menu

:run_web
echo.
echo Starting Web Server...
echo Press Ctrl+C to stop.
python web/app.py
pause
goto menu

:run_cli
echo.
echo Starting CLI...
if not exist build\auto_grader.exe (
    echo [ERROR] Executable not found. Please build first.
    pause
    goto menu
)
build\auto_grader.exe
pause
goto menu

:rebuild
echo.
echo Rebuilding...
make clean
make
pause
goto menu

:end
endlocal

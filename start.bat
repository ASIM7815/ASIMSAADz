@echo off
echo ============================================================
echo  Codebase and Repository Explorer Agent
echo  Starting both Node.js backend and Python frontend...
echo ============================================================
echo.

REM Check if Node.js is installed
where node >nul 2>nul
if %errorlevel% neq 0 (
    echo ERROR: Node.js is not installed!
    echo Please install Node.js from https://nodejs.org/
    pause
    exit /b 1
)

REM Check if Python is installed
where python >nul 2>nul
if %errorlevel% neq 0 (
    echo ERROR: Python is not installed!
    echo Please install Python from https://www.python.org/
    pause
    exit /b 1
)

REM Check if .env file exists
if not exist .env (
    echo WARNING: .env file not found!
    echo Please copy .env.example to .env and configure it.
    echo.
    echo Press Ctrl+C to exit and configure .env
    echo or press any key to continue anyway...
    pause
)

REM Check if node_modules exists
if not exist node_modules (
    echo Installing Node.js dependencies...
    call npm install
    if %errorlevel% neq 0 (
        echo ERROR: Failed to install dependencies!
        pause
        exit /b 1
    )
)

echo.
echo Starting services...
echo.
echo [1/2] Starting Node.js backend on port 3001...
start "Node.js Backend" cmd /k "node server.js"
timeout /t 3 /nobreak >nul

echo [2/2] Starting Python frontend on port 5000...
start "Python Frontend" cmd /k "python app.py"
timeout /t 2 /nobreak >nul

echo.
echo ============================================================
echo  Both servers are starting!
echo ============================================================
echo.
echo  Backend:  http://localhost:3001
echo  Frontend: http://localhost:5000
echo.
echo  Opening browser in 5 seconds...
echo ============================================================

timeout /t 5 /nobreak >nul
start http://localhost:5000

echo.
echo Press any key to stop all servers and exit...
pause >nul

echo.
echo Stopping servers...
taskkill /FI "WINDOWTITLE eq Node.js Backend*" /F >nul 2>nul
taskkill /FI "WINDOWTITLE eq Python Frontend*" /F >nul 2>nul

echo Done!
exit /b 0

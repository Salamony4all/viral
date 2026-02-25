@echo off
REM Start the entire Viral Engine stack on Windows

echo.
echo ╔════════════════════════════════════════╗
echo ║   VIRAL ENGINE - STARTUP SEQUENCE      ║
echo ╚════════════════════════════════════════╝
echo.

REM Check if Ollama is running
echo [1/3] Checking Ollama...
curl -s http://localhost:11434/api/tags > nul 2>&1
if errorlevel 1 (
    echo ⚠️  Ollama is not running!
    echo Run this in a separate terminal:
    echo   ollama serve
    echo.
    pause
)

REM Start the backend API
echo [2/3] Starting Backend API...
start "Viral Engine API" cmd /k python api.py
echo ✅ Backend started on http://localhost:8000

REM Install frontend dependencies if needed
echo [3/3] Starting Frontend...
cd frontend
if not exist node_modules (
    echo Installing dependencies...
    call npm install
)

echo ✅ Frontend starting on http://localhost:3000
call npm run dev

echo.
echo ╔════════════════════════════════════════╗
echo ║       🚀 VIRAL ENGINE IS LIVE! 🚀      ║
echo ║   Open: http://localhost:3000          ║
echo ╚════════════════════════════════════════╝
echo.

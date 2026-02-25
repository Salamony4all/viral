@echo off
REM Start all Viral Engine services (Backend + Frontend)
REM Run from anywhere: double-click or "start_all.bat" from viral_engine folder

setlocal enabledelayedexpansion
cd /d "%~dp0"

echo.
echo ╔════════════════════════════════════════════════════════════════╗
echo ║           STARTING VIRAL ENGINE - ALL SERVICES                ║
echo ╚════════════════════════════════════════════════════════════════╝
echo.

REM Use .venv if present, else system python
set BACKEND_DIR=%~dp0
set FRONTEND_DIR=%~dp0frontend
if exist "%~dp0..\.venv\Scripts\python.exe" (
    set PYTHON=%~dp0..\.venv\Scripts\python.exe
) else (
    set PYTHON=python
)

echo [1/2] Starting Backend API (FastAPI)...
echo        http://localhost:8000
start "Viral Engine Backend" cmd /k "cd /d %BACKEND_DIR% && %PYTHON% api.py"

echo.
echo [2/2] Starting Frontend (React + Vite)...
echo        http://localhost:3001
start "Viral Engine Frontend" cmd /k "cd /d %FRONTEND_DIR% && (if not exist node_modules npm install) && npm run dev"

echo.
echo ╔════════════════════════════════════════════════════════════════╗
echo ║  ✅ ALL SERVICES STARTING IN NEW WINDOWS                      ║
echo ║                                                                 ║
echo ║  Backend:  http://localhost:8000                              ║
echo ║  Frontend: http://localhost:3001  ^<- OPEN THIS                ║
echo ║                                                                 ║
echo ║  Close the 2 terminal windows to stop the servers.             ║
echo ╚════════════════════════════════════════════════════════════════╝
echo.

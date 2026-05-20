@echo off
REM One-click local launcher for Arcade Hub (Windows)
setlocal
set ROOT=%~dp0

echo ==^> Setting up backend...
cd /d "%ROOT%arcade-backend"
if not exist venv ( python -m venv venv )
call venv\Scripts\activate.bat
python -m pip install --upgrade pip >nul
pip install -r requirements.txt
if not exist .env copy .env.example .env >nul

echo ==^> Starting backend on http://localhost:8000 ...
start "Arcade Hub API" cmd /k "cd /d %ROOT%arcade-backend && call venv\Scripts\activate.bat && uvicorn main:app --host 0.0.0.0 --port 8000"

cd /d "%ROOT%arcade-frontend"
echo ==^> Setting up frontend...
if not exist node_modules ( call npm install )
if not exist .env ( echo VITE_API_URL=http://localhost:8000 > .env )

echo.
echo =================================================
echo  Arcade Hub is starting!
echo    Backend  : http://localhost:8000  (docs: /docs)
echo    Frontend : http://localhost:5173
echo    Admin    : admin@gmail.com / admin123
echo =================================================
echo.
call npm run dev -- --host 0.0.0.0 --port 5173
endlocal

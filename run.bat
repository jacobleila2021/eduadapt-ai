@echo off
title Alora AI
cd /d "%~dp0"

echo.
echo  ========================================
echo   Alora AI - Starting...
echo  ========================================
echo.

REM Find Python (python or py launcher)
set "PYTHON_CMD="
where python >nul 2>&1
if %errorlevel% equ 0 (
    set "PYTHON_CMD=python"
) else (
    where py >nul 2>&1
    if %errorlevel% equ 0 (
        set "PYTHON_CMD=py -3"
    )
)

if "%PYTHON_CMD%"=="" (
    echo ERROR: Python not found.
    echo Install Python 3.10+ from https://www.python.org/downloads/
    echo Check "Add python.exe to PATH" during setup, then run this file again.
    pause
    exit /b 1
)

REM Virtual environment (keeps dependencies isolated)
if not exist ".venv\Scripts\python.exe" (
    echo Creating virtual environment...
    %PYTHON_CMD% -m venv .venv
    if %errorlevel% neq 0 (
        echo ERROR: Could not create virtual environment.
        pause
        exit /b 1
    )
)

set "VENV_PY=.venv\Scripts\python.exe"
set "VENV_PIP=.venv\Scripts\pip.exe"

echo Installing dependencies...
"%VENV_PIP%" install -r requirements.txt -q
if %errorlevel% neq 0 (
    echo ERROR: pip install failed.
    pause
    exit /b 1
)

if not exist "samples\sample_lesson.docx" (
    echo Creating sample lesson file...
    "%VENV_PY%" create_sample_lesson.py
)

if not exist ".env" (
    echo.
    echo NOTE: Copy .env.example to .env and add your OPENAI_API_KEY
    echo       Generation will not work until the key is set.
    echo.
)

if not exist "%USERPROFILE%\.streamlit" (
    mkdir "%USERPROFILE%\.streamlit"
)
(
    echo [general]
    echo email = ""
) > "%USERPROFILE%\.streamlit\credentials.toml"

REM Pick a free port if 8501 is already in use
set "PORT=8501"
netstat -ano | findstr ":%PORT% " | findstr "LISTENING" >nul 2>&1
if %errorlevel% equ 0 (
    echo Port 8501 is busy — using 8502 instead.
    set "PORT=8502"
)

set "APP_URL=http://127.0.0.1:%PORT%"

echo.
echo ========================================
echo   Alora AI — local URL (HTTP only):
echo   %APP_URL%
echo ========================================
echo.
echo IMPORTANT: Use http:// NOT https://
echo If you see "connection is not secure" or ERR_SSL_PROTOCOL_ERROR,
echo your browser tried HTTPS by mistake. Paste the URL above manually.
echo.
echo Keep this window open. Press Ctrl+C to stop.
echo.

set "STREAMLIT_BROWSER_GATHER_USAGE_STATS=false"

REM Open browser with plain HTTP once the server responds
start "" powershell -NoProfile -WindowStyle Hidden -Command ^
  "$url='%APP_URL%'; for ($i=0; $i -lt 60; $i++) { try { Invoke-WebRequest -Uri $url -UseBasicParsing -TimeoutSec 2 | Out-Null; Start-Process $url; exit 0 } catch { Start-Sleep -Seconds 1 } }"

".venv\Scripts\streamlit.exe" run app.py --server.port %PORT% --server.address 127.0.0.1 --server.headless true --browser.gatherUsageStats false --browser.serverAddress 127.0.0.1

if %errorlevel% neq 0 (
    echo.
    echo ERROR: Alora AI could not start. See the message above.
    pause
    exit /b 1
)

pause

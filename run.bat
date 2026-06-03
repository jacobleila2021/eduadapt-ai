@echo off
REM EduAdapt AI — one-click launcher for Windows
cd /d "%~dp0"

echo.
echo  ========================================
echo   EduAdapt AI - Starting...
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
        set "PYTHON_CMD=py"
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

REM Sample lesson for testing uploadsc
if not exist "samples\sample_lesson.docx" (
    echo Creating sample lesson file...
    "%VENV_PY%" create_sample_lesson.py
)

REM Remind about API key
if not exist ".env" (
    echo.
    echo NOTE: Copy .env.example to .env and add your OPENAI_API_KEY
    echo       Generation will not work until the key is set.
    echo.
)

echo Opening EduAdapt AI in your browser...
echo Press Ctrl+C in this window to stop the app.
echo.

REM Prevent first-run interactive Streamlit email prompt
if not exist "%USERPROFILE%\.streamlit" (
    mkdir "%USERPROFILE%\.streamlit"
)
(
    echo [general]
    echo email = ""
) > "%USERPROFILE%\.streamlit\credentials.toml"

set "STREAMLIT_BROWSER_GATHER_USAGE_STATS=false"
".venv\Scripts\streamlit.exe" run app.py --browser.gatherUsageStats false

pause

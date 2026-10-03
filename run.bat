@echo off
setlocal
cd /d "%~dp0"

set "PYTHON=python"
set "VENV_PYTHON=.venv\Scripts\python.exe"
set "INSTALL_DEPS=0"

where python >nul 2>&1
if errorlevel 1 (
    echo Python 3.10 or newer is required. Install Python from https://www.python.org/downloads/
    pause
    exit /b 1
)

if not exist "%VENV_PYTHON%" (
    echo Creating local virtual environment...
    %PYTHON% -m venv .venv
    if errorlevel 1 (
        echo Could not create the virtual environment.
        pause
        exit /b 1
    )
    set "INSTALL_DEPS=1"
)

if not exist ".venv\.requirements-installed" (
    set "INSTALL_DEPS=1"
)

if "%INSTALL_DEPS%"=="1" (
    echo Installing project dependencies for the first run...
    "%VENV_PYTHON%" -m pip install -r requirements.txt
    if errorlevel 1 (
        echo Dependency installation failed.
        pause
        exit /b 1
    )
    type nul > ".venv\.requirements-installed"
) else (
    echo Dependencies already installed. Starting directly...
)

echo Opening dashboard at http://localhost:8501
start "" "http://localhost:8501"

echo Launching Scholarship Verification Dashboard...
"%VENV_PYTHON%" -m streamlit run app.py --server.port 8501

if errorlevel 1 (
    echo.
    echo ERROR: The Streamlit dashboard could not be started.
    echo Check that Python, Streamlit, and the project dependencies are installed.
    pause
) else (
    echo.
    echo The dashboard has stopped.
    pause
)
endlocal

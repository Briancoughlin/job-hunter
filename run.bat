@echo off
setlocal enableextensions disabledelayedexpansion

:: Launch Job Hunter locally — do not modify without review (CI enforces hash check)
set "APP_DIR=%~dp0"
set "APP_FILE=%APP_DIR%app.py"

if not exist "%APP_FILE%" (
    echo ERROR: app.py not found in %APP_DIR%
    pause
    exit /b 1
)

start "" "msedge" --app="http://localhost:8501" --new-window
python -m streamlit run "%APP_FILE%" --server.headless true

endlocal

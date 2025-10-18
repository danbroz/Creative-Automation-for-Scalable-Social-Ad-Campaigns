@echo off
REM Creative Automation Pipeline Runner (Windows)
REM Convenience script for running the pipeline on Windows

echo ================================
echo Creative Automation Pipeline
echo ================================
echo.

REM Check if virtual environment exists
if not exist "venv\" (
    echo Virtual environment not found. Creating...
    python -m venv venv
    echo Virtual environment created
)

REM Activate virtual environment
echo Activating virtual environment...
call venv\Scripts\activate.bat

REM Check if dependencies are installed
python -c "import openai" 2>nul
if errorlevel 1 (
    echo Dependencies not found. Installing...
    pip install -q -r requirements.txt
    echo Dependencies installed
)

REM Check if brief file is provided
if "%~1"=="" (
    echo Usage: run.bat ^<brief_file.json^> [--verbose]
    echo.
    echo Examples:
    echo   run.bat examples\campaign_brief_1.json
    echo   run.bat examples\campaign_brief_2.json --verbose
    echo.
    echo Available examples:
    echo   - examples\campaign_brief_1.json (Wellness products^)
    echo   - examples\campaign_brief_2.json (Tech accessories^)
    echo   - examples\campaign_brief_3.json (Holiday gifts^)
    exit /b 1
)

REM Run the pipeline
echo.
echo Running pipeline...
echo.
python -m src.main %*

REM Check exit code
if %errorlevel% equ 0 (
    echo.
    echo Pipeline completed successfully!
    echo Check the output\ directory for your generated assets.
) else (
    echo.
    echo Pipeline encountered errors. Check logs for details.
)


@echo off
REM Installation and Setup Script for Assignment 1 (Windows)

echo CS 440 Assignment 1 - Setup Script
echo ====================================
echo.

REM Check Python installation
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH!
    echo Please install Python 3.7 or higher from https://www.python.org
    pause
    exit /b 1
)

for /f "tokens=*" %%i in ('python --version') do set PYTHON_VERSION=%%i
echo OK Found %PYTHON_VERSION%
echo.

REM Install dependencies
echo Installing dependencies...
python -m pip install --upgrade pip
python -m pip install numpy matplotlib scipy

echo.
echo OK Dependencies installed successfully
echo.

REM Create data directory
echo Creating data directories...
if not exist "data\gridworlds" mkdir "data\gridworlds"
if not exist "data\visualizations" mkdir "data\visualizations"
if not exist "results" mkdir "results"

echo OK Directories created
echo.

REM Run experiments
echo Running experiments...
echo This will generate 50 gridworlds and run all tests.
echo.

cd src\experiments
python runner.py

echo.
echo OK Experiments completed!
echo Results saved to results\experiment_results.json
echo Visualizations saved to data\visualizations\
echo.

REM Compile LaTeX report (if pdflatex available)
echo Attempting to compile LaTeX report...
cd ..\..\report

where pdflatex >nul 2>&1
if errorlevel 1 (
    echo WARNING: LaTeX not found. Report source is at report.tex
    echo To generate PDF, install MiKTeX or similar LaTeX distribution
) else (
    pdflatex -interaction=nonstopmode report.tex >nul 2>&1
    pdflatex -interaction=nonstopmode report.tex >nul 2>&1
    echo OK PDF report generated: report.pdf
)

echo.
echo Setup Complete!
echo ====================================
pause

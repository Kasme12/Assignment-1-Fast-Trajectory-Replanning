#!/bin/bash
# Installation and Setup Script for Assignment 1

echo "CS 440 Assignment 1 - Setup Script"
echo "===================================="
echo ""

# Check Python installation
if ! command -v python3 &> /dev/null; then
    echo "ERROR: Python 3 is not installed!"
    echo "Please install Python 3.7 or higher from https://www.python.org"
    exit 1
fi

PYTHON_VERSION=$(python3 --version)
echo "✓ Found $PYTHON_VERSION"
echo ""

# Install dependencies
echo "Installing dependencies..."
python3 -m pip install --upgrade pip
python3 -m pip install numpy matplotlib scipy

echo ""
echo "✓ Dependencies installed successfully"
echo ""

# Create data directory
echo "Creating data directories..."
mkdir -p data/gridworlds
mkdir -p data/visualizations
mkdir -p results

echo "✓ Directories created"
echo ""

# Run experiments
echo "Running experiments..."
echo "This will generate 50 gridworlds and run all tests."
echo ""

cd src/experiments
python3 runner.py

echo ""
echo "✓ Experiments completed!"
echo "Results saved to results/experiment_results.json"
echo "Visualizations saved to data/visualizations/"
echo ""

# Compile LaTeX report
echo "Compiling LaTeX report..."
cd ../../report

if command -v pdflatex &> /dev/null; then
    pdflatex -interaction=nonstopmode report.tex > /dev/null 2>&1
    pdflatex -interaction=nonstopmode report.tex > /dev/null 2>&1
    echo "✓ PDF report generated: report.pdf"
else
    echo "⚠ LaTeX not found. Report source is at report.tex"
    echo "  To generate PDF, install texlive or similar LaTeX distribution"
fi

echo ""
echo "Setup Complete!"
echo "================================"

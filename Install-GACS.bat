@echo off
setlocal EnableDelayedExpansion
title GACS Setup
echo ==========================================
echo GACS Automated Setup
echo ==========================================
echo.

:: Check for Python
echo [1/4] Checking Python installation...
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python not found in PATH!
    echo Please install Python from https://python.org
    echo Make sure to check "Add Python to PATH" during install.
    pause
    exit /b 1
)
echo Python found.
echo.

:: Install Python libraries
echo [2/4] Installing Python libraries...
python -m pip install keyboard pyautogui pytesseract Pillow
if errorlevel 1 (
    echo ERROR: Failed to install Python libraries.
    pause
    exit /b 1
)
echo Python libraries installed.
echo.

:: Download Tesseract
echo [3/4] Downloading Tesseract OCR...
set "TESS_URL=https://github.com/UB-Mannheim/tesseract/releases/download/v5.4.0.20240606/tesseract-ocr-w64-setup-5.4.0.20240606.exe"
set "TESS_INSTALLER=%TEMP%\tesseract-setup.exe"

echo Downloading from GitHub...
powershell -Command "Invoke-WebRequest -Uri '%TESS_URL%' -OutFile '%TESS_INSTALLER%'" 2>nul
if not exist "%TESS_INSTALLER%" (
    echo Retry with curl...
    curl -L -o "%TESS_INSTALLER%" "%TESS_URL%" 2>nul
)
if not exist "%TESS_INSTALLER%" (
    echo ERROR: Download failed. Please download manually from:
    echo https://github.com/UB-Mannheim/tesseract/releases
    pause
    exit /b 1
)
echo Download complete.
echo.

:: Install Tesseract
echo [4/4] Installing Tesseract OCR...
echo This may take a minute...
start /wait "" "%TESS_INSTALLER%" /S
if errorlevel 1 (
    echo WARNING: Silent install may have failed, trying normal install...
    start /wait "" "%TESS_INSTALLER%"
)

:: Cleanup
del "%TESS_INSTALLER%" 2>nul

:: Verify installation
if exist "C:\Program Files\Tesseract-OCR\tesseract.exe" (
    echo.
    echo ==========================================
    echo SUCCESS! Setup complete.
    echo ==========================================
    echo.
    echo Tesseract installed to: C:\Program Files\Tesseract-OCR\
    echo Python libraries installed.
    echo.
    echo You can now run GACS.py
    echo.
) else (
    echo.
    echo WARNING: Could not verify Tesseract installation.
    echo Please check if it was installed successfully.
    echo Expected location: C:\Program Files\Tesseract-OCR\tesseract.exe
    echo.
)

pause
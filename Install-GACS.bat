@echo off
setlocal enabledelayedexpansion
title GACS2 one-time installer
set "HERE=%~dp0"
set "PY=%HERE%portable-python\python.exe"
set "VENV=%HERE%venv"

echo --- 1. Downloading portable Python 3.11 (18 MB) ---
powershell -NoP -C "& {
  $url='https://github.com/indygreg/python-build-standalone/releases/download/20231002/cpython-3.11.5+20231002-x86_64-pc-windows-msvc-shared-install_only.tar.gz';
  $tmp=(Join-Path $env:TEMP 'py.tar.gz');
  Invoke-WebRequest -Uri $url -OutFile $tmp;
  tar -xf $tmp -C '%HERE%' --strip-components=1;
  Rename-Item '%HERE%\python' 'portable-python'
}"

echo --- 2. Creating venv ---
"%PY%" -m venv "%VENV%"

echo --- 3. Installing packages ---
"%VENV%\Scripts\python.exe" -m pip install -U pip wheel
"%VENV%\Scripts\python.exe" -m pip install keyboard pyautogui pillow pytesseract opencv-python

echo --- 4. Creating desktop shortcut ---
set "DESK=%USERPROFILE%\Desktop\GACS2.lnk"
powershell -NoP -C "$WshShell=New-Object -ComObject WScript.Shell; $lnk=$WshShell.CreateShortcut('%DESK%'); $lnk.TargetPath='%VENV%\Scripts\pythonw.exe'; $lnk.Arguments='\"%HERE%GACS2.py\"'; $lnk.WorkingDirectory='%HERE%'; $lnk.WindowStyle=0; $lnk.Save()"

echo.
echo === DONE ===
echo Double-click the new "GACS2" desktop icon to run the bot.
echo (First time: tab into GTA, then press = to start, - to stop)
pause

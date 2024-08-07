@echo off

REM Stažení závislostí
pip install -r requirements.txt

REM Vytvoření zástupce na ploše
set SCRIPT_PATH=%~dp0
set DESKTOP_PATH=%USERPROFILE%\Desktop
set PYTHON_PATH=%PYTHONHOME%\python.exe

REM Vytvoření zástupce pomocí PowerShellu
powershell -Command "$s=(New-Object -COM WScript.Shell).CreateShortcut('%DESKTOP_PATH%\Ambulance App.lnk');$s.TargetPath='%PYTHON_PATH%';$s.Arguments='%SCRIPT_PATH%main.py';$s.IconLocation='%SCRIPT_PATH%icon.ico';$s.Save()"

echo Instalace dokončena. Zástupce byl vytvořen na ploše.
pause

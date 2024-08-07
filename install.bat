@echo off

REM Vytvoření virtuálního prostředí
python -m venv venv
call venv\Scripts\activate

REM Instalace závislostí
pip install -r requirements.txt

REM Získání cesty k aktuálnímu skriptu
set SCRIPT_PATH=%~dp0
set DESKTOP_PATH=%USERPROFILE%\Desktop
set PYTHON_PATH=%SCRIPT_PATH%venv\Scripts\python.exe

REM Vytvoření zástupce pomocí PowerShellu
echo Vytváření zástupce na ploše...
powershell -Command "$s=(New-Object -COM WScript.Shell).CreateShortcut('%DESKTOP_PATH%\Ambulance App.lnk');$s.TargetPath='%PYTHON_PATH%';$s.Arguments='%SCRIPT_PATH%main.py';$s.IconLocation='%SCRIPT_PATH%icon.ico';$s.Save()"

if exist "%DESKTOP_PATH%\Ambulance App.lnk" (
    echo Zástupce byl úspěšně vytvořen na ploše.
) else (
    echo Chyba: Zástupce nebyl vytvořen.
)

echo Instalace dokončena. Stiskněte libovolnou klávesu pro ukončení.
pause

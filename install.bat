@echo off

REM Vytvoření virtuálního prostředí
python -m venv venv
call venv\Scripts\activate

REM Instalace závislostí
pip install -r requirements.txt

REM Získání cesty k aktuálnímu skriptu
set SCRIPT_PATH=%~dp0
set DESKTOP_PATH=%USERPROFILE%\Desktop
set PYTHON_PATH=%~dp0venv\Scripts\python.exe
set SCRIPT_FILE=%SCRIPT_PATH%ambulance.py

REM Vytvoření zástupce pomocí VBScriptu
echo Vytváření zástupce na ploše...
cscript create_shortcut.vbs "%PYTHON_PATH%" "%SCRIPT_FILE%"

if exist "%DESKTOP_PATH%\Ambulance App.lnk" (
    echo Zástupce byl úspěšně vytvořen na ploše.
) else (
    echo Chyba: Zástupce nebyl vytvořen.
)

echo Instalace dokončena. Stiskněte libovolnou klávesu pro ukončení.
pause

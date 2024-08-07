@echo off

REM Vytvoření virtuálního prostředí
python -m venv venv
call venv\Scripts\activate

REM Instalace závislostí
pip install -r requirements.txt

REM Vytvoření spustitelného souboru
python -m PyInstaller --onefile --icon=icon.ico main.py

REM Získání cesty k aktuálnímu skriptu
set SCRIPT_PATH=%~dp0
set DIST_PATH=%SCRIPT_PATH%dist
set DESKTOP_PATH=%USERPROFILE%\Desktop
set EXE_PATH=%DIST_PATH%\main.exe
set ICON_PATH=%SCRIPT_PATH%icon.ico

REM Vytvoření zástupce pomocí VBScriptu
echo Vytváření zástupce na ploše...
cscript create_shortcut.vbs "%EXE_PATH%" "%ICON_PATH%"

if exist "%DESKTOP_PATH%\Ambulance App.lnk" (
    echo Zástupce byl úspěšně vytvořen na ploše.
) else (
    echo Chyba: Zástupce nebyl vytvořen.
)

echo Instalace dokončena. Stiskněte libovolnou klávesu pro ukončení.
pause

#!/bin/bash

# Stažení repozitáře
git clone https://github.com/adamlnenicka/ambulance.git
cd ambulance

# Instalace závislostí
pip install -r requirements.txt

# Vytvoření zástupce na ploše
desktop=$(xdg-user-dir DESKTOP)
target=$(which python3)
echo "[Desktop Entry]
Name=Ambulance
Exec=$target $(pwd)/main.py
Type=Application
Icon=$(pwd)/icon.png
Terminal=false" > "$desktop/Ambulance.desktop"

chmod +x "$desktop/Ambulance.desktop"

echo "Instalace dokončena. Zástupce byl vytvořen na ploše."

from setuptools import setup, find_packages
import os

setup(
    name='ambulance_app',
    version='1.0',
    packages=find_packages(),
    install_requires=[
        'tkcalendar',
        'pandas',
        'fpdf',
        'Pillow'
    ],
    entry_points={
        'console_scripts': [
            'ambulance-app = main:main',
        ],
    },
)

# Vytvoření zástupce na ploše
desktop = os.path.join(os.path.join(os.environ['USERPROFILE']), 'Desktop')
shortcut = os.path.join(desktop, 'Ambulance App.lnk')
target = os.path.join(os.environ['USERPROFILE'], 'AppData', 'Local', 'Programs', 'Python', 'Python39', 'Scripts', 'ambulance-app.exe')

with open(shortcut, 'w') as f:
    f.write(f"""
[InternetShortcut]
URL=file://{target}
IconIndex=0
IconFile={target}
""")

from setuptools import setup, find_packages

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
)

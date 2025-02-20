@echo off
pip install --upgrade --target venv\Lib\site-packages requests
venv\Scripts\python.exe checkCookie.py
pause

@echo off
pip install --upgrade --target venv\Lib\site-packages pytubefix
pip install --upgrade --target venv\Lib\site-packages ffmpeg-python
venv\Scripts\python.exe YTDL.py
pause

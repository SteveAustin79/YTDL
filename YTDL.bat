@echo off
pip install --upgrade --target venv\Lib\site-packages pytubefix browser-cookie3 ffmpeg-python
venv\Scripts\python.exe YTDL.py
pause

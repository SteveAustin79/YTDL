# YTDL - YouTubeDownLoader 0.4
A command line YouTube video downloader, downloading a specific video resolution file and a 128kps audio stream, finally merged into a single file. Use of ffmpeg and pytubefix.

#### Note: Member, ageRestricted or unplayable videos cannot be downloaded with YTDL or YTDLchannel!

### History
- 20250227 - v0.4 - download path structure based on YTDLchannel v0.1
- 20250224 - v0.3 - config file support
- 20250223 - v0.2 - added webm support (>1080p)
- 20250220 - v0.1 - initial version

<br/>

# YTDLchannel - YouTubeChannelDownloader 0.3
Download all videos from a specific YouTube channel.

### Features
- highest available resolution will be downloaded automatically
- sub directory structure will be suggested
- already downloaded videos will be skipped

### History
- 20250228 - v0.3 - added limit for max resolution
- 20250227 - v0.2 - enhanced file support (checks if already downloaded etc)
- 20250226 - v0.1 - initial version, based on YTDL v0.3

### 2do
- check /tmp dir for merged file to prevent downloading again

<br/>

## Prerequisites
- Git (https://git-scm.com/downloads)
- Python (https://www.python.org)
- FFMPG (https://ffmpeg.org)

## Installation/Start
- <code>git clone https://github.com/SteveAustin79/YTDL.git</code>
- <code>cd YTDL</code>
- <code>python3 -m venv venv</code>
- <code>sudo venv/bin/python3 -m pip install pytubefix ffmpeg-python</code>
- modify config.json
- <code>venv/bin/python3 YTDL.py</code>
- or
- <code>venv/bin/python3 YTDLchannel.py</code>

## Update
- <code>git pull https://github.com/SteveAustin79/YTDL.git</code>

# YTDLchannel - YouTubeChannelDownloader 0.5
Download one, multiple ar all videos from a specific YouTube channel in any available resolution as mp4.

### Features
- filters: video title name, minimum video views, video duration, exclude/include video ID's 
- channels.txt: YouTube Channels list
- video resolutions > 1080p only provided as webm by YouTube -> converted to mp4 after downloading
- highest available resolution (limitable) downloaded automatically
- sub directory structure switch in config.json
- skipping already downloaded videos

### History
- 20250301 - v0.5 - added support to exclude videos by video_id, filters
- 20250228 - v0.4 - added support for age_restricted videos
- 20250228 - v0.3 - added optional limit for max resolution, channels.txt list
- 20250227 - v0.2 - file support (checks if already downloaded)
- 20250226 - v0.1 - initial version, based on YTDL v0.3

### 2do
- check /tmp dir for merged file to prevent downloading again

<br/>

# YTDL - YouTubeDownLoader 0.4

![#f03c15](Deprecated! --> YTDLchannel supports now also video URL's!)

A command line YouTube video downloader, downloading a specific video resolution file and a 128kps audio stream, finally merged into a single file. Use of ffmpeg and pytubefix.

Download unrestricted/playable videos:<br/>
<code>venv/bin/python3 YTDL.py</code><br/><br/>

Download restricted/playable videos:<br/>
<code>venv/bin/python3 YTDLx.py</code>

### History
- 20250227 - v0.4 - download path structure based on YTDLchannel v0.1
- 20250224 - v0.3 - config file support
- 20250223 - v0.2 - added webm support (>1080p)
- 20250220 - v0.1 - initial version

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
- <code>cp config.example.json config.json</code>
- modify config.json
- add channel URLs to channels.txt (not required)
- <code>venv/bin/python3 YTDL.py</code>
- or
- <code>venv/bin/python3 YTDLchannel.py</code>

## Update
- <code>git pull https://github.com/SteveAustin79/YTDL.git</code>

# YTDL - YouTube Channel Downloader 0.6
Download one, multiple or all videos from a specific YouTube channel in any available resolution as mp4.

Restricted video download possible, but requires authentication via accounts.google.com/device.

### Features
- channel config file with default filters (file must be located in target directory)
- filters: video title name, minimum video views, video duration, exclude/include video ID's 
- channels.txt: YouTube Channels list
- video resolutions > 1080p only provided as webm by YouTube -> converted to mp4 after downloading
- highest available resolution (can be limited) downloaded automatically
- sub directory structure switch in config.json
- skipping already downloaded videos

### History
- 20250302 - v0.6 - added channel config file support 
- 20250301 - v0.5 - added exclude videos by video_id, filter support 
- 20250228 - v0.4 - added age_restricted videos support 
- 20250228 - v0.3 - added optional limit for max resolution, channels.txt list
- 20250227 - v0.2 - file support (check if already downloaded)
- 20250226 - v0.1 - initial version, based on YTDL v0.3

## Prerequisites
- Git (https://git-scm.com/downloads)
- Python (https://www.python.org)
- FFMPG (https://ffmpeg.org)

## Installation
1. Clone repository:
```diff
git clone https://github.com/SteveAustin79/YTDL.git
```
2. Change directory
```diff
cd YTDL
```
3. Install python environment
```diff
python3 -m venv venv
```
4. Install dependencies
```diff
sudo venv/bin/python3 -m pip install pytubefix ffmpeg-python
```
5. Create and modify config.json
```diff
cp config.example.json config.json
nano config.json
```
6. Add channel URLs to channels.txt (optional)
```diff
nano channels.txt
```
7. Run the application
```diff
venv/bin/python3 YTDLchannel.py
```

## Update
```diff
git pull https://github.com/SteveAustin79/YTDL.git
```

<br/><br/>

## YTDL - YouTubeDownLoader 0.4 - DEPRECATED!

### Deprecated! --> YTDLchannel supports now also video URL's!

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
from pytubefix import YouTube
import requests


# ✅ Function to Load Cookies from cookies.txt
def load_cookies_from_file(filename):
    """Reads cookies from cookies.txt and returns them as a dictionary."""
    cookies = {}
    with open(filename, "r") as f:
        for line in f:
            if not line.startswith("#"):
                parts = line.strip().split("\t")
                if len(parts) >= 7:
                    cookies[parts[5]] = parts[6]  # Extract name and value
    return cookies


# 🔹 Subclass YouTube to Override `watch_html`
class YouTubeWithCookies(YouTube):
    def __init__(self, url, cookies):
        self._cookies = cookies  # Store cookies
        super().__init__(url)  # Call original YouTube constructor

    @property
    def watch_html(self):
        """Fetch video page manually with authentication cookies."""
        headers = {"User-Agent": "Mozilla/5.0"}
        response = requests.get(self.watch_url, headers=headers, cookies=self._cookies)

        if response.status_code != 200:
            raise Exception(f"❌ Failed to fetch video page! HTTP {response.status_code}")

        return response.text  # Return HTML content for PyTubeFix to parse


# 🔹 YouTube video URL (must be logged in to access)
video_url = "https://www.youtube.com/watch?v=HH_iMeIRHxk"

# 🔹 Load cookies from `cookies.txt`
cookie_dict = load_cookies_from_file("cookies.txt")

# 🔹 Create YouTube object using our subclass
yt = YouTubeWithCookies(video_url, cookie_dict)

# 🔹 Perform age check (needed for restricted videos)
yt.age_check()

# 🔹 Download highest quality stream
for idx, i in enumerate(yt.streams):
    if i.resolution == res:
        break

print("Downloading VIDEO...\n")

yt.streams[idx].download()

print("Download VIDEO complete. Downloading AUDIO...\n")

for idx, i in enumerate(yt.streams):
    if i.bitrate == "128kbps":
        break
yt.streams[idx].download()

print("Download AUDIO complete.")

print("✅ Download complete!")

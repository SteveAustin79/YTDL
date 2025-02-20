import requests

# ✅ Function to Load Cookies from cookies.txt
def load_cookies_from_file(filename):
    """Reads cookies from a cookies.txt file and returns them as a dictionary."""
    cookies = {}
    with open(filename, "r") as f:
        for line in f:
            if not line.startswith("#"):
                parts = line.strip().split("\t")
                if len(parts) >= 7:
                    cookies[parts[5]] = parts[6]  # Extract name and value
    return cookies

cookies = load_cookies_from_file("cookies.txt")
headers = {"User-Agent": "Mozilla/5.0"}

response = requests.get("https://www.youtube.com", cookies=cookies, headers=headers)

print(response.status_code)  # Should return 200 if cookies are working
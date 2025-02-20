import requests

cookies = load_cookies_from_file("cookies.txt")
headers = {"User-Agent": "Mozilla/5.0"}

response = requests.get("https://www.youtube.com", cookies=cookies, headers=headers)

print(response.status_code)  # Should return 200 if cookies are working
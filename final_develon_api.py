import requests
import json
import urllib3
from bs4 import BeautifulSoup

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# Load cookies
with open("develon_cookies.json", "r") as f:
    cookies_list = json.load(f)
cookies = {cookie['name']: cookie['value'] for cookie in cookies_list}

# FULL browser headers, including the AJAX header
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36 Edg/124.0.0.0",
    "Accept": "text/html, */*; q=0.01",
    "Accept-Language": "en-US,en;q=0.9",
    "X-Requested-With": "XMLHttpRequest",  # <--- THIS IS THE MAGIC HEADER
    "Referer": "https://gsps.hd-ce.com/cepcna/catalog/parts_books_search_pvw.jsp",
    "Connection": "keep-alive"
}

test_part = "DS130602-00850"
# Let's try the search URL directly
url = f"https://gsps.hd-ce.com/cepcna/catalog/parts_books_search_pvw.jsp?v_search_type=PART_NO&v_search_value={test_part}"

print(f"Hitting: {url}")
response = requests.get(url, cookies=cookies, headers=headers, verify=False)

print(f"Status Code: {response.status_code}")
print(f"Content Length: {len(response.text)}")

if len(response.text) < 1000:
    print("\n--- RAW RESPONSE ---")
    print(response.text)
else:
    print("\n--- PARSED TEXT ---")
    soup = BeautifulSoup(response.text, 'html.parser')
    text = soup.get_text(separator='\n', strip=True)
    print(text[:2000])

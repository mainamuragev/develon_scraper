import requests
import json
import urllib3
from bs4 import BeautifulSoup

# Suppress SSL warnings
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# Load your fresh cookies
with open("develon_cookies.json", "r") as f:
    cookies_list = json.load(f)

# Convert to requests format
cookies = {cookie['name']: cookie['value'] for cookie in cookies_list}

# Standard browser headers
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36 Edg/124.0.0.0",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.9",
    "Referer": "https://gsps.hd-ce.com/cepcna/main/main.jsp"
}

test_part = "DS130602-00850"
url = f"https://gsps.hd-ce.com/cepcna/catalog/parts_books_search_pvw.jsp?v_search_type=PART_NO&v_search_value={test_part}"

print(f"Fetching: {url}")
response = requests.get(url, cookies=cookies, headers=headers, verify=False)

print(f"Status Code: {response.status_code}")
print(f"Content Length: {len(response.text)} bytes")

if len(response.text) < 500:
    print("\n--- RAW RESPONSE ---")
    print(response.text)
else:
    print("\n--- PARSING HTML ---")
    soup = BeautifulSoup(response.text, 'html.parser')
    text = soup.get_text(separator='\n', strip=True)
    print(text[:2000]) # Print first 2000 chars
    
    # Save it just in case
    with open("develon_requests_output.html", "w", encoding="utf-8") as f:
        f.write(response.text)
    print("\nSaved full HTML to develon_requests_output.html")

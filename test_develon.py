import requests
import json
import urllib3

# Suppress SSL warnings
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# Load your session cookies
with open("develon_cookies.json", "r") as f:
    cookies_list = json.load(f)

# Convert from the extension format to Python requests format
cookies = {cookie['name']: cookie['value'] for cookie in cookies_list}

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.5",
    "Referer": "https://gsps.hd-ce.com/cepcna/main/main.jsp"
}

# The URL of the main page
url = "https://gsps.hd-ce.com/cepcna/main/main.jsp?version=2A&SSO_YN=LoginOK&loginNo=&password=&EAI_LAN_CD=EN&p_auto_part_no=&p_partsbk_no=&p_stype=&p_equip_suffix=&p_equip_serielno="

print("Connecting to Develon...")
response = requests.get(url, cookies=cookies, headers=headers, verify=False)

print(f"Status Code: {response.status_code}")

if response.status_code == 200:
    print("Success! We are in.")
    # Let's check if we got the actual page or a login redirect
    if "DEVELON" in response.text or "HD CONSTRUCTION" in response.text:
        print("Confirmed: We are logged in. The page data is accessible.")
        # Save the HTML so we can inspect it for search URLs
        with open("develon_main.html", "w", encoding="utf-8") as f:
            f.write(response.text)
        print("Saved the page HTML to 'develon_main.html'.")
    else:
        print("Warning: We got a 200 OK, but the page doesn't look like the main dashboard.")
        print("The session might be expired or the server redirected us to a login page.")
        print(response.text[:500])
else:
    print("Failed to connect. Response:")
    print(response.text[:500])

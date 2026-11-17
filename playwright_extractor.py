from playwright.sync_api import sync_playwright
import json
import time

def extract_data():
    with open("develon_cookies.json", "r") as f:
        cookies_list = json.load(f)

    playwright_cookies = []
    for c in cookies_list:
        playwright_cookies.append({
            "name": c["name"], "value": c["value"], "domain": c["domain"],
            "path": c["path"], "expires": c.get("expirationDate", -1),
            "httpOnly": c.get("httpOnly", False), "secure": c.get("secure", False),
            "sameSite": "Lax"
        })

    with sync_playwright() as p:
        # Launch browser (headless=False so you can watch it)
        browser = p.chromium.launch(headless=False, channel="msedge")
        context = browser.new_context()
        context.add_cookies(playwright_cookies)
        page = context.new_page()

        # The URL from your screenshot!
        test_part = "130602-00850"
        url = f"https://gsps.hd-ce.com/cepcna/catalog/parts_books_search_pvw.jsp?v_search_type=PART_NO&v_search_value={test_part}"

        print(f"Navigating to: {url}")
        try:
            page.goto(url, wait_until="domcontentloaded", timeout=60000)
        except Exception as e:
            print(f"Page load timeout, continuing... Error: {e}")

        print("Waiting 10 seconds for the dynamic data to load...")
        time.sleep(10) 
        
        print("\n--- PAGE TEXT ---")
        # The data is likely in a specific div or table. 
        # Let's just grab the whole body text first to see if it's there.
        try:
            page_text = page.locator("body").inner_text()
            print(page_text[:2000]) # Print first 2000 chars
        except Exception as e:
            print(f"Could not read text: {e}")
        
        print("\nBrowser staying open for 60 seconds so you can look at it...")
        page.wait_for_timeout(60000)

if __name__ == "__main__":
    extract_data()

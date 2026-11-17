from playwright.sync_api import sync_playwright
import json
import time

def test_single_develon():
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
        # Added stealth arguments to hide automation
        browser = p.chromium.launch(
            headless=False,
            args=[
                "--disable-blink-features=AutomationControlled",
                "--no-sandbox",
                "--disable-dev-shm-usage"
            ]
        )
        
        context = browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36 Edg/124.0.0.0",
            viewport={"width": 1920, "height": 1080}
        )
        
        # Hide navigator.webdriver
        context.add_init_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
        
        context.add_cookies(playwright_cookies)
        page = context.new_page()

        test_part = "DS130602-00850" 
        url = f"https://gsps.hd-ce.com/cepcna/catalog/parts_books_search_pvw.jsp?v_search_type=PART_NO&v_search_value={test_part}"

        print(f"Navigating to: {url}")
        try:
            page.goto(url, wait_until="networkidle", timeout=60000)
        except Exception as e:
            print(f"Timeout: {e}")

        print("Waiting 15 seconds for data...")
        time.sleep(15)
        
        print("\n--- PAGE TEXT ---")
        print(page.locator("body").inner_text())
        
        # Save the HTML for inspection
        with open("develon_search.html", "w", encoding="utf-8") as f:
            f.write(page.content())
        print("\nSaved HTML to develon_search.html")

        print("\nBrowser staying open for 60 seconds...")
        page.wait_for_timeout(60000)

if __name__ == "__main__":
    test_single_develon()

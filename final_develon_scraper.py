from playwright.sync_api import sync_playwright
import json
import time

def test_develon_playwright():
    # Load the cookies from your exported file
    with open("develon_cookies.json", "r") as f:
        cookies_list = json.load(f)

    # Playwright expects cookies in a specific format
    playwright_cookies = []
    for c in cookies_list:
        playwright_cookies.append({
            "name": c["name"],
            "value": c["value"],
            "domain": c["domain"],
            "path": c["path"],
            "expires": c.get("expirationDate", -1),
            "httpOnly": c.get("httpOnly", False),
            "secure": c.get("secure", False),
            "sameSite": "Lax"
        })

    with sync_playwright() as p:
        # Launch headless (invisible) browser. Change to False if you want to watch.
        browser = p.chromium.launch(headless=True) 
        context = browser.new_context()
        
        # Inject your login cookies!
        context.add_cookies(playwright_cookies)
        
        page = context.new_page()
        
        # The search URL we found
        test_part = "DX300LCA"
        url = f"https://gsps.hd-ce.com/cepcna/catalog/parts_books_search_pvw.jsp?v_search_type=PART_NO&v_search_value={test_part.upper()}"
        
        print(f"Navigating to: {url}")
        page.goto(url, wait_until="domcontentloaded", timeout=60000)
        
        print("Waiting 10 seconds for background data to load...")
        time.sleep(10)
        
        print("\n--- PAGE TEXT ---")
        page_text = page.locator("body").inner_text()
        print(page_text[:1500]) # Print the first 1500 characters to see if data is there
        
        browser.close()

if __name__ == "__main__":
    test_develon_playwright()

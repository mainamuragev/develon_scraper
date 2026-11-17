from playwright.sync_api import sync_playwright
import time

def test_connect():
    with sync_playwright() as p:
        print("Connecting to your open Edge window on Windows...")
        try:
            # Connect using your WSL host IP
            browser = p.chromium.connect_over_cdp("http://172.28.0.1:9222")
            context = browser.contexts[0]
            page = context.pages[0] if context.pages else context.new_page()
        except Exception as e:
            print(f"Error connecting: {e}")
            print("\nMake sure:")
            print("1. Edge is closed, and opened with the --remote-debugging-port=9222 command.")
            print("2. You used the --remote-allow-origins=* flag.")
            print("3. Windows Firewall isn't blocking port 9222.")
            return

        test_part = "DS130602-00850"
        url = f"https://gsps.hd-ce.com/cepcna/catalog/parts_books_search_pvw.jsp?v_search_type=PART_NO&v_search_value={test_part}"
        
        print(f"\nNavigating to: {url}")
        try:
            page.goto(url, wait_until="domcontentloaded", timeout=30000)
        except Exception as e:
            print(f"Page load timeout, continuing...")
        
        print("Waiting 8 seconds for data...")
        time.sleep(8)
        
        print("\n--- PAGE TEXT ---")
        try:
            print(page.locator("body").inner_text()[:2000]) # Print first 2000 chars
        except Exception as e:
            print(f"Could not read text: {e}")
        
        print("\nDone!")

if __name__ == "__main__":
    test_connect()

from playwright.sync_api import sync_playwright
import time

def find_develon_api():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        context = browser.new_context()
        page = context.new_page()

        url = "https://gsps.hd-ce.com/cepcna/main/main.jsp?version=2A&SSO_YN=LoginOK&loginNo=&password=&EAI_LAN_CD=EN&p_auto_part_no=&p_partsbk_no=&p_stype=&p_equip_suffix=&p_equip_serielno="
        
        print("Opening Develon... (waiting for DOM, not full load)")
        try:
            page.goto(url, wait_until="domcontentloaded", timeout=60000)
        except Exception as e:
            print(f"Page load timed out, but we might still be able to interact. Error: {e}")

        print("\n>>> PLEASE LOG IN (IF NEEDED) AND NAVIGATE TO THE SEARCH PAGE <<<")
        page.pause() 

        print("\n--- READY TO CAPTURE ---")
        print("1. Go to the browser window.")
        print("2. Type a part number and click 'Search'.")
        print("3. Wait 10 seconds after the results load.")
        
        time.sleep(15) 
        
        print("\n--- CAPTURED URL ---")
        print(f"Current URL: {page.url}")
        
        print("\nDone! Copy the URL above and send it to me.")
        
        page.wait_for_timeout(60000)

if __name__ == "__main__":
    find_develon_api()

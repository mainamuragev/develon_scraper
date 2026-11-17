import pandas as pd
import json
import time
from playwright.sync_api import sync_playwright
from bs4 import BeautifulSoup
import os

# --- 1. SETUP ---
FILE_NAME = "Develon_item_codes_models.xlsx"
OUTPUT_FILE = "Develon_RESULTS.xlsx"

# Load the cookies you exported from Edge
try:
    with open("develon_cookies.json", "r") as f:
        cookies_list = json.load(f)
except FileNotFoundError:
    print("Error: develon_cookies.json not found. Please export cookies from Edge.")
    exit()

playwright_cookies = []
for c in cookies_list:
    playwright_cookies.append({
        "name": c["name"], "value": c["value"], "domain": c["domain"],
        "path": c["path"], "expires": c.get("expirationDate", -1),
        "httpOnly": c.get("httpOnly", False), "secure": c.get("secure", False),
        "sameSite": "Lax"
    })

def extract_models(html):
    soup = BeautifulSoup(html, 'html.parser')
    model_div = soup.find("div", {"id": "modelMainList"})
    if not model_div:
        return "Not Found"
    
    models = []
    for td in model_div.find_all("td"):
        span = td.find("span")
        if span and span.text.strip() and span.text.strip() != "Model":
            models.append(span.text.strip())
    
    # Remove duplicates
    unique_models = list(dict.fromkeys(models))
    return " | ".join(unique_models) if unique_models else "Not Found"

def main():
    print(f"Loading {FILE_NAME}...")
    df = pd.read_excel(FILE_NAME, sheet_name="Develon")
    
    if "Model" not in df.columns:
        df["Model"] = ""
    df["Model"] = df["Model"].astype(str)

    with sync_playwright() as p:
        print("Launching Chromium...")
        browser = p.chromium.launch(headless=False) # Set to True to hide browser
        context = browser.new_context()
        context.add_cookies(playwright_cookies)
        page = context.new_page()

        # Go to the main page to establish the session
        page.goto("https://gsps.hd-ce.com/cepcna/main/main.jsp", timeout=60000)
        time.sleep(2)

        total_rows = len(df)
        print(f"Starting loop for {total_rows} parts...")

        for index, row in df.iterrows():
            raw_part = str(row["Original Item Code"]).strip()
            
            if pd.notna(row["Model"]) and row["Model"] not in ["", "nan"]:
                continue

            print(f"[{index+1}/{total_rows}] Searching: {raw_part} ... ", end="", flush=True)

            # Strip DS for search
            search_part = raw_part
            if search_part.upper().startswith("DS"):
                search_part = search_part[2:]
                
            url = f"https://gsps.hd-ce.com/cepcna/catalog/parts_books_search_pvw.jsp?v_search_type=PART_NO&v_search_value={search_part}"
            
            models = "Not Found"
            
            try:
                page.goto(url, wait_until="domcontentloaded", timeout=30000)
                time.sleep(3) 
                
                html = page.content()
                models = extract_models(html)
                
                # Try with DS if not found
                if models == "Not Found":
                    url_ds = f"https://gsps.hd-ce.com/cepcna/catalog/parts_books_search_pvw.jsp?v_search_type=PART_NO&v_search_value={raw_part}"
                    page.goto(url_ds, wait_until="domcontentloaded", timeout=30000)
                    time.sleep(3)
                    html_ds = page.content()
                    models = extract_models(html_ds)
                
                df.at[index, "Model"] = models
                
                if models == "Not Found":
                    print("❌ Not Found")
                else:
                    print(f"✅ Found: {models[:50]}...")
                    
            except Exception as e:
                df.at[index, "Model"] = f"Error"
                print(f"❌ Error")

            # Save progress every 5 parts
            if (index + 1) % 5 == 0:
                with pd.ExcelWriter(OUTPUT_FILE, engine='openpyxl') as writer:
                    df.to_excel(writer, sheet_name="Develon", index=False)

        print(f"\nFinished! Saving to {OUTPUT_FILE}...")
        with pd.ExcelWriter(OUTPUT_FILE, engine='openpyxl') as writer:
            df.to_excel(writer, sheet_name="Develon", index=False)
        
        print("Done!")
        browser.close()

if __name__ == "__main__":
    main()

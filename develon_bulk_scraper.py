import pandas as pd
import json
import time
import re
from playwright.sync_api import sync_playwright

# --- 1. SETUP ---
# We load the PREVIOUS output file if it exists, otherwise the original
import os
FILE_NAME = "Develon_WITH_MODELS.xlsx" if os.path.exists("Develon_WITH_MODELS.xlsx") else "Develon_item_codes_models.xlsx"
OUTPUT_FILE = "Develon_FINAL_DATA.xlsx"

# Load cookies
with open("develon_cookies.json", "r") as f:
    cookies_list = json.load(f)

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

def search_develon_part(page, part_number):
    url = f"https://gsps.hd-ce.com/cepcna/catalog/parts_books_search_pvw.jsp?v_search_type=PART_NO&v_search_value={part_number}"
    try:
        page.goto(url, wait_until="domcontentloaded", timeout=30000)
        time.sleep(4) 
        page_text = page.locator("body").inner_text()
        
        if "No data found" in page_text:
            return "Not Found"
            
        return page_text
    except Exception as e:
        return f"Error: {e}"

def main():
    print(f"Loading {FILE_NAME}...")
    sheets = pd.read_excel(FILE_NAME, sheet_name=None)
    
    # ONLY PROCESS THE 'Develon' SHEET
    for sheet_name, df in sheets.items():
        if sheet_name.strip().lower() != "develon":
            continue

        print(f"\n--- Processing Sheet: {sheet_name} ---")
        
        part_col = "Original Item Code"
        
        if "Model" not in df.columns:
            df["Model"] = ""
        
        df["Model"] = df["Model"].astype(str)
        
        # Count how many are left to do
        remaining = len(df[df["Model"].isin(["", "nan"])])
        print(f"Found {len(df)} total parts. {remaining} left to search.")
        
        if remaining == 0:
            print("All parts in this sheet are already searched! Skipping.")
            continue
        
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            context = browser.new_context()
            context.add_cookies(playwright_cookies)
            page = context.new_page()

            for index, row in df.iterrows():
                raw_part = str(row[part_col]).strip()
                
                # SKIP IF ALREADY SEARCHED
                if pd.notna(row["Model"]) and row["Model"] not in ["", "nan"]:
                    continue
                    
                print(f"[{index+1}/{len(df)}] Searching: {raw_part} ... ", end="", flush=True)
                
                result = search_develon_part(page, raw_part)
                
                if result == "Not Found" and raw_part.upper().startswith("DS"):
                    stripped_part = raw_part[2:]
                    result = search_develon_part(page, stripped_part)
                
                df.at[index, "Model"] = result
                
                if result == "Not Found":
                    print("❌ Not Found")
                else:
                    print(f"✅ Found")
                    
                if (index + 1) % 5 == 0:
                    with pd.ExcelWriter(OUTPUT_FILE, engine='openpyxl') as writer:
                        df.to_excel(writer, sheet_name=sheet_name, index=False)
            
            browser.close()
        
        sheets[sheet_name] = df

    print(f"\nSaving final data to {OUTPUT_FILE}...")
    with pd.ExcelWriter(OUTPUT_FILE, engine='openpyxl') as writer:
        if "Develon" in sheets:
            sheets["Develon"].to_excel(writer, sheet_name="Develon", index=False)
            
    print("Done!")

if __name__ == "__main__":
    main()

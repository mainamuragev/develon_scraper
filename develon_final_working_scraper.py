import pandas as pd
from playwright.sync_api import sync_playwright
from bs4 import BeautifulSoup
import json
import time

# --- 1. SETUP ---
FILE_NAME = "Develon_item_codes_models.xlsx"
OUTPUT_FILE = "Develon_WITH_MODELS_FINAL.xlsx"

def extract_models_from_html(html_content):
    soup = BeautifulSoup(html_content, 'html.parser')
    text = soup.get_text(separator='\n', strip=True)
    
    lines = text.split('\n')
    models = []
    capture = False
    
    for line in lines:
        if line.strip() == "Model":
            capture = True
            continue
        if capture:
            if "HD CONSTRUCTION" in line or "WORDS" in line or "off" in line or "Part No." in line:
                break
            if line.strip():
                models.append(line.strip())
    
    seen = set()
    unique_models = []
    for m in models:
        if m not in seen:
            unique_models.append(m)
            seen.add(m)
            
    return " | ".join(unique_models) if unique_models else "Not Found"

def main():
    print(f"Loading {FILE_NAME}...")
    df = pd.read_excel(FILE_NAME, sheet_name="Develon")
    
    if "Model" not in df.columns:
        df["Model"] = ""
    df["Model"] = df["Model"].astype(str)

    with sync_playwright() as p:
        print("Launching Edge with your real profile...")
        print(">>> WARNING: Make sure ALL Edge windows are CLOSED first! <<<")
        
        # Path to your real Windows Edge profile (WSL format)
        edge_user_data = "/mnt/c/Users/murag/AppData/Local/Microsoft/Edge/User Data"
        
        try:
            context = p.chromium.launch_persistent_context(
                user_data_dir=edge_user_data,
                channel="msedge",
                headless=False,
                args=["--profile-directory=Default"]
            )
            page = context.pages[0] if context.pages else context.new_page()
        except Exception as e:
            print(f"Failed to launch Edge. Error: {e}")
            print("Make sure Edge is completely closed and try again.")
            return

        total_rows = len(df)
        print(f"\nStarting loop for {total_rows} parts...")

        for index, row in df.iterrows():
            raw_part = str(row["Original Item Code"]).strip()
            
            # Skip if we already have data
            if pd.notna(row["Model"]) and row["Model"] not in ["", "nan"]:
                continue

            print(f"[{index+1}/{total_rows}] Searching: {raw_part} ... ", end="", flush=True)

            # Prepare search term (strip DS first)
            search_part = raw_part
            if search_part.upper().startswith("DS"):
                search_part = search_part[2:]
                
            url = f"https://gsps.hd-ce.com/cepcna/catalog/parts_books_search_pvw.jsp?v_search_type=PART_NO&v_search_value={search_part}"
            
            models = "Not Found"
            
            try:
                page.goto(url, wait_until="domcontentloaded", timeout=30000)
                time.sleep(3) 
                
                html_content = page.content()
                models = extract_models_from_html(html_content)
                
                # If not found without DS, try WITH the DS prefix
                if models == "Not Found":
                    url_ds = f"https://gsps.hd-ce.com/cepcna/catalog/parts_books_search_pvw.jsp?v_search_type=PART_NO&v_search_value={raw_part}"
                    page.goto(url_ds, wait_until="domcontentloaded", timeout=30000)
                    time.sleep(3)
                    html_content_ds = page.content()
                    models = extract_models_from_html(html_content_ds)
                
                df.at[index, "Model"] = models
                
                if models == "Not Found":
                    print("❌ Not Found")
                else:
                    print(f"✅ Found: {models[:50]}...")
                    
            except Exception as e:
                df.at[index, "Model"] = f"Error: {e}"
                print(f"❌ Error")

            # Save every 5 items
            if (index + 1) % 5 == 0:
                with pd.ExcelWriter(OUTPUT_FILE, engine='openpyxl') as writer:
                    df.to_excel(writer, sheet_name="Develon", index=False)

        print(f"\nFinished! Saving final data to {OUTPUT_FILE}...")
        with pd.ExcelWriter(OUTPUT_FILE, engine='openpyxl') as writer:
            df.to_excel(writer, sheet_name="Develon", index=False)
        
        print("Done!")
        context.close()

if __name__ == "__main__":
    main()

import pandas as pd
from playwright.sync_api import sync_playwright
import time

# --- 1. SETUP ---
FILE_NAME = "Develon_item_codes_models.xlsx"
OUTPUT_FILE = "Develon_FINAL_ATTEMPT.xlsx"

def main():
    print(f"Loading {FILE_NAME}...")
    df = pd.read_excel(FILE_NAME, sheet_name="Develon")
    
    if "Model" not in df.columns:
        df["Model"] = ""
    df["Model"] = df["Model"].astype(str)

    with sync_playwright() as p:
        # The exact WSL path to your Windows Edge profile
        edge_user_data = "/mnt/c/Users/murag/AppData/Local/Microsoft/Edge/User Data"
        
        print("Launching Edge with your real profile...")
        print(">>> WARNING: Make sure all Edge windows are CLOSED first! <<<")
        
        try:
            context = p.chromium.launch_persistent_context(
                user_data_dir=edge_user_data,
                channel="msedge",
                headless=False,
                args=["--profile-directory=Default"]
            )
        except Exception as e:
            print(f"Failed to launch Edge. Error: {e}")
            print("Make sure Edge is completely closed and try again.")
            return

        # Get the active page (or open a new one if it opens blank)
        page = context.pages[0] if context.pages else context.new_page()

        print("\n>>> PLEASE LOG IN MANUALLY IN THE EDGE WINDOW (IF NOT ALREADY) <<<")
        print("Once you are on the Develon dashboard, press ENTER here to start.")
        input() 

        total_rows = len(df)
        print(f"\nStarting loop for {total_rows} parts...")

        for index, row in df.iterrows():
            raw_part = str(row["Original Item Code"]).strip()
            
            if pd.notna(row["Model"]) and row["Model"] not in ["", "nan"]:
                continue

            print(f"[{index+1}/{total_rows}] Searching: {raw_part} ... ", end="", flush=True)

            url = f"https://gsps.hd-ce.com/cepcna/catalog/parts_books_search_pvw.jsp?v_search_type=PART_NO&v_search_value={raw_part}"
            
            try:
                page.goto(url, wait_until="domcontentloaded", timeout=30000)
                time.sleep(3) 
                
                page_text = page.locator("body").inner_text()
                
                if "No data found" in page_text or not page_text.strip():
                    df.at[index, "Model"] = "Not Found"
                    print("❌ Not Found")
                else:
                    df.at[index, "Model"] = page_text
                    print("✅ Found")
            except Exception as e:
                df.at[index, "Model"] = f"Error: {e}"
                print(f"❌ Error")

            if (index + 1) % 5 == 0:
                with pd.ExcelWriter(OUTPUT_FILE, engine='openpyxl') as writer:
                    df.to_excel(writer, sheet_name="Develon", index=False)

        print(f"\nFinished! Saving to {OUTPUT_FILE}...")
        with pd.ExcelWriter(OUTPUT_FILE, engine='openpyxl') as writer:
            df.to_excel(writer, sheet_name="Develon", index=False)
        
        print("Done!")
        context.close()

if __name__ == "__main__":
    main()

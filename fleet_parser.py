import os
import glob
from bs4 import BeautifulSoup
import pandas as pd

# --- YOUR EXACT FLEET LIST ---
my_fleet = [
    "ADT", "DX225LCA-7M", "DX420LCA", "DX420LCA-K", "DL250A", "DL300A", 
    "DL550", "DL551", "DX140LC", "DX220LCA-2", "DX220LCA-2M", "DX225LCA", 
    "DX300LCA", "DX300LCA-7M", "DX340LCA", "DX340LCA-K", "DX360LCA-7M", 
    "DXB230", "HB20", "HB30", "MG22", "S300LC", "SD 300", "SD200", 
    "SD200-2", "SD300E", "SD300H", "SD300N", "SD320A"
]

def extract_models_from_file(filepath):
    with open(filepath, "r", encoding="utf-8", errors="ignore") as f:
        html_content = f.read()
        
    soup = BeautifulSoup(html_content, 'html.parser')
    model_div = soup.find("div", {"id": "modelMainList"})
    
    if not model_div:
        return "Not Found"
    
    models = []
    for td in model_div.find_all("td"):
        span = td.find("span")
        if span and span.text.strip() and span.text.strip() != "Model":
            model_name = span.text.strip()
            
            # Check if this model is in our fleet
            # (Using a substring check so "SD 300" matches "SD300")
            for fleet_model in my_fleet:
                if fleet_model in model_name or model_name in fleet_model:
                    models.append(model_name)
                    break
    
    unique_models = list(dict.fromkeys(models))
    return " | ".join(unique_models) if unique_models else "Not in Fleet"

def main():
    download_dir = "/mnt/c/Users/murag/Downloads"
    html_files = glob.glob(os.path.join(download_dir, "*.html"))
    
    if not html_files:
        print(f"No HTML files found in {download_dir}")
        return
        
    print(f"Found {len(html_files)} HTML files.\n")
    
    results = []
    
    for filepath in html_files:
        filename = os.path.basename(filepath)
        part_number = filename.replace(".html", "")
        
        # Skip generic files
        if not part_number[0].isdigit() and not part_number.startswith("DS"):
            continue
        
        print(f"Parsing: {part_number} ... ", end="", flush=True)
        models = extract_models_from_file(filepath)
        
        if models == "Not in Fleet":
            print("❌ Not in Fleet")
        else:
            print(f"✅ Found: {models}")
            
        results.append({"Part Number": part_number, "Matching Fleet Models": models})
    
    if not results:
        print("No valid files found.")
        return
    
    df = pd.DataFrame(results)
    output_file = "Develon_FLEET_MATCHES.xlsx"
    df.to_excel(output_file, index=False)
    print(f"\nDone! Saved to {output_file}")
    print(f"Copy to Windows: cp {output_file} /mnt/c/Users/murag/Downloads/")

if __name__ == "__main__":
    main()

import os
import glob
from bs4 import BeautifulSoup
import pandas as pd
import re

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
            models.append(span.text.strip())
    
    seen = set()
    unique_models = []
    for m in models:
        if m not in seen:
            unique_models.append(m)
            seen.add(m)
            
    return " | ".join(unique_models) if unique_models else "Not Found"

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
        # Try to extract part number from filename
        # Files named "130602-00850.html" or "DS130602-00850.html"
        part_number = filename.replace(".html", "")
        
        # Skip generic names
        if not re.match(r"^(DS)?\d", part_number):
            print(f"Skipping generic file: {filename}")
            continue
        
        print(f"Parsing: {part_number} ... ", end="", flush=True)
        models = extract_models_from_file(filepath)
        
        if models == "Not Found":
            print("❌ Not Found")
        else:
            print(f"✅ Found: {models[:50]}...")
            
        results.append({"Part Number": part_number, "Model": models})
    
    if not results:
        print("No files with valid part number names found.")
        return
    
    df = pd.DataFrame(results)
    output_file = "Develon_MANUAL_HTML_RESULTS.xlsx"
    df.to_excel(output_file, index=False)
    print(f"\nDone! Saved {len(results)} results to {output_file}")
    print(f"Copy to Windows: cp {output_file} /mnt/c/Users/murag/Downloads/")

if __name__ == "__main__":
    main()

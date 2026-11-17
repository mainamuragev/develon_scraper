import pandas as pd

# Load the client file
file_name = "All DEVELON CLIENTS.xlsx"

try:
    sheets = pd.read_excel(file_name, sheet_name=None)
except FileNotFoundError:
    print(f"Error: Could not find '{file_name}'. Please make sure it is in the current folder.")
    exit()

unique_models = set()

for sheet_name, df in sheets.items():
    # Look for the 'MODEL' column
    if 'MODEL' in df.columns:
        # Drop empty rows and get unique values
        models = df['MODEL'].dropna().astype(str).str.strip().unique()
        for m in models:
            if m != "" and m != "MODEL":
                unique_models.add(m)

print("--- UNIQUE MODELS FOUND ---")
for m in sorted(unique_models):
    print(m)

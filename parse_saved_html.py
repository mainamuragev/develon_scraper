from bs4 import BeautifulSoup

# Open the HTML file you saved
with open("search_result.html", "r", encoding="utf-8") as f:
    html_content = f.read()

soup = BeautifulSoup(html_content, 'html.parser')

# Print the text of the page
print("--- EXTRACTED DATA ---")
print(soup.get_text(separator='\n', strip=True)[:2000])

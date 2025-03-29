# podane strony nie miały możliwości bezpośredniego pobrania z nich zdjęć - trzeba by wyciągać je bezpośrednio jako adresy url z kodu html, wchodzić i dopiero zapisywać
# dlaczego więc nie napisać kodu, który wyciąga takie adresy url obrazków na serwerze, 
# wchodzi na te adresy url i dopiero stąd je pobiera, 
# a następnie zapisuje zdjęcia w folderze o nazwie ostatniego segmentu url?

import requests
from bs4 import BeautifulSoup
import os
from urllib.parse import urljoin, urlparse
import re

# Pytamy użytkownika o URL
url = input("🔗 Podaj URL strony z obrazkami: ").strip()

# Ostatni fragment ścieżki URL jako nazwę folderu
path_parts = urlparse(url).path.rstrip("/").split("/")
folder_name = path_parts[-1] if path_parts[-1] else "pobrane_obrazki"
os.makedirs(folder_name, exist_ok=True)

# Pobieramy stronę i parsujemy
response = requests.get(url)
soup = BeautifulSoup(response.text, "html.parser")
img_tags = soup.find_all("img")

# Regex do czyszczenia miniaturek typu -1024x768
pattern = re.compile(r"-\d+x\d+(?=\.jpg)")

for img in img_tags:
    src = img.get("src")
    if src and ".jpg" in src.lower():
        full_url = urljoin(url, src)
        full_url_cleaned = pattern.sub("", full_url)

        filename = os.path.join(folder_name, os.path.basename(full_url_cleaned))
        print(f"⬇️ Pobieram: {full_url_cleaned} -> {filename}")

        try:
            img_data = requests.get(full_url_cleaned).content
            with open(filename, "wb") as f:
                f.write(img_data)
        except Exception as e:
            print(f"❌ Błąd przy pobieraniu {full_url_cleaned}: {e}")


# Wyświetlam ścieżkę folderu i skryptu
script_path = os.getcwd()
full_path = os.path.abspath(folder_name)

print(f"\n📂 Skrypt działa w folderze:\n{script_path}")
print(f"✅ Wszystkie obrazy zapisane w folderze:\n{full_path}")

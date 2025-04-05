# podmiana starego + zamalowanie białym + wstawienie nowego + zamalowanie białym + wstawienie nowego
# po podaniu folderu i ścieżki nowego i starego logo
# pięknie rozpoznajesz, Py


# dopisać kroki i dlaczego takie zabiegi

import cv2
import numpy as np
from PIL import Image
import os
import unicodedata
import shutil


# 🔧 Ścieżki
template_path = r"\stare-probka.jpg" # tutaj pełny trzeba wpisać D:....
new_logo_path = r"siatki-logo.jpg" # the same


# 📁 Folder wejściowy
input_folder = input("👉 Podaj pełną ścieżkę do folderu ze zdjęciami JPG: ").strip()
output_folder = os.path.join(input_folder, "export-zmienione-logo")
os.makedirs(output_folder, exist_ok=True)

# 🔤 Funkcja: usuwanie polskich znaków z nazw jpg
def strip_polish_chars(text):
    mapping = {
        'ą': 'a', 'ć': 'c', 'ę': 'e', 'ł': 'l',
        'ń': 'n', 'ó': 'o', 'ś': 's', 'ź': 'z', 'ż': 'z',
        'Ą': 'A', 'Ć': 'C', 'Ę': 'E', 'Ł': 'L',
        'Ń': 'N', 'Ó': 'O', 'Ś': 'S', 'Ź': 'Z', 'Ż': 'Z'
    }
    return ''.join(mapping.get(c, c) for c in text)


# 📌 Wczytaj template
template = cv2.imread(template_path)
if template is None:
    raise FileNotFoundError(f"❌ Nie udało się wczytać template: {template_path}")
template_h, template_w = template.shape[:2]

# 🔁 Przetwarzanie plików
for filename in os.listdir(input_folder):
    if not filename.lower().endswith(".jpg"):
        continue

    original_filename = filename
    safe_filename = strip_polish_chars(original_filename)

    # Zamiana _ na - do finalnej nazwy eksportowej
    export_filename = original_filename.replace("_", "-")

    # Ścieżki
    full_path_original = os.path.join(input_folder, original_filename)
    full_path_safe = os.path.join(input_folder, safe_filename)

    # Jeśli potrzebna tymczasowa zamiana nazwy
    renamed = False
    if original_filename != safe_filename:
        try:
            shutil.copy2(full_path_original, full_path_safe)
            renamed = True
        except Exception as e:
            print(f"⚠️ Nie można skopiować pliku tymczasowo: {original_filename}")
            continue

    print(f"🔍 Przetwarzanie: {original_filename}")

    # Wczytaj zdjęcie
    background = cv2.imread(full_path_safe if renamed else full_path_original)
    if background is None:
        print(f"⚠️ Nie można wczytać: {original_filename}")
        if renamed:
            os.remove(full_path_safe)
        continue

    result = cv2.matchTemplate(background, template, cv2.TM_CCOEFF_NORMED)
    min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)

    # Minimalny próg dopasowania
    if max_val < 0.75:
        print(f"⚠️ Logo nie znalezione (score {max_val:.2f}) — pominięto.")
        if renamed:
            os.remove(full_path_safe)
        continue

    top_left = max_loc

    # Wczytaj nowe logo i dopasuj rozmiar do template
    new_logo = Image.open(new_logo_path).convert("RGBA").resize((template_w, template_h))

    # Konwersja do PIL
    background_rgb = cv2.cvtColor(background, cv2.COLOR_BGR2RGB)
    background_pil = Image.fromarray(background_rgb).convert("RGBA")

    # 1. Zamaluj stare logo
    white_rect = Image.new("RGBA", (template_w, template_h), (255, 255, 255, 255))
    background_pil.paste(white_rect, top_left)

    # 2. Nałóż nowe logo
    background_pil.paste(new_logo, top_left, new_logo)

    # Zapisz z oryginalną nazwą + myślniki
    export_path = os.path.join(output_folder, export_filename)
    background_pil.convert("RGB").save(export_path)
    print(f"✅ Zapisano: {export_path}")

    # Usuń tymczasowy plik jeśli był tworzony
    if renamed and os.path.exists(full_path_safe):
        os.remove(full_path_safe)

print("\n🎯 Gotowe! Polskie znaki i podkreślenia ogarnięte.")



















# podmiana starego + zamalowanie białym + wstawienie nowego + zamalowanie białym + wstawienie nowego
# po podaniu folderu i ścieżki nowego i starego logo
# pięknie rozpoznajesz, Py


# dopisać kroki i dlaczego takie zabiegi

import cv2
import numpy as np
from PIL import Image
import os

# 🔧 Ścieżki
template_path = r"\stare-probka.jpg" # tutaj pełny trzeba wpisać D:....
new_logo_path = r"siatki-logo.jpg" # the same

# 📁 Folder ze zdjęciami
input_folder = input("👉 Podaj pełną ścieżkę do folderu ze zdjęciami JPG: ").strip()
output_folder = os.path.join(input_folder, "export-zmienione-logo")
os.makedirs(output_folder, exist_ok=True)

# Template do wykrywania pozycji
template = cv2.imread(template_path)
template_h, template_w = template.shape[:2]

# 🔁 Dla każdego JPG
for filename in os.listdir(input_folder):
    if not filename.lower().endswith(".jpg"):
        continue

    full_path = os.path.join(input_folder, filename)
    print(f"🔍 Przetwarzanie: {filename}")

    background = cv2.imread(full_path)
    result = cv2.matchTemplate(background, template, cv2.TM_CCOEFF_NORMED)
    _, _, _, max_loc = cv2.minMaxLoc(result)
    top_left = max_loc

    # Wczytaj nowe logo i skaluj do template
    new_logo = Image.open(new_logo_path).convert("RGBA").resize((template_w, template_h))

    # PIL konwersja zdjęcia
    background_rgb = cv2.cvtColor(background, cv2.COLOR_BGR2RGB)
    background_pil = Image.fromarray(background_rgb).convert("RGBA")

    # Zamaluj stare logo (biały prostokąt)
    white_rect = Image.new("RGBA", (template_w, template_h), (255, 255, 255, 255))
    background_pil.paste(white_rect, top_left)

    # Nałóż nowe logo raz
    background_pil.paste(new_logo, top_left, new_logo)

    # Zapisz
    export_path = os.path.join(output_folder, filename)
    background_pil.convert("RGB").save(export_path)

    print(f"✅ Zapisano: {export_path}")

print("\n🎯 Gotowe!")

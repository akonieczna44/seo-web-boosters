# mam pobrane już zdjęcia i potrzebuję zmienić ich tytuły zgodnie z seo
# czyli tytul-zdjecia-fraza.jpg
# montaz-siatek-na-ptaki-krakow.jpg, najlepsza-fraza-kluczowa-top1.jpg

import os

# Podaj folder
folder = input("📂 Podaj ścieżkę do folderu z obrazkami: ").strip()

# Podaj nazwy zdjęć (po jednej na linię)
print("\n✏️ Wklej nowe nazwy plików:")
new_names = []
while True:
    line = input()
    if line.strip() == "":
        break
    new_names.append(line.strip())

#  Znajdź wszystkie .jpg w folderze
jpg_files = sorted([f for f in os.listdir(folder) if f.lower().endswith(".jpg")])

# Sprawdź, czy liczba nazw pasuje
if len(new_names) != len(jpg_files):
    print(f"\n❌ Liczba nazw ({len(new_names)}) nie zgadza się z liczbą plików JPG ({len(jpg_files)}).")
    exit()

# Zmieniamy nazwy
print("\n🔄 Zmieniam nazwy plików:")
for old, new in zip(jpg_files, new_names):
    old_path = os.path.join(folder, old)
    new_filename = new if new.lower().endswith(".jpg") else new + ".jpg"
    new_path = os.path.join(folder, new_filename)
    os.rename(old_path, new_path)
    print(f"✅ {old} -> {new_filename}")

print("\n🎉 Gotowe! Wszystkie pliki zostały przemianowane.")

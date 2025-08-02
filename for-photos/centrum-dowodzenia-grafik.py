# pytanko o folder z plikami do ogarnięcia
# pytanie o kolumnę z tytułami/ csv (filename, title, alt)

## jeśli podasz kolumnę z tytułami, to zmieni tylko tytuły (export do .jpg)
## jeśli podasz csv, to zmieni tytuły na nowe i wsadzi title i alty do metadanych (Title → ImageDescription, Alt → UserComment (EXIF)) (export do .jpg)
## jeśli klikniesz 2x enter, to zmieni to co jest na .webp
## jeśli wpiszesz "xxx" i enter, to zmieni rozmiar, zostawi tytuły, metadane i zrobi export do .jpg

## jeśli masz heic to zmieni go na .jpg/ webp w zależności od tego co wybierzesz

import os
import pandas as pd
import piexif
from io import StringIO
from PIL import Image
import shutil
import pillow_heif
pillow_heif.register_heif_opener()

# --- Funkcja do zmniejszania i zapisu ---
def resize_and_save(input_path, output_path, format="JPEG"):
    image = Image.open(input_path)
    width, height = image.size

    # na sztywno 2560px, żeby nie było przy skalowaniu 2599 px
    if width >= height:  # landscape lub kwadrat
        if width > 2560:
            new_width = 2560
            new_height = int(height * (2560 / width))
        else:
            new_width, new_height = width, height
    else:  # portrait
        if height > 2560:
            new_height = 2560
            new_width = int(width * (2560 / height))
        else:
            new_width, new_height = width, height

    image = image.resize((new_width, new_height), Image.LANCZOS)

    print(f"Zapisano: .../{os.path.basename(output_path)} ({new_width}x{new_height}px)")

# --- Funkcja do zmniejszania JPG przy zachowaniu metadanych ---
def resize_jpg_with_exif(input_path, output_path):
    from PIL import Image
    image = Image.open(input_path)
    exif = image.info.get('exif')  # zachowujemy oryginalne metadane

    width, height = image.size
    if max(width, height) > 2560:
        scale = 2560 / max(width, height)
        new_width = int(width * scale)
        new_height = int(height * scale)
        image = image.resize((new_width, new_height), Image.LANCZOS)
    else:
        new_width, new_height = width, height

    image.save(output_path, "JPEG", exif=exif)
    print(f"Zmniejszono JPG (z metadanymi): .../{os.path.basename(output_path)} ({new_width}x{new_height}px)")


# --- Funkcja do wstawiania metadanych w JPG, bo w webp się nie da ---
def set_jpg_metadata(file_path, title, alt):
    try:
        exif_dict = piexif.load(file_path)
        # Tytuł ---→ ImageDescription
        exif_dict['0th'][piexif.ImageIFD.ImageDescription] = title.encode('utf-8')
        # ALT ---→ UserComment
        exif_dict['Exif'][piexif.ExifIFD.UserComment] = b"ASCII\0\0\0" + alt.encode('ascii', errors='replace')
        # Zapisz zmiany
        exif_bytes = piexif.dump(exif_dict)
        piexif.insert(exif_bytes, file_path)
        print(f"✅ Metadane zapisane: {os.path.basename(file_path)}")
    except Exception as e:
        print(f"⚠️ Błąd zapisu metadanych JPG {file_path}: {e}")

# --- Pobranie danych od użytkownika ---
def get_user_mapping(folder):
    print("\n📝 Wklej CSV (filename,title,alt) lub listę nowych nazw.")
    print("Zakończ wklejanie pustym Enterem dwa razy:\n")

    lines = []
    empty_count = 0
    first_line = None

    while True:
        line = input()
        if first_line is None:
            first_line = line.strip().lower()

        # Podwójny Enter (WebP)
        if line == "":
            empty_count += 1
            if empty_count >= 2:
                break
        else:
            empty_count = 0
            lines.append(line)

    # --- Tryb "xxx" ---
    if first_line == "xxx" and len(lines) == 1:
        print("\nTryb: zmniejszanie JPG z zachowaniem metadanych, bez zmiany nazw.")
        files = sorted([f for f in os.listdir(folder) if f.lower().endswith((".jpg", ".jpeg", ".png"))])
        mapping = {}
        for f in files:
            mapping[f] = {"new_name": os.path.splitext(f)[0], "title": "", "alt": ""}
        return mapping, "resize_jpg"


    files = sorted([f for f in os.listdir(folder) if f.lower().endswith((".jpg", ".jpeg", ".png"))])

    # --- Brak CSV → tylko konwersja do WebP ---
    if len(lines) == 0:
        print("\nOkej, to zamieniam to co jest w folderze na WebP (oryginalne nazwy).")
        mapping = {}
        for f in files:
            mapping[f] = {"new_name": os.path.splitext(f)[0], "title": "", "alt": ""}
        return mapping, False

    # --- CSV lub lista ---
    csv_text = "\n".join(lines)
    df = pd.read_csv(StringIO(csv_text), header=None)

    mapping = {}

    if df.shape[1] == 1:
        # tylko nazwy (bez metadanych)
        for old, new_name in zip(files, df[0]):
            new_name = str(new_name).strip()
            if new_name.lower().endswith(".jpg"):
                new_name = os.path.splitext(new_name)[0]
            mapping[old] = {"new_name": new_name, "title": "", "alt": ""}
        return mapping, False
    elif df.shape[1] >= 3:
        # filename (docelowa), title, alt -> mapujemy po kolei
        if len(df) != len(files):
            print(f"⚠️ Uwaga: liczba plików ({len(files)}) różni się od liczby rekordów w CSV ({len(df)})!")
        for old, (new_name, title, alt) in zip(files, df.itertuples(index=False, name=None)):
            new_name = str(new_name).strip()
            if new_name.lower().endswith(".jpg"):
                new_name = os.path.splitext(new_name)[0]
            mapping[old] = {"new_name": new_name, "title": str(title), "alt": str(alt)}
        return mapping, True
    else:
        print("❌ Zły format CSV, przerwano.")
        exit()

# --- Główna logika ---
def process_images(folder, mapping, with_metadata):
    if with_metadata:
        output_folder = os.path.join(folder, "jpg z meta do portfolio")
        os.makedirs(output_folder, exist_ok=True)
        for old_name, info in mapping.items():
            old_path = os.path.join(folder, old_name)
            if not os.path.isfile(old_path):
                print(f"❌ Brak pliku: {old_name}")
                continue

            new_jpg_path = os.path.join(output_folder, info['new_name'] + ".jpg")
            # Zmniejszamy i zapisujemy jako nowy JPG
            resize_and_save(old_path, new_jpg_path, format="JPEG")
            # Ustawiamy metadane na nowym pliku
            set_jpg_metadata(new_jpg_path, info['title'], info['alt'])

    else:
        output_folder = os.path.join(folder, "webp do portfolio")
        os.makedirs(output_folder, exist_ok=True)
        for old_name, info in mapping.items():
            old_path = os.path.join(folder, old_name)
            if not os.path.isfile(old_path):
                print(f"❌ Brak pliku: {old_name}")
                continue

            new_webp_path = os.path.join(output_folder, info['new_name'] + ".webp")
            resize_and_save(old_path, new_webp_path, format="WEBP")

    print("\n🎉 Gotowe!")

if __name__ == "__main__":
    folder = input("📁 Podaj ścieżkę do folderu ze zdjęciami: ").strip()
    if not os.path.isdir(folder):
        print("❌ Folder nie istnieje!")
        exit()

    mode = None
    mapping, mode = get_user_mapping(folder)

    if mode == "resize_jpg":
        output_folder = os.path.join(folder, "jpg do portfolio")
        os.makedirs(output_folder, exist_ok=True)
        for old_name in mapping:
            old_path = os.path.join(folder, old_name)
            new_jpg_path = os.path.join(output_folder, old_name)
            resize_jpg_with_exif(old_path, new_jpg_path)
        print("\n🎉 Gotowe (zmniejszone JPG z zachowanymi metadanymi)!")
    elif mode is True:
        process_images(folder, mapping, with_metadata=True)
    else:
        process_images(folder, mapping, with_metadata=False)

# sprawdza rozmiar dłuższego boku
# zamienia go na 3000 px max
# skaluje to adekwatnie, wiadomo
# zapisuje w folderze nowym "do portfolio", żeby nie zmieniać oryginałów i do testów
# zmienia rozszerzenie na .webp

from PIL import Image
import os

def convert_to_webp(input_path, output_path):
    # Wczytaj obraz
    image = Image.open(input_path)
    width, height = image.size

    # Skalowanie jeśli dłuższy bok > 3000 px
    if max(width, height) > 3000:
        scale = 3000 / max(width, height)
        new_width = int(width * scale)
        new_height = int(height * scale)
        image = image.resize((new_width, new_height), Image.LANCZOS)
    else:
        new_width, new_height = width, height

    # Zapis do WEBP
    image.save(output_path, 'WEBP', quality=80)

    # Rozmiar pliku w MB
    file_size_mb = os.path.getsize(output_path) / (1024 * 1024)

    # Nazwa pliku do wyświetlenia
    filename = os.path.basename(output_path)
    print(f"Zapisano: .../{filename} ({new_width}x{new_height}px) {file_size_mb:.2f} MB")

def batch_convert_to_webp(input_folder):
    # folder wynikowy w tym samym miejscu
    output_folder_path = os.path.join(input_folder, "webp do portfolio")
    os.makedirs(output_folder_path, exist_ok=True)

    for filename in os.listdir(input_folder):
        if filename.lower().endswith((".jpg", ".jpeg", ".png")):
            input_path = os.path.join(input_folder, filename)
            output_path = os.path.join(output_folder_path, os.path.splitext(filename)[0] + ".webp")
            convert_to_webp(input_path, output_path)

# --- pytanie o ścieżkę ---
input_folder = input("Podaj ścieżkę do folderu z obrazami: ").strip('"')
batch_convert_to_webp(input_folder)

print("\nFinito!")


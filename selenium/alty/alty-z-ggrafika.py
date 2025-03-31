from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys
from webdriver_manager.chrome import ChromeDriverManager
import time
import pandas as pd

# otworz chrome, zaakceptuj ciasteczka, wpisz podana fraze, pobiera tytuly i alty top10 grafik - ale nie wyszukuje ich dobrze po miejscu, wiec nie zwraca wynikow

# Konfiguracja przeglądarki
options = Options()
options.add_argument("--start-maximized")
driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

fraza = input("Wpisz frazę do wyszukania w Google Grafika: ")
url = f"https://www.google.com/search?tbm=isch&q={fraza.replace(' ', '+')}"
driver.get(url)
time.sleep(3)

# Kliknij „Zaakceptuj wszystko” jeśli trzeba
try:
    accept_button = driver.find_element(By.XPATH, "//div[contains(text(), 'Zaakceptuj wszystko') or contains(text(), 'Akceptuję')]")
    accept_button.click()
    print("✅ Kliknięto 'Zaakceptuj wszystko'")
    time.sleep(2)
except:
    print("ℹ️ Brak zgody na ciasteczka")

# Scrollowanie żeby załadować więcej miniatur
for _ in range(3):
    driver.find_element(By.TAG_NAME, "body").send_keys(Keys.END)
    time.sleep(2)

# Szukamy miniaturek do kliknięcia
thumbnails = driver.find_elements(By.CSS_SELECTOR, 'img[jsname="Q4LuWd"]')
print(f"🔎 Znaleziono {len(thumbnails)} miniatur")

data = []

for i, thumb in enumerate(thumbnails[:10]):
    try:
        ActionChains(driver).move_to_element(thumb).click().perform()
        time.sleep(2)

        # Szukamy dużych obrazków
        images = driver.find_elements(By.CSS_SELECTOR, 'img.n3VNCb')
        for image in images:
            src = image.get_attribute("src")
            if src and src.startswith("http"):
                alt = thumb.get_attribute("alt")
                data.append({
                    "alt": alt,
                    "src": src,
                    "filename": src.split("/")[-1].split("?")[0]
                })
                print(f"✅ ({i+1}) ALT: {alt}")
                break  # tylko pierwszy poprawny
    except Exception as e:
        print(f"⚠️ Miniatura {i+1} błąd: {e}")

driver.quit()

# Wyniki
df = pd.DataFrame(data)
print(df)

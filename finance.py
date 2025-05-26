import threading
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager
import time

# === Настройки ===
symbols = ['AAPL', 'META', 'GOOGL', 'MSFT']

# Укажите корректный путь к chrome.exe
CHROME_BINARY_PATH = r"C:\Program Files\Google\Chrome\Application\chrome.exe"  # Windows
# CHROME_BINARY_PATH = "/usr/bin/google-chrome-stable"  # Linux
# CHROME_BINARY_PATH = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"  # macOS

# === Класс Stock - поток для получения цены акции ===
class Stock(threading.Thread):
    def __init__(self, symbol):
        super().__init__()
        self.symbol = symbol
        self.url = f'https://finance.yahoo.com/quote/ {symbol}'
        self.price = None

    def run(self):
        # Настройки браузера
        chrome_options = Options()
        chrome_options.add_argument('--headless=new')  # фоновый режим
        chrome_options.add_argument('--disable-gpu')
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        chrome_options.add_argument('--window-size=1920,1080')
        chrome_options.binary_location = CHROME_BINARY_PATH  # важно!

        # Обход защиты от автоматизации
        chrome_options.add_argument('--disable-blink-features=AutomationControlled')
        chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
        chrome_options.add_experimental_option("useAutomationExtension", False)

        try:
            driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)
            driver.execute_cdp_cmd("Page.addScriptToEvaluateOnNewDocument", {
                "source": """
                    Object.defineProperty(navigator, 'webdriver', {
                      get: () => undefined
                    })
                  """
            })

            print(f"[{self.symbol}] Открываем: {self.url}")
            driver.get(self.url)
            time.sleep(5)  # ждём загрузки JS

            price_element = driver.find_element(
                By.CSS_SELECTOR,
                f'fin-streamer[data-symbol="{self.symbol}"][data-field="regularMarketPrice"]'
            )
            self.price = float(price_element.text.replace(',', ''))
            print(f"[{self.symbol}] Цена: {self.price}")

        except Exception as e:
            print(f"[{self.symbol}] Ошибка: {e}")
        finally:
            try:
                driver.quit()
            except:
                pass

    def __str__(self):
        return f'{self.symbol.ljust(6)}\t{self.price if self.price is not None else "N/A"}'

# === Основной блок запуска ===
if __name__ == "__main__":
    threads = []

    for symbol in symbols:
        t = Stock(symbol)
        t.start()
        threads.append(t)
        time.sleep(3)

    for t in threads:
        t.join()

    print("\n✅ Результаты:")
    for t in threads:
        print(t)
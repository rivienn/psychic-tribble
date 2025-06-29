import csv
import os
import time
import asyncio
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


class DeveloperScraper:
    """ПАРСИНГ САЙТОВ ЗАСТРОЙЩИКОВ (асинхронно через asyncio.to_thread)"""

    def __init__(self):
        # Конфиг с URL-ами
        self.config = {
            "Dogma": {
                "residential": ["https://dogma.ru/kvartiry"],
                "commercial": ["https://dogma.ru/commerce"]
            },
            "Avadom": {
                "residential": ["https://avadom.ru/objects/"],
                "commercial": ["https://avadom.ru/commercial/"]
            },
            "SSK": {
                "residential": ["https://sskuban.ru/complexes"],
                "commercial": ["https://sskuban.ru/commercial"]
            },
            "Family-Yug": {
                "residential": ["https://family-yug.ru/novostroyki/"],
                "commercial": []
            },
            "Bel Development": {
                "residential": [
                    "https://www.beldevelopment.ru/projects/territoriya-green-apple",
                    "https://www.beldevelopment.ru/projects/biznes-tsentr-на-rashpilevskoy",
                    "https://www.beldevelopment.ru/projects/fok-trud"
                ],
                "commercial": []
            }
        }
        self.output_dir = "./data/real_estate"
        self.output_file = os.path.join(self.output_dir, "objects.csv")
        self.fields = [
            "developer", "project_name", "property_type",
            "rooms", "area_sqm", "floor",
            "price", "price_per_sqm",
            "year", "address", "description"
        ]

    @staticmethod
    # Запуск драйвра
    def create_driver():
        options = Options()
        options.add_argument("--headless")
        options.add_argument("--disable-gpu")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument(
            "user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        )
        return webdriver.Chrome(options=options)

    @staticmethod
    # Закртыие рекламы
    def close_popups(driver):
        for sel in ('[aria-label="Close"]', '.modal-close', '.cookie-banner__close'):
            for el in driver.find_elements(By.CSS_SELECTOR, sel):
                try:
                    el.click()
                    time.sleep(0.5)
                except:
                    pass

    @staticmethod
    # Прокрутка страницы
    def scroll_page(driver, pause: float = 1.0):
        last_height = driver.execute_script("return document.body.scrollHeight")
        while True:
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(pause)
            new_height = driver.execute_script("return document.body.scrollHeight")
            if new_height == last_height:
                break
            last_height = new_height

    def build_item(self, developer, project_name, property_type, **kwargs):
        item = {f: None for f in self.fields}
        item.update({
            "developer": developer,
            "project_name": project_name,
            "property_type": property_type
        })
        item.update(kwargs)
        return item

    # Догма
    def parse_dogma(self):
        driver = self.create_driver();
        data = [];
        dev = "Dogma"
        try:
            for url in self.config[dev]["residential"]:
                driver.get(url)
                WebDriverWait(driver, 10).until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, ".project-card")))
                self.close_popups(driver)
                self.scroll_page(driver)
                for card in driver.find_elements(By.CSS_SELECTOR, ".project-card"):
                    name = card.find_element(By.CSS_SELECTOR, ".project-card__title").text
                    price = card.find_element(By.CSS_SELECTOR, ".project-card__price").text.replace("₽", "").strip()
                    data.append(self.build_item(dev, name, "жк", price=price))
            for url in self.config[dev]["commercial"]:
                driver.get(url)
                WebDriverWait(driver, 10).until(
                    EC.presence_of_all_elements_located((By.CSS_SELECTOR, ".commerce-card")))
                self.close_popups(driver)
                for card in driver.find_elements(By.CSS_SELECTOR, ".commerce-card"):
                    name = card.find_element(By.CSS_SELECTOR, ".commerce-card__title").text
                    price = card.find_element(By.CSS_SELECTOR, ".commerce-card__price").text.replace("₽", "").strip()
                    data.append(self.build_item(dev, name, "ком", price=price))
        finally:
            driver.quit()
        return data

    # Ава
    def parse_avadom(self):
        driver = self.create_driver();
        data = [];
        dev = "Avadom"
        try:
            for url in self.config[dev]["residential"]:
                driver.get(url)
                WebDriverWait(driver, 10).until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, ".object-item")))
                self.close_popups(driver)
                for itm in driver.find_elements(By.CSS_SELECTOR, ".object-item"):
                    name = itm.find_element(By.CSS_SELECTOR, ".object-item__name").text
                    area = itm.find_element(By.CSS_SELECTOR, ".object-item__area").text
                    data.append(self.build_item(dev, name, "жк", area_sqm=area))
            for url in self.config[dev]["commercial"]:
                driver.get(url)
                WebDriverWait(driver, 10).until(
                    EC.presence_of_all_elements_located((By.CSS_SELECTOR, ".commercial-item")))
                self.close_popups(driver)
                for itm in driver.find_elements(By.CSS_SELECTOR, ".commercial-item"):
                    name = itm.find_element(By.CSS_SELECTOR, ".commercial-item__name").text
                    desc = itm.find_element(By.CSS_SELECTOR, ".commercial-item__desc").text
                    data.append(self.build_item(dev, name, "ком", description=desc))
        finally:
            driver.quit()
        return data

    # ССК
    def parse_ssk(self):
        driver = self.create_driver();
        data = [];
        dev = "SSK"
        try:
            for url in self.config[dev]["residential"]:
                driver.get(url)
                WebDriverWait(driver, 10).until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, ".complex-card")))
                self.close_popups(driver)
                for c in driver.find_elements(By.CSS_SELECTOR, ".complex-card"):
                    name = c.find_element(By.CSS_SELECTOR, ".complex-card__name").text
                    year = c.find_element(By.CSS_SELECTOR, ".complex-card__year").text
                    data.append(self.build_item(dev, name, "жк", year=year))
            for url in self.config[dev]["commercial"]:
                driver.get(url)
                WebDriverWait(driver, 10).until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, ".biz-card")))
                self.close_popups(driver)
                for b in driver.find_elements(By.CSS_SELECTOR, ".biz-card"):
                    name = b.find_element(By.CSS_SELECTOR, ".biz-card__title").text
                    data.append(self.build_item(dev, name, "ком"))
        finally:
            driver.quit()
        return data

    # Семья
    def parse_family_yug(self):
        driver = self.create_driver();
        data = [];
        dev = "Family-Yug"
        try:
            driver.get(self.config[dev]["residential"][0])
            WebDriverWait(driver, 10).until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, ".novostroyka-item")))
            self.close_popups(driver)
            for n in driver.find_elements(By.CSS_SELECTOR, ".novostroyka-item"):
                name = n.find_element(By.CSS_SELECTOR, ".novostroyka-item__title").text
                rooms = n.find_element(By.CSS_SELECTOR, ".novostroyka-item__rooms").text
                address = n.find_element(By.CSS_SELECTOR, ".novostroyka-item__address").text
                data.append(self.build_item(dev, name, "жк", rooms=rooms, address=address))
        finally:
            driver.quit()
        return data

    # Бэл
    def parse_bel_development(self):
        driver = self.create_driver();
        data = [];
        dev = "Bel Development"
        try:
            for url in self.config[dev]["residential"]:
                driver.get(url)
                WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CSS_SELECTOR, ".project-header")))
                self.close_popups(driver)
                title = driver.find_element(By.CSS_SELECTOR, ".project-header__title").text
                price = driver.find_element(By.CSS_SELECTOR, ".project-info__price").text
                data.append(self.build_item(dev, title, "жк", price=price))
        finally:
            driver.quit()
        return data

    async def scrape(self):
        os.makedirs(self.output_dir, exist_ok=True)
        tasks = [
            asyncio.create_task(asyncio.to_thread(self.parse_dogma)),
            asyncio.create_task(asyncio.to_thread(self.parse_avadom)),
            asyncio.create_task(asyncio.to_thread(self.parse_ssk)),
            asyncio.create_task(asyncio.to_thread(self.parse_family_yug)),
            asyncio.create_task(asyncio.to_thread(self.parse_bel_development)),
        ]
        results = await asyncio.gather(*tasks)
        all_data = [item for sub in results for item in sub]
        with open(self.output_file, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=self.fields)
            writer.writeheader()
            writer.writerows(all_data)

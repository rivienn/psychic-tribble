import re
import time
import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from concurrent.futures import ThreadPoolExecutor
from scraping.scr_config import ScrapersConfig


class AvitoParser:
    """ПАРСИНГ СТРАНИЦ C AVITO"""

    def __init__(self, config: ScrapersConfig):
        self.urls = config.developer_urls
        self.output_file = config.output_file

    @staticmethod
    def create_headless_driver():
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
    def scroll_page(driver):
        last_h = driver.execute_script("return document.body.scrollHeight")
        while True:
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(1)
            new_h = driver.execute_script("return document.body.scrollHeight")
            if new_h == last_h:
                break
            last_h = new_h
        driver.execute_script("window.scrollTo(0, 0);")
        time.sleep(1)

    def parse_one(self, url):
        driver = self.create_headless_driver()
        try:
            driver.get(url)
            self.scroll_page(driver)

            name_el = driver.find_element(By.CSS_SELECTOR,
                                          "h4.EEPdn.T7ujv.IKawI.SPIVg.p964m.Ms35a.P1HOd.cujIu.UzLWZ")
            name = name_el.text.strip()

            p = driver.find_element(By.CSS_SELECTOR,
                                    "p.T7ujv.Tdsqf.dsi88.cujIu.aStJv.Gw0o7.M5bdx.pFEn3.Qizeb").text
            year_match = re.search(r"(\d{4})", p)
            est_year = int(year_match.group(1)) if year_match else None

            h1 = driver.find_element(By.XPATH,
                                     "//div[starts-with(@class,'//div[contains(@class,'grid')]]"
                                     )
            passed_text = driver.find_elements(By.CSS_SELECTOR,
                                               "h3.EEPdn.T7ujv.IKawI.SPIVg.U3sqP.p964m.R42AR.P1HOd.cujIu.UzLWZ")[0].text
            hp, lp = map(int, re.findall(r"(\d+)", passed_text))

            const_text = driver.find_elements(By.CSS_SELECTOR,
                                              "h3.EEPdn.T7ujv.IKawI.SPIVg.U3sqP.p964m.R42AR.P1HOd.cujIu.UzLWZ")[1].text
            hc, lc = map(int, re.findall(r"(\d+)", const_text))

            tp_text = driver.find_element(By.CSS_SELECTOR,
                                          "h3.EEPdn.T7ujv.FfCOp.OIvE4.BX2kt.pYHWV.R42AR.P1HOd.cujIu.b005q.Gw0o7.huYxK.pFEn3.Qizeb"
                                          ).text
            tp = int(tp_text.replace("%", ""))

            return {
                "url": url,
                "name": name,
                "est_year": est_year,
                "houses_passed": hp,
                "lcd_passed": lp,
                "houses_const": hc,
                "lcd_const": lc,
                "transfers_percent": tp
            }
        finally:
            driver.quit()

    def run(self):
        records = []
        with ThreadPoolExecutor(max_workers=4) as ex:
            futures = [ex.submit(self.parse_one, url) for url in self.urls]
            for f in futures:
                try:
                    rec = f.result(timeout=60)
                    records.append(rec)
                except Exception as e:
                    print(f"Error parsing {f}: {e}")

        df = pd.DataFrame(records,
                          columns=[
                              "url", "name", "est_year",
                              "houses_passed", "lcd_passed",
                              "houses_const", "lcd_const",
                              "transfers_percent"
                          ])
        df.to_csv(self.output_file, index=False, encoding="utf-8")
        return df

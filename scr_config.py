import os
import json


class ScrapersConfig:
    """КОНФИГУРАЦИЯ ДЛЯ ЗАСТРОЙЩИКОВ"""

    CONFIG_DIR = "./scraping"
    CONFIG_FILE = os.path.join(CONFIG_DIR, "settings.json")

    def __init__(self):
        os.makedirs(self.CONFIG_DIR, exist_ok=True)
        self.load_config()

    def load_config(self):
        if os.path.exists(self.CONFIG_FILE):
            with open(self.CONFIG_FILE, "r", encoding="utf-8") as f:
                cfg = json.load(f)
        else:
            cfg = self.default_config()
            self.save_config(cfg)

        # Список URL застройщиков
        self.developer_urls = cfg["developer_urls"]

        # Путь к итоговому csv
        self.output_dir = cfg["output_dir"]
        self.output_file = os.path.join(self.output_dir, cfg["output_file"])
        os.makedirs(self.output_dir, exist_ok=True)

    def save_config(self, cfg):
        with open(self.CONFIG_FILE, "w", encoding="utf-8") as f:
            json.dump(cfg, f, indent=4, ensure_ascii=False)

    @staticmethod
    def default_config():
        return {
            "developer_urls": [
                "https://www.avito.ru/catalog/zastrojshiki/bauinvest/23162-ASgBAgICA0TQvA7~m9EBypQTkOLfEcyUE5ji3xE",
                "https://www.avito.ru/catalog/zastrojshiki/sz_partner_invest_kuban/22064-ASgBAgICA0TQvA7~m9EBypQT5MjfEcyUE~7I3xE",
                "https://www.avito.ru/catalog/zastrojshiki/metriks_develorment/19145-ASgBAgICA0TQvA7~m9EBypQTwIvfEcyUE8qL3xE",
                "https://www.avito.ru/catalog/zastrojshiki/sz_kontinent/614892-ASgBAgICA0TQvA7~m9EBypQTuqLgEcyUE8a1hRU",
                "https://www.avito.ru/catalog/zastrojshiki/sz_rut/21393-ASgBAgICA0TQvA7~m9EBypQTgL7fEcyUE4i~3xE",
                "https://www.avito.ru/catalog/zastrojshiki/romeks-kuban/19686-ASgBAgICA0TQvA7~m9EBypQTzIPfEcyUE9SD3xE",
                "https://www.avito.ru/catalog/zastrojshiki/nvm/729794-ASgBAgICA0TQvA7~m9EBypQTtpaLFcyUE7iWixU",
                "https://www.avito.ru/catalog/zastrojshiki/stroygrad/19541-ASgBAgICA0TQvA7~m9EBypQT2o7fEcyUE8yV3xE",
                "https://www.avito.ru/catalog/zastrojshiki/alfastroyinvest/19296-ASgBAgICA0TQvA7~m9EBypQTtJLfEcyUE8KS3xE",
                "https://www.avito.ru/catalog/zastrojshiki/sz_flagman/20608-ASgBAgICA0TQvA7~m9EBypQT7KjfEcyUE_yo3xE",
                "https://www.avito.ru/catalog/zastrojshiki/sredastroy/1012850-ASgBAgICA0TQvA7~m9EBypQTiNGrFcyUE4rRqxU",
                "https://www.avito.ru/catalog/zastrojshiki/vkb-novostroyki/159387-ASgBAgICA0TQvA7~m9EBypQTnqvtEcyUE6Cr7RE",
                "https://www.avito.ru/catalog/zastrojshiki/yug-inzhiniring/19390-ASgBAgICA0TQvA7~m9EBypQTqJHfEcyUE7SR3xE",
                "https://www.avito.ru/catalog/zastrojshiki/yugstroyinvest/18735-ASgBAgICA0TQvA7~m9EBypQTmIDfEcyUE6KA3xE"
            ],
            "association_urls": [
                "https://www.avito.ru/catalog/zastrojshiki/semya/19819-ASgBAgICA0TQvA7~m9EBypQTkpXfEcyUE8Ke3xE",
                "https://www.avito.ru/catalog/zastrojshiki/afk/20893-ASgBAgICA0TQvA7~m9EBypQT4LPfEcyUE~Sz3xE",
                "https://www.avito.ru/catalog/zastrojshiki/development-yug/19386-ASgBAgICA0TQvA7~m9EBypQTsJLfEcyUE7yS3xE",
                "https://www.avito.ru/catalog/zastrojshiki/art_group/21640-ASgBAgICA0TQvA7~m9EBypQT9qjmEcyUE8S73xE",
                "https://www.avito.ru/catalog/zastrojshiki/evropeya/20784-ASgBAgICA0TQvA7~m9EBypQTirDfEcyUE5iw3xE",
                "https://www.avito.ru/catalog/zastrojshiki/lendeks/423451-ASgBAgICA0TQvA7~m9EBypQT6LiCFcyUE~q4ghU",
                "https://www.avito.ru/catalog/zastrojshiki/sochioylstroy/23165-ASgBAgICA0TQvA7~m9EBypQT8t_fEcyUE_rf3xE",
                "https://www.avito.ru/catalog/zastrojshiki/ava_group/19207-ASgBAgICA0TQvA7~m9EBypQT6o_fEcyUE_SP3xE",
                "https://www.avito.ru/catalog/zastrojshiki/tochno/20180-ASgBAgICA0TQvA7~m9EBypQTqqffEcyUE7qn3xE",
                "https://www.avito.ru/catalog/zastrojshiki/ssk/18858-ASgBAgICA0TQvA7~m9EBypQT6rWCFcyUE9iF3xE"
            ],
            "output_dir": "./data/company",
            "output_file": "developers.csv",
            "association_file": "association.csv"
        }

    def set_config(self, developer_urls, output_dir, output_file, association_urls=None, association_file=None):
        cfg = {
            "developer_urls": developer_urls,
            "output_dir": output_dir,
            "output_file": output_file,
            "association_urls": association_urls or [],
            "association_file": association_file or "association.csv"
        }
        self.save_config(cfg)
        self.load_config()

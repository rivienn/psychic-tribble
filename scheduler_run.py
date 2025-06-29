import os
import time
import asyncio
import schedule
import functools

from scraping.scr_base import AvitoParser
from scraping.scr_net import DeveloperScraper
from scraping.scr_config import ScrapersConfig
from scraping.slider_captcha import AntiCaptchaSolver


class ParserScheduler:
    """ПЛАНИРОВЩИК ЗАПУСКА"""

    def __init__(self):
        self.schedule = schedule
        self.config = ScrapersConfig()
        self.scraper = DeveloperScraper()
        # self.avito = AvitoParser()
        # self.captcha = AntiCaptchaSolver()

    def data_exists(self) -> bool:
        return os.path.exists(self.config.output_file)

    @staticmethod
    def log_execution(message: str):
        def decorator(func):
            @functools.wraps(func)
            def wrapper(*args, **kwargs):
                print(f"{time.strftime('%Y-%m-%d %H:%M:%S')} — {message}...")
                return func(*args, **kwargs)
            return wrapper
        return decorator

    @log_execution("Запуск парсинга недвижимости")
    def run_parsing(self):
        if self.data_exists():
            print(f"Файл {self.config.output_file} уже обновлен!")
            return

        asyncio.run(self.scraper.scrape())
        print(f"Результаты сохранены в {self.config.output_file}.")

    def setup_schedule(self):
        if self.data_exists():
            print(f"[Scheduler] {self.config.output_file} уже запущен.")
            return

        run_time = "06:00"
        self.schedule.every().day.at(run_time).do(self.run_parsing)
        print(f"[Scheduler]  запуск запланирован на {run_time}.")

    def start(self):
        print("=== Запуск планировщика DeveloperScraper ===")
        if not self.schedule.jobs:
            print("Нет задач в расписании. Проверьте setup_schedule().")
            return

        print(f"Ожидание... следующий запуск в {self.schedule.jobs[0].next_run.strftime('%Y-%m-%d %H:%M:%S')}")
        try:
            while True:
                self.schedule.run_pending()
                time.sleep(1)
        except KeyboardInterrupt:
            print("Планировщик остановлен вручную.")


# from scraping import ParserScheduler
# # Запуск
# if __name__ == "__main__":
#     scheduler = ParserScheduler()
#     scheduler.setup_schedule()
#     scheduler.start()

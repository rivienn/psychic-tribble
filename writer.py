import urllib3
import requests
from config import BDConfig


urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


class HTTPtWriter:
    """ML-RESULT ENDPOINT"""
    def __init__(self, config: BDConfig = None):
        self.cfg = config or BDConfig()
        self.post_url = getattr(self.cfg, "post_url", None)

    # Отправка результата ML-модели на сервер
    def send_csv(self, csv_path: str) -> requests.Response:
        with open(csv_path, "rb") as f:
            files = {"file": (csv_path, f, "text/csv")}
            resp = requests.post(self.post_url, files=files, verify=False)
        resp.raise_for_status()
        return resp

# from writer import HTTPtWriter
# # Запуск
# if __name__ == "__main__":
#     writer = HTTPtWriter(config=BDConfig())
#     response = writer.send_csv(BDConfig().output_csv)
#     print("Статус отправки:", response.status_code)
#     print("Ответ сервера:", response.text)

import cv2
import time
import requests
import numpy as np
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver import ActionChains


class AntiCaptchaSolver:
    """РЕШЕНИЕ GETTEST КАПЧИ + OPEN CV"""

    def __init__(self, driver: webdriver.Chrome):
        self.driver = driver
        self.action = ActionChains(driver)

    # Рисунок
    def _download_image(self, url: str) -> np.ndarray:
        resp = requests.get(url)
        img_arr = np.frombuffer(resp.content, np.uint8)
        return cv2.imdecode(img_arr, cv2.IMREAD_COLOR)

    # Метод matchTemplate X-смещение
    def _find_slider_offset(self, bg_img: np.ndarray, piece_img: np.ndarray) -> int:
        result = cv2.matchTemplate(bg_img, piece_img, cv2.TM_CCOEFF_NORMED)
        _, _, _, max_loc = cv2.minMaxLoc(result)
        return max_loc[0]

    # Слайдер капчи
    def solve_slider(self):
        time.sleep(2)

        bg_elem = self.driver.find_element(By.CSS_SELECTOR, ".geetest_canvas_bg")
        bg_url = bg_elem.get_attribute("src")
        bg_img = self._download_image(bg_url)

        piece_elem = self.driver.find_element(By.CSS_SELECTOR, ".geetest_canvas_slice")
        piece_url = piece_elem.get_attribute("src")
        piece_img = self._download_image(piece_url)

        offset = self._find_slider_offset(bg_img, piece_img)
        print(f"Расчет пикселей: {offset}px")

        slider = self.driver.find_element(By.CSS_SELECTOR, ".geetest_slider_button")
        self.action.click_and_hold(slider).perform()
        move_track = self._generate_move_track(offset)
        for dx in move_track:
            self.action.move_by_offset(dx, 0).perform()
            time.sleep(0.02)
        self.action.release().perform()

        time.sleep(2)

    # Генерируем шаги для расчёта дситации
    def _generate_move_track(self, distance: int) -> list[int]:
        track = []
        current = 0
        mid = distance * 0.6
        t = 0.2
        v = 0
        while current < distance:
            if current < mid:
                a = 2.0     # ускорение
            else:
                a = -3.0    # замедление
            v0 = v
            v = v0 + a * t
            move = v0 * t + 0.5 * a * (t ** 2)
            move = max(1, round(move))
            current += move
            track.append(move)
        overshoot = current - distance
        if overshoot > 0:
            track.append(-overshoot)
        return track

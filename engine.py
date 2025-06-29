import os
from config import BDConfig
from sqlalchemy import create_engine
from sqlalchemy.pool import QueuePool


class AdaptivePool(QueuePool):
    """МОДУЛЬ ПЕРЕОПРЕДЕЛЕНИЯ ЛОГИКИ ПОЛУЧЕНИЯ/ВОЗВРАТА СОЕДИНЕНИЙ"""

    def __init__(self, creator, pool_size, max_overflow,
                 high_water=0.8, low_water=0.3, adjust_step=2, **kwargs):
        super().__init__(creator, pool_size=pool_size,
                         max_overflow=max_overflow, **kwargs)
        self.high_water = high_water
        self.low_water = low_water
        self.adjust_step = adjust_step

    # Рейтинг достпности
    def status_ratio(self):
        checked_out = self.checkedout()
        return checked_out / float(self._pool.maxsize)

    # Динамический расчёт max_overflow
    def _do_get(self):
        ratio = self.status_ratio()
        if ratio > self.high_water:
            self._max_overflow += self.adjust_step
        elif ratio < self.low_water and self._max_overflow >= self.adjust_step:
            self._max_overflow -= self.adjust_step
        return super()._do_get()


class DBEngineFactory:
    """SQLAlchemy С ПУЛОМ СОЕДИНЕНИЙ"""

    def __init__(self, config: BDConfig = None, env_var: str = "DB_URL"):
        self.cfg = config or BDConfig()
        self.env_var = env_var

    # Точка входа движка
    def get_engine(self):
        db_url = os.getenv(self.env_var) or (f"postgresql+psycopg2://"
                                             f"{self.cfg.db_user}:{self.cfg.db_password}@"
                                             f"{self.cfg.db_host}:{self.cfg.db_port}/"
                                             f"{self.cfg.db_name}")
        return create_engine(db_url,
                             poolclass=AdaptivePool,
                             pool_size=5,
                             max_overflow=10,
                             pool_timeout=10,
                             pool_pre_ping=True)  # echo=True - лог SQL-запросов


# # Запуск
# if __name__ == "__main__":
#     db_connector = DBEngineFactory()
#     raw = db_connector.get_engine()

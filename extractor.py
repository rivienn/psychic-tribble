import pandas as pd
from config import BDConfig
from sqlalchemy import text
from typing import Union, Sequence
from db_connector.engine import DBEngineFactory


class SQLExtractor:
    """ИМПРОТ СЫРЫХ ДАННЫХ ИЗ БД"""

    def __init__(self, config: BDConfig = None):
        self.cfg = config or BDConfig()
        self.engine = DBEngineFactory(config=self.cfg).get_engine()

    # Отправка SQL-запроса
    @staticmethod
    def run_query(engine, sql: str) -> pd.DataFrame:
        with engine.connect() as conn:
            return pd.read_sql(text(sql), conn)

    # Слияние схем-таблиц
    @staticmethod
    def smart_merge(*dfs, on: Union[str, Sequence[str]], how: str = "left") -> pd.DataFrame:
        keys = [on] if isinstance(on, str) else list(on)
        result = dfs[0]
        for df in dfs[1:]:
            overlap = set(result.columns) & set(df.columns) - set(keys)
            cols = keys + [c for c in df.columns if c not in overlap and c not in keys]
            result = result.merge(df[cols], on=keys, how=how)
        return result

    # Основная функция
    def extract_sql(self):
        df1 = self.run_query(self.engine, "SELECT * FROM data_train ")
        df2 = self.run_query(self.engine, "SELECT * FROM data_test")
        df1.to_csv(self.cfg.train_raw, index=False)
        df2.to_csv(self.cfg.test_raw, index=False)
        return df1, df2

# from extractor import SQLExtractor
# # Запуск
# if __name__ == "__main__":
#     db_connector = SQLExtractor()
#     raw = db_connector.extract_sql()

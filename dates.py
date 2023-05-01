import pandas as pd

from datetime import datetime


class DateOperations:
    
    MONTHS_DICT = {
        1:  "Janeiro",
        2:  "Fevereiro",
        3:  "Março",
        4:  "Abril",
        5:  "Maio",
        6:  "Junho",
        7:  "Julho",
        8:  "Agosto",
        9:  "Setembro",
        10: "Outubro",
        11: "Novembro",
        12: "Dezembro",
    }

    MONTHS_LIST = list(MONTHS_DICT.values())

    @staticmethod
    def get_month_index_from_string(month: str) -> int:
        return DateOperations.MONTHS_LIST.index(month) + 1

    @staticmethod
    def get_month_string_from_index(month: int) -> str:
        return DateOperations.MONTHS_DICT.get(month)

    @staticmethod
    def convert_values_to_datetime(year: int, month: int, day=1) -> datetime:
        return datetime(year, month, day)

    @staticmethod
    def get_dataframe_from_dates(df: pd.DataFrame, date_column: str, initial_date: datetime, final_date: datetime) -> pd.DataFrame:
        return df.loc[(df[date_column] >= initial_date) & (df[date_column] <= final_date)]

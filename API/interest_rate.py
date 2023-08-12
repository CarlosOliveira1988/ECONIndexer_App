"""Script used to perform some calculation related to Interest Values and Rates."""

import pandas as pd


class InterestCalculation:
    
    NONE_RATE = "Nenhuma"
    PREFIXED_RATE = "Préfixada(+)"
    PROPORTIONAL_RATE = "Proporcional(x)"
    
    NONE_RATE_INDEX = 0
    PREFIXED_RATE_INDEX = 1
    PROPORTIONAL_RATE_INDEX = 2
    
    ADDED_RATE_TYPE_LIST = [NONE_RATE, PREFIXED_RATE, PROPORTIONAL_RATE]
    
    @staticmethod
    def set_yearly_rate_from_monthly_rates(df: pd.DataFrame, yearly_rate_column: str, months_columns: list) -> None:
        df_copy = df.copy()
        df_copy[months_columns] = df_copy[months_columns].div(100)
        df_copy[months_columns] = df_copy[months_columns].add(1)
        df[yearly_rate_column] = df_copy[months_columns].product(axis="columns")
        df[yearly_rate_column] = df[yearly_rate_column].sub(1)
        df[yearly_rate_column] = df[yearly_rate_column].mul(100)

    @staticmethod
    def get_monthly_rates_from_prefixed_yearly_rate(yearly_rate: float):
        adjusted_yearly_rate = (yearly_rate / 100) + 1
        return ((adjusted_yearly_rate ** (1/12)) - 1) * 100

    @staticmethod
    def set_cumulative_values_by_rates(df: pd.DataFrame, rate_column: str, value_column: str, initial_value: float) -> None:
        df_copy = df.copy()
        df_copy[rate_column] = df_copy[rate_column].div(100)
        df_copy[rate_column] = df_copy[rate_column].add(1)
        df[value_column] = df_copy[rate_column].cumprod()
        df[value_column] = df[value_column].mul(initial_value)

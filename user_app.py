"""Script used to show a GUI interface, based on Streamlit, to show data related to IPCA, SELIC, etc.

Those data are registered in MongoDB database.
"""

import locale

import streamlit as st

from db_collection import DBCollection, EconomicIndexers

from dates import DateOperations as date

from interest_rate import InterestCalculation as interest

from indexer_api import get_interest_value, get_interest_rate



locale.setlocale(locale.LC_ALL, "pt_BR.UTF-8")



# Methods for formatting

def get_value_as_currency_string(value: float) -> str:
    return locale.currency(value, grouping=True)

def get_value_as_percentage_string(value: float) -> str:
    return locale.format_string("%.2f", value) + " %"



# General methods

def get_mean_interest_rate_per_months(total_months: int, interest_rate: float) -> float:
    return ((1 + interest_rate) ** (1 / total_months)) - 1

def get_mean_interest_rate_per_year(monthly_interest_rate: float) -> float:
    return ((1 + monthly_interest_rate) ** 12) - 1



# Methods for Streamlit organization

def show_additional_rate_fields(collection: DBCollection, rate_value, rate_index) -> tuple:
    col1, col2 = st.columns(2)
    with col1:
        added_rate = st.number_input(
            "Taxa adicional a.a. (%):", min_value=0.00, max_value=1000.00, value=rate_value,
            key=collection.get_collection_name()+"rate",
        )
    with col2:
        added_rate_type = st.radio(
            "Tipo de taxa:", added_rate_type_list, horizontal=True, index=rate_index,
            key=collection.get_collection_name()+"rate_type",
        )
    return added_rate, added_rate_type

def show_result_fields_top(collection: DBCollection, added_rate, added_rate_type) -> tuple:
    final_value = collection.get_adjusted_value_from_values(initial_value, initial_date, final_date, added_rate, added_rate_type)
    interest_value = get_interest_value(initial_value, final_value)
    interest_rate = get_interest_rate(initial_value, final_value)
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Valor final:", get_value_as_currency_string(final_value))
    with col2:
        st.metric("Juros:", get_value_as_currency_string(interest_value))
    with col3:
        st.metric("Juros:", get_value_as_percentage_string(interest_rate * 100))
    return final_value, interest_value, interest_rate

def show_indexer_historic_table(collection: DBCollection) -> None:
    with st.expander("Tabela de histórico do Índice:", expanded=False):
        st.dataframe(
            collection.get_transposed_stacked_dataframe().style.format(na_rep="-", precision=4, decimal=",", thousands=None),
            column_config={collection.STACKED_YEAR_COLUMN: st.column_config.NumberColumn(format="%d")},
            use_container_width=True,
        )  

def show_indexer_cumulated_chart(collection: DBCollection, stacked_dataframe) -> None:
    with st.expander("Gráfico de valor acumulado:", expanded=False):
        st.line_chart(
            data=stacked_dataframe,
            x=collection.STACKED_DATE_COLUMN,
            y=[collection.STACKED_VALUE_COLUMN, collection.STACKED_ADJ_VALUE_COLUMN],
        )

def show_indexer_historic_chart(collection: DBCollection, stacked_dataframe) -> None:
    with st.expander("Gráfico de taxa mensal:", expanded=False):
        st.line_chart(
            data=stacked_dataframe,
            x=collection.STACKED_DATE_COLUMN,
            y=[collection.STACKED_RATE_COLUMN, collection.STACKED_ADJ_RATE_COLUMN],
        )

def fill_data_in_tab(collection: DBCollection, rate_value, rate_index) -> None:
    added_rate, added_rate_type = show_additional_rate_fields(collection, rate_value, rate_index)
    final_value, interest_value, interest_rate = show_result_fields_top(collection, added_rate, added_rate_type)
    
    stacked_dataframe = collection.get_stacked_dataframe_adjusted_from_values(initial_value, initial_date, final_date, added_rate, added_rate_type)
    
    total_months = len(stacked_dataframe)
    monthly_interest_rate = get_mean_interest_rate_per_months(total_months, interest_rate)
    yearly_interest_rate = get_mean_interest_rate_per_year(monthly_interest_rate)
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Período total em meses:", total_months)
    with col2:
        st.metric("Taxa média mensal:", get_value_as_percentage_string(monthly_interest_rate * 100))
    with col3:
        st.metric("Taxa média anual:", get_value_as_percentage_string(yearly_interest_rate * 100))
    
    show_indexer_cumulated_chart(collection, stacked_dataframe)
    show_indexer_historic_chart(collection, stacked_dataframe)

    show_indexer_historic_table(collection)
    




st.set_page_config(page_title="Indicadores Econômicos", layout="wide")

st.write("## Indicadores Econômicos")



indexers = EconomicIndexers()



# Side bar for value and date parameterization

with st.sidebar:
    
    months_list = date.MONTHS_LIST
    
    years_list = indexers.ipca.get_years_from_stacked_dataframe()
    
    added_rate_type_list = interest.ADDED_RATE_TYPE_LIST
    
    initial_value = st.number_input("Valor inicial (R$):", min_value=0.01, max_value=1000000000.00, value=1000.00, step=10.00)
    
    left_col, right_col = st.columns(2)
    
    with left_col:
        initial_month = st.selectbox("Mês inicial:", months_list)
        final_month = st.selectbox("Mês final:", months_list)
    
    with right_col:
        initial_year = st.selectbox("Ano inicial:", years_list, index=0)
        final_year = st.selectbox("Ano final:", years_list, index=len(years_list)-1)
    
    initial_date = date.convert_values_to_datetime(initial_year, date.get_month_index_from_string(initial_month))
    final_date = date.convert_values_to_datetime(final_year, date.get_month_index_from_string(final_month))



# Economic Indexer tabs

ipca_tab, cdi_tab, selic_tab, fgts_tab, poup_tab = st.tabs(indexers.get_db_collection_titles_list())

with ipca_tab:
    fill_data_in_tab(indexers.ipca, 5.0, interest.PREFIXED_RATE_INDEX)

with cdi_tab:
    fill_data_in_tab(indexers.cdi, 110.0, interest.PROPORTIONAL_RATE_INDEX)

with selic_tab:
    fill_data_in_tab(indexers.selic, 110.0, interest.PROPORTIONAL_RATE_INDEX)

with fgts_tab:
    fill_data_in_tab(indexers.fgts, 0.0, interest.NONE_RATE_INDEX)

with poup_tab:
    fill_data_in_tab(indexers.poup, 0.0, interest.NONE_RATE_INDEX)

"""Script used to show a GUI interface, based on Streamlit, to show data related to IPCA, SELIC, etc.

Those data are registered in MobgoDB.
"""

import streamlit as st

from db_connection import init_connection
from db_collection import DBCollection, IPCACollection, CDICollection, SELICCollection, FGTSCollection, PoupancaCollection

from dates import DateOperations as date
from interest_rate import InterestCalculation as interest



st.set_page_config(
    page_title="Indicadores Econômicos",
    layout="wide",
)

st.write("## Indicadores Econômicos")



mongo_client = init_connection()



ipca = IPCACollection(mongo_client)
cdi = CDICollection(mongo_client)
selic = SELICCollection(mongo_client)
fgts = FGTSCollection(mongo_client)
poup = PoupancaCollection(mongo_client)



with st.sidebar:
    
    months_list = date.MONTHS_LIST
    
    years_list = ipca.get_years_from_stacked_dataframe()
    
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



tabs_title_list = [
    ipca.get_title(),
    cdi.get_title(),
    selic.get_title(),
    fgts.get_title(),
    poup.get_title(),
]

ipca_tab, cdi_tab, selic_tab, fgts_tab, poup_tab = st.tabs(tabs_title_list)

def fill_data_in_tab(collection: DBCollection, rate_value, rate_index):

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

    stacked_dataframe = collection.get_stacked_dataframe_adjusted_from_values(initial_value, initial_date, final_date, added_rate, added_rate_type)

    with st.expander("Tabela de histórico do Índice:", expanded=False):
        st.dataframe(
            collection.get_transposed_stacked_dataframe().style.format(na_rep="-", precision=4, decimal=",", thousands=None),
            column_config={collection.STACKED_YEAR_COLUMN: st.column_config.NumberColumn(format="%d")},
            use_container_width=True,
        )    
    
    with st.expander("Gráfico de valor acumulado:", expanded=True):
        st.line_chart(
            data=stacked_dataframe,
            x=collection.STACKED_DATE_COLUMN,
            y=[collection.STACKED_VALUE_COLUMN, collection.STACKED_ADJ_VALUE_COLUMN],
        )
    
    with st.expander("Gráfico de taxa mensal:", expanded=True):
        st.line_chart(
            data=stacked_dataframe,
            x=collection.STACKED_DATE_COLUMN,
            y=[collection.STACKED_RATE_COLUMN, collection.STACKED_ADJ_RATE_COLUMN],
        )

with ipca_tab:
    fill_data_in_tab(ipca, 6.0, interest.PREFIXED_RATE_INDEX)

with cdi_tab:
    fill_data_in_tab(cdi, 120.0, interest.PROPORTIONAL_RATE_INDEX)

with selic_tab:
    fill_data_in_tab(selic, 100.0, interest.PROPORTIONAL_RATE_INDEX)

with fgts_tab:
    fill_data_in_tab(fgts, 0.0, interest.NONE_RATE_INDEX)

with poup_tab:
    fill_data_in_tab(poup, 0.0, interest.NONE_RATE_INDEX)

"""Script used to display a GUI interface, based on Streamlit, in order to register in MongoDB some values related to IPCA, SELIC, etc."""

import pymongo

from datetime import date

import streamlit as st

from dateutil.relativedelta import relativedelta

from db_collection import DBCollection, EconomicIndexers


# Example:
# LAST_REGISTER_DATE = 01/MAR/2023
# NEXT_REGISTER_DATE = 01/APR/2023
# BUT, the data related to April is only completely available in 15/May/2023
# Then, NEXT_DATE = 15/MAI/2023 (about 2 months and a half = 75 days)
TODAY_DATE_LESS_LAST_REGISTER_DATE = 75



def insert_new_item(db_collection: DBCollection, item_date: date, item_rate: float) -> None:
    """Insert a new register to the collection."""
    db = db_collection._mongo_client.get_database(db_collection._database_name)
    db.get_collection(db_collection._collection_name).insert_one(
        {
            DBCollection.DB_YEAR_COLUMN: item_date.year,
            DBCollection.DB_MONTH_COLUMN: item_date.month,
            DBCollection.DB_DAY_COLUMN: item_date.day,
            DBCollection.DB_RATE_COLUMN: item_rate,
        }
    )



def get_last_item_registered(db_collection: DBCollection) -> dict:
    """Return a dictionary with year, month, day, value."""
    db = db_collection._mongo_client.get_database(db_collection._database_name)
    item = db.get_collection(db_collection._collection_name).find().sort(
        DBCollection.DB_ID_COLUMN, pymongo.DESCENDING
    ).limit(1)
    return list(item)[0]

def get_date_tuple_from_item_registered(item: dict) -> tuple:
    """Return a tuple with year, month, day from the register."""
    return (
        item[DBCollection.DB_YEAR_COLUMN],
        item[DBCollection.DB_MONTH_COLUMN],
        item[DBCollection.DB_DAY_COLUMN],
    )

def get_date_from_item_registered(item: dict) -> date:
    """Return a date from the register."""
    date_tuple = get_date_tuple_from_item_registered(item)
    return get_date_from_date_tuple(date_tuple)

def get_rate_from_item_registered(item: dict) -> float:
    """Return a rate from the register."""
    return item[DBCollection.DB_RATE_COLUMN]



def get_date_from_date_tuple(date_tuple: tuple) -> date:
    """Return a date from year, month, day tuple."""
    return date(date_tuple[0], date_tuple[1], date_tuple[2])



def get_last_register_string(db_collection: DBCollection) -> str:
    """Return a string related to the last register."""
    last_item = get_last_item_registered(db_collection)
    last_date = get_date_from_item_registered(last_item)
    last_rate = get_rate_from_item_registered(last_item)
    return f"( {last_date}  :  {last_rate:.4f} )"



def show_number_input(db_collection: DBCollection) -> float:
    """Show a widget to insert the related rate."""
    label = f"[{db_collection.get_title()}]({db_collection.get_link_for_scraping()}) {get_last_register_string(db_collection)}"
    return st.number_input(label, value=1.0000, step=0.0001, format="%.4f")



def get_days_to_be_unblocked(last_date: date) -> int:
    today_date = date.today()
    return TODAY_DATE_LESS_LAST_REGISTER_DATE - (today_date - last_date).days

def is_blocked_to_insert_new_register(last_date: date) -> bool:
    """Return TRUE if today is SUFFICIENT days above the last register."""
    today_date = date.today()
    return not (today_date - last_date).days >= TODAY_DATE_LESS_LAST_REGISTER_DATE



st.set_page_config(
    page_title="Indicadores Econômicos",
    layout="wide",
)



indexers = EconomicIndexers()



last_date = get_date_from_item_registered(get_last_item_registered(indexers.ipca))
next_date = last_date + relativedelta(months=1)



st.write(f"## Indicadores Econômicos")
st.write(f"")
st.write(f"Insira nos campos abaixo a taxa correspondente de cada um dos Indicadores Econômicos.")
st.write(f"")
st.write(f"Data de referência para o novo registro: __{next_date}__")
st.write(f"")



col1, col2, col3 = st.columns(3)

with col1:
    ipca_number = show_number_input(indexers.ipca)

with col2:
    cdi_number = show_number_input(indexers.cdi)
    selic_number = show_number_input(indexers.selic)

with col3:
    fgts_number = show_number_input(indexers.fgts)
    poup_number = show_number_input(indexers.poup)



st.write(f"")
st.write(f"")
if st.button("INSERIR REGISTRO", disabled=is_blocked_to_insert_new_register(last_date)):
    insert_new_item(indexers.ipca, next_date, ipca_number)
    insert_new_item(indexers.cdi, next_date, cdi_number)
    insert_new_item(indexers.selic, next_date, selic_number)
    insert_new_item(indexers.fgts, next_date, fgts_number)
    insert_new_item(indexers.poup, next_date, poup_number)
    st.balloons()
    st.success("Registro salvo com sucesso! A página será recarregada.", icon="✅")
    st.experimental_rerun()



if is_blocked_to_insert_new_register(last_date):
    st.warning(
        f"A página está bloqueada para inserção de novos registros. Retorne em {get_days_to_be_unblocked(last_date)} dia(s).", icon="⚠️")

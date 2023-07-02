from fastapi import FastAPI, HTTPException

from datetime import datetime

from interest_rate import InterestCalculation as interest

from db_connection import init_connection
from db_collection import DBCollection, IPCACollection, CDICollection, SELICCollection, FGTSCollection, PoupancaCollection



app = FastAPI()


mongo_client = init_connection()

ipca = IPCACollection(mongo_client)
cdi = CDICollection(mongo_client)
selic = SELICCollection(mongo_client)
fgts = FGTSCollection(mongo_client)
poup = PoupancaCollection(mongo_client)

db_collection_dict = {
    "IPCA": ipca, 
    "CDI": cdi,
    "SELIC": selic,
    "FGTS": fgts,
    "POUPANCA": poup,
}



def get_db_collection(indexer_reference: str) -> DBCollection:
    if indexer_reference == "IPCA":
        return ipca
    elif indexer_reference == "CDI":
        return cdi
    elif indexer_reference == "SELIC":
        return selic
    elif indexer_reference == "FGTS":
        return fgts
    elif indexer_reference == "POUPANCA":
        return poup



@app.get("/")
def read_root():
    return {"App": "ECONIndexer API"}



@app.get("/interest_value")
def get_interest_value(
    initial_value: float = 0.0,
    final_value: float = 0.0,
    ):
    return {"interest_value": final_value - initial_value}

@app.get("/interest_rate")
def get_interest_rate(
    initial_value: float = 0.0,
    final_value: float = 0.0,
    ):
    try:
        interest_rate = get_interest_value(initial_value, final_value)["interest_value"] / initial_value
        return {"interest_rate": interest_rate}
    except ZeroDivisionError:
        raise HTTPException(status_code=500, detail="Uma divisão por zero ocorreu.")



@app.get("/final_value_by_indexer")
def get_final_value_by_indexer(
	initial_value: float,
	initial_date: datetime,
	final_date: datetime,
	indexer_reference: str,
	indexer_type: int,
	indexer_add_rate: float,
    ):
    """Return the final value given some parameters related to some economic indexer.

    Args:
        initial_value (float): the initial amount of contributed value
        initial_date (datetime): the initial date
        final_date (datetime): the final date
        indexer_reference (str): a string with 'IPCA', 'CDI', 'SELIC', 'FGTS', 'POUPANCA'
        indexer_type (int): 0=None; 1=Prefixed; 2=Proportional
        indexer_add_rate (float)[%]: if Prefixed type, a rate to 'sum'; if Proportional type, a rate to multiply per the indexer rate
    """
    indexer = get_db_collection(indexer_reference)
    if indexer:
        rate_value = indexer_add_rate
        rate_type = interest.ADDED_RATE_TYPE_LIST[indexer_type]
        df = indexer.get_stacked_dataframe_adjusted_from_values(initial_value, initial_date, final_date, rate_value, rate_type)
        final_value_by_indexer = df[indexer.STACKED_ADJ_VALUE_COLUMN].iloc[-1]
        return {"final_value_by_indexer": final_value_by_indexer}
    else:
        raise HTTPException(status_code=500, detail="O valor para a variável 'indexer_reference' é inválido.")

@app.get("/interest_value_by_indexer")
def get_interest_value_by_indexer(
	initial_value: float,
	initial_date: datetime,
	final_date: datetime,
	indexer_reference: str,
	indexer_type: int,
	indexer_add_rate: float,
    ):
    """Return the delta value given some parameters related to some economic indexer.

    Args:
        initial_value (float): the initial amount of contributed value
        initial_date (datetime): the initial date
        final_date (datetime): the final date
        indexer_reference (str): a string with 'IPCA', 'CDI', 'SELIC', 'FGTS', 'POUPANCA'
        indexer_type (int): 0=None; 1=Prefixed; 2=Proportional
        indexer_add_rate (float)[%]: if Prefixed type, a rate to 'sum'; if Proportional type, a rate to multiply per the indexer rate
    """
    final_value_by_indexer = get_final_value_by_indexer(initial_value, initial_date, final_date, indexer_reference, indexer_type, indexer_add_rate)["final_value_by_indexer"]
    interest_value_by_indexer = get_interest_value(initial_value, final_value_by_indexer)["interest_value"]
    return {"interest_value_by_indexer": interest_value_by_indexer}

@app.get("/interest_rate_by_indexer")
def get_interest_rate_by_indexer(
	initial_value: float,
	initial_date: datetime,
	final_date: datetime,
	indexer_reference: str,
	indexer_type: int,
	indexer_add_rate: float,
    ):
    """Return the interest rate given some parameters related to some economic indexer.

    Args:
        initial_value (float): the initial amount of contributed value
        initial_date (datetime): the initial date
        final_date (datetime): the final date
        indexer_reference (str): a string with 'IPCA', 'CDI', 'SELIC', 'FGTS', 'POUPANCA'
        indexer_type (int): 0=None; 1=Prefixed; 2=Proportional
        indexer_add_rate (float)[%]: if Prefixed type, a rate to 'sum'; if Proportional type, a rate to multiply per the indexer rate
    """
    final_value_by_indexer = get_final_value_by_indexer(initial_value, initial_date, final_date, indexer_reference, indexer_type, indexer_add_rate)["final_value_by_indexer"]
    interest_rate_by_indexer = get_interest_rate(initial_value, final_value_by_indexer)["interest_rate"]
    return {"interest_rate_by_indexer": interest_rate_by_indexer}



@app.get("/benchmarking_by_indexer")
def get_benchmarking_by_indexer(
	initial_value: float,
    final_value: float,
	initial_date: datetime,
	final_date: datetime,
    indexer_reference: str,
    ):
    """Return the proportion of the interest values in the period compared with some indexer.

    Args:
        initial_value (float): the initial amount of contributed value
        final_value (float): the final amount of value (initial_value + interest_value)
        initial_date (datetime): the initial date
        final_date (datetime): the final date
        indexer_reference (str): a string with 'CDI'; others are not implemented for now
    """
    indexer = get_db_collection(indexer_reference)
    if indexer_reference == "CDI":
        pass
    elif indexer is None:
        raise HTTPException(status_code=500, detail="O valor para a variável 'indexer_reference' é inválido.")
    else:
        raise HTTPException(status_code=501, detail="Método ainda não implementado para o valor da variável 'indexer_reference'.")
    indexer_type = 0 # None
    indexer_add_rate = 0.0 # None
    interest_value_by_indexer = get_interest_value_by_indexer(initial_value, initial_date, final_date, indexer_reference, indexer_type, indexer_add_rate)["interest_value_by_indexer"]
    interest_value = get_interest_value(initial_value, final_value)["interest_value"]
    benchmarking_by_indexer = interest_value / interest_value_by_indexer
    return {"benchmarking_by_indexer": benchmarking_by_indexer}



# TODO: convert the below code to pytest

# print(get_interest_value(1000, 1500))
# print(get_interest_rate(1000, 1500))

# print("DEFAULT:   " + str(get_final_value_by_indexer(1000, datetime(2000,1,1), datetime(2023,1,1), "IPCA", 0, 0.00)))
# print("DEFAULT:   " + str(get_interest_value_by_indexer(1000, datetime(2000,1,1), datetime(2023,1,1), "IPCA", 0, 0.00)))
# print("DEFAULT:   " + str(get_interest_rate_by_indexer(1000, datetime(2000,1,1), datetime(2023,1,1), "IPCA", 0, 0.00)))
# print("DEFAULT:   " + str(get_benchmarking_by_indexer(1000, 13755.97129523145, datetime(2000,1,1), datetime(2023,1,1), "CDI")))
# print("")

# print("PREFIXADO: " + str(get_final_value_by_indexer(1000, datetime(2000,1,1), datetime(2023,1,1), "IPCA", 1, 6.00)))
# print("PREFIXADO: " + str(get_interest_value_by_indexer(1000, datetime(2000,1,1), datetime(2023,1,1), "IPCA", 1, 6.00)))
# print("PREFIXADO: " + str(get_interest_rate_by_indexer(1000, datetime(2000,1,1), datetime(2023,1,1), "IPCA", 1, 6.00)))
# print("PREFIXADO: " + str(get_benchmarking_by_indexer(1000, 13755.97129523145, datetime(2000,1,1), datetime(2023,1,1), "CDI")))
# print("")

# print(get_final_value_by_indexer(1000, datetime(2000,1,1), datetime(2023,1,1), "CDI", 0, 0.00))
# print(get_final_value_by_indexer(1000, datetime(2000,1,1), datetime(2023,1,1), "CDI", 2, 120.00))

# print(get_final_value_by_indexer(1000, datetime(2000,1,1), datetime(2023,1,1), "SELIC", 0, 0.00))
# print(get_final_value_by_indexer(1000, datetime(2000,1,1), datetime(2023,1,1), "SELIC", 1, 2.00))

# print(get_final_value_by_indexer(1000, datetime(2000,1,1), datetime(2023,1,1), "FGTS", 0, 0.00))

# print(get_final_value_by_indexer(1000, datetime(2000,1,1), datetime(2023,1,1), "POUPANCA", 0, 0.00))

# print(get_final_value_by_indexer(1000, datetime(2000,1,1), datetime(2023,1,1), "", 0, 0.00))

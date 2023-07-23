"""This is an API, based on FastAPI, used to calculate Interest Value and Interest Rate based on some Brazilian Economic Indexers."""

from fastapi import FastAPI, HTTPException

from datetime import datetime

from interest_rate import InterestCalculation as interest

from db_collection import EconomicIndexers



app = FastAPI()



@app.get("/")
def root():
    """Return a dictionary with some APP properties.

    Example:
        {
            'App': 'ECONIndexer API',
            'Version': '1.0.0',
            'Last Update': '22/Jul/2023',
        }
    """
    return {
        "App": "ECONIndexer API",
        "Version": "1.0.0",
        "Last Update": "22/Jul/2023",
    }



@app.get("/interest_value")
def get_interest_value(
    initial_value: float = 0.0,
    final_value: float = 0.0,
    ) -> float:
    """Return the Interest Value given the initial and final values.

    Args:
        initial_value (float, optional): the Initial amount of money. Defaults to 0.0.
        final_value (float, optional): the Final amount of money. Defaults to 0.0.

    Returns:
        float: the Interest Value is the difference between Final and Initial values.
    """
    return final_value - initial_value

@app.get("/interest_rate")
def get_interest_rate(
    initial_value: float = 0.0,
    final_value: float = 0.0,
    ) -> float:
    """Return the Interest Rate given the initial and final values.

    Args:
        initial_value (float, optional): the Initial amount of money. Defaults to 0.0.
        final_value (float, optional): the Final amount of money. Defaults to 0.0.

    Returns:
        float: the Interest Rate is the difference between Final and Initial values, divided per the Initial value.
    """
    try:
        interest_rate = get_interest_value(initial_value, final_value) / initial_value
        return interest_rate
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
    """Return the final amount of value given some Economic Indexer.

    Args:
        initial_value (float): the Initial amount of money
        initial_date (datetime): the initial date
        final_date (datetime): the final date
        indexer_reference (str): a string with 'IPCA', 'CDI', 'SELIC', 'FGTS' or 'POUPANCA'
        indexer_type (int): 0=None; 1=Prefixed; 2=Proportional
        indexer_add_rate (float)[%]: if Prefixed type, a rate to 'sum'; if Proportional type, a rate to multiply per the indexer rate
    
    Returns:
        float: the total amount of money.
    """
    indexers = EconomicIndexers()
    indexer = indexers.get_db_collection_by_indexer(indexer_reference)
    if indexer:
        rate_value = indexer_add_rate
        rate_type = interest.ADDED_RATE_TYPE_LIST[indexer_type]
        return indexer.get_adjusted_value_from_values(initial_value, initial_date, final_date, rate_value, rate_type)
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
        initial_value (float): the Initial amount of money
        initial_date (datetime): the initial date
        final_date (datetime): the final date
        indexer_reference (str): a string with 'IPCA', 'CDI', 'SELIC', 'FGTS', 'POUPANCA'
        indexer_type (int): 0=None; 1=Prefixed; 2=Proportional
        indexer_add_rate (float)[%]: if Prefixed type, a rate to 'sum'; if Proportional type, a rate to multiply per the indexer rate
    
    Returns:
        float: the Interest Value is the difference between Final and Initial values.
    """
    final_value_by_indexer = get_final_value_by_indexer(initial_value, initial_date, final_date, indexer_reference, indexer_type, indexer_add_rate)
    interest_value_by_indexer = get_interest_value(initial_value, final_value_by_indexer)
    return interest_value_by_indexer

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
        initial_value (float): the Initial amount of money
        initial_date (datetime): the initial date
        final_date (datetime): the final date
        indexer_reference (str): a string with 'IPCA', 'CDI', 'SELIC', 'FGTS', 'POUPANCA'
        indexer_type (int): 0=None; 1=Prefixed; 2=Proportional
        indexer_add_rate (float)[%]: if Prefixed type, a rate to 'sum'; if Proportional type, a rate to multiply per the indexer rate
    
    Returns:
        float: the Interest Rate is the difference between Final and Initial values, divided per the Initial value.
    """
    final_value_by_indexer = get_final_value_by_indexer(initial_value, initial_date, final_date, indexer_reference, indexer_type, indexer_add_rate)
    interest_rate_by_indexer = get_interest_rate(initial_value, final_value_by_indexer)
    return interest_rate_by_indexer



@app.get("/benchmarking_by_indexer")
def get_benchmarking_by_indexer(
	initial_value: float,
    final_value: float,
	initial_date: datetime,
	final_date: datetime,
    indexer_reference: str,
    ):
    """Return the proportion of the interest values in the period compared with some indexer.
    For now, only 'CDI' benchmarking is available.
    
    At first, the method calculates the User Interest Value given the user numbers (initial_value and final_value).
    Then, the method calculates the Indexer Interest Value based on the wished Economic Indexer (indexer_reference).
    Finally, the method divides the Indexer Interest Value per the User Interest Value.

    Args:
        initial_value (float): the Initial amount of money
        final_value (float): the Final amount of money (initial_value + interest_value)
        initial_date (datetime): the initial date
        final_date (datetime): the final date
        indexer_reference (str): a string with 'CDI'; others are not implemented for now
    
    Returns:
        float: Indexer Interest Value divided per the User Interest Value.
    """
    indexers = EconomicIndexers()
    indexer = indexers.get_db_collection_by_indexer(indexer_reference)
    if indexer_reference == "CDI":
        pass
    elif indexer is None:
        raise HTTPException(status_code=500, detail="O valor para a variável 'indexer_reference' é inválido.")
    else:
        raise HTTPException(status_code=501, detail="Método ainda não implementado para o valor da variável 'indexer_reference'.")
    indexer_type = 0 # None
    indexer_add_rate = 0.0 # None
    interest_value_by_indexer = get_interest_value_by_indexer(initial_value, initial_date, final_date, indexer_reference, indexer_type, indexer_add_rate)
    interest_value = get_interest_value(initial_value, final_value)
    benchmarking_by_indexer = interest_value / interest_value_by_indexer
    return benchmarking_by_indexer

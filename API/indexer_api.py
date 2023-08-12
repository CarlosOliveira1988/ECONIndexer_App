"""This is an API, based on FastAPI, used to calculate Interest Value and Interest Rate based on some Brazilian Economic Indexers."""

import pymongo

from fastapi import FastAPI, HTTPException

from datetime import datetime



import sys
sys.path.append('..')

try:
    from interest_rate import InterestCalculation as interest
except ModuleNotFoundError:
    from API.interest_rate import InterestCalculation as interest

try:
    from db_collection import EconomicIndexers
except ModuleNotFoundError:
    from API.db_collection import EconomicIndexers

import os
print(os.path.abspath(os.curdir))



description = """
__ECONIndexer API__ helps you to compare your investments with some common __Brazilian Economic Indexers__. 🚀

 
Let's suppose you have bought a small property 10 years ago, but today yout want to sell it.

__1)__ How much should your property costs in order to you not lose money due the inflation (IPCA)?

__2)__ Considering some common Treasury Bonds yields (let's say IPCA + 6.5%) as the cost oportunity. 
What would be the best option in the past: buy the small property or buy some Treasure Bonds?

 
Since the __Economy is cyclic__, those questions and answers may lead you (or your children) to make
better decisions in the future.

If you bought the small property in a time of high Interest Rates, probably you lost money.
Then, why buy new properties during the next cycle of high Interest Rates?
"""

app = FastAPI(
    title = "ECONIndexer API",
    description=description,
    version = "1.0.0",
)



from dotenv import load_dotenv
load_dotenv(encoding="iso-8859-1")
mongodb_credentials = os.getenv("MONGODB_CREDENTIALS")
mongo_client = pymongo.MongoClient(mongodb_credentials)



@app.get("/")
def root():
    """Return a dictionary with some __APP properties__."""
    return {
        "App": "ECONIndexer API",
        "Version": "1.0.0",
        "Last Update": "12/Aug/2023",
    }



@app.get("/interest_value")
def get_interest_value(
    initial_value: float = 0.0,
    final_value: float = 0.0,
    ) -> float:
    """Return the __Interest Value__ given the Initial and Final values.

    Args:  
    > __initial_value (float, optional):__ the Initial amount of money. Defaults to 0.0.  
    > __final_value (float, optional):__ the Final amount of money. Defaults to 0.0.  

    Returns:
    > __interest_value (float):__ is the difference between Final and Initial values.
    """
    return final_value - initial_value

@app.get("/interest_rate")
def get_interest_rate(
    initial_value: float = 0.0,
    final_value: float = 0.0,
    ) -> float:
    """Return the __Interest Rate__ given the Initial and Final values.

    Args:
    > __initial_value (float, optional):__ the Initial amount of money. Defaults to 0.0.  
    > __final_value (float, optional):__ the Final amount of money. Defaults to 0.0.  

    Returns:
    > __interest_rate (float):__ is the difference between Final and Initial values, divided per the Initial value.
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
    """Return the __Final Amount of Value__ given some Economic Indexer.

    Args:
    > __initial_value (float):__ the Initial amount of money  
    > __initial_date (datetime):__ the initial date  
    > __final_date (datetime):__ the final date  
    > __indexer_reference (str):__ a string with _IPCA_, _CDI_, _SELIC_, _FGTS_ or _POUPANCA_  
    > __indexer_type (int):__ 0=None; 1=Prefixed; 2=Proportional  
    > __indexer_add_rate (float)[%]:__ if Prefixed type, a rate to 'sum'; if Proportional type, a rate to multiply per the indexer rate  
    
    Returns:
    > __final_value (float):__ the total amount of money.
    """
    indexers = EconomicIndexers(mongo_client)
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
    """Return the __Interest Value__ given some parameters related to some Economic Indexer.

    Args:
    > __initial_value (float):__ the Initial amount of money  
    > __initial_date (datetime):__ the initial date  
    > __final_date (datetime):__ the final date  
    > __indexer_reference (str):__ a string with _IPCA_, _CDI_, _SELIC_, _FGTS_ or _POUPANCA_  
    > __indexer_type (int):__ 0=None; 1=Prefixed; 2=Proportional  
    > __indexer_add_rate (float)[%]:__ if Prefixed type, a rate to 'sum'; if Proportional type, a rate to multiply per the indexer rate  
    
    Returns:
    > __interest_value_by_indexer (float):__ is the difference between Final and Initial values, considering the Economic Indexer and the given period.
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
    """Return the __Interest Rate__ given some parameters related to some Economic Indexer.

    Args:
    > __initial_value (float):__ the Initial amount of money  
    > __initial_date (datetime):__ the initial date  
    > __final_date (datetime):__ the final date  
    > __indexer_reference (str):__ a string with _IPCA_, _CDI_, _SELIC_, _FGTS_ or _POUPANCA_  
    > __indexer_type (int):__ 0=None; 1=Prefixed; 2=Proportional  
    > __indexer_add_rate (float)[%]:__ if Prefixed type, a rate to 'sum'; if Proportional type, a rate to multiply per the indexer rate  
    
    Returns:
    > __interest_rate_by_indexer (float):__ is the difference between Final and Initial values, divided per the Initial value, considering the Economic Indexer and the given period.
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
    """Return the proportion of the interest values in the period compared with some Economic Indexer.  
    __For now, only 'CDI' benchmarking is available.__
    
    At first, the method calculates the __User Interest Value__ given the user values (initial_value and final_value).  
    Then, the method calculates the __Indexer Interest Value__ based on the wished Economic Indexer (indexer_reference).  
    Finally, the method divides the __Indexer Interest Value__ per the __User Interest Value__.  

    Args:
    > __initial_value (float):__ the Initial amount of money  
    > __final_value (float):__ the Final amount of money (initial_value + interest_value)  
    > __initial_date (datetime):__ the initial date  
    > __final_date (datetime):__ the final date  
    > __indexer_reference (str):__ a string with 'CDI'; others are not implemented for now  
    
    Returns:
    > __benchmarking_by_indexer (float):__ is the Indexer Interest Value divided per the User Interest Value.
    """
    indexers = EconomicIndexers(mongo_client)
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

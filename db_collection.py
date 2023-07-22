
import pymongo

from abc import ABC
import pandas as pd

from datetime import datetime

from dates import DateOperations as date
from interest_rate import InterestCalculation as interest

from db_connection import init_connection



class DBCollection(ABC):
    
    # Columns from the database collection
    DB_ID_COLUMN = "_id"
    DB_DAY_COLUMN = "day"
    DB_MONTH_COLUMN = "month"
    DB_YEAR_COLUMN = "year"
    DB_RATE_COLUMN = "value"
    
    # Stacked columns related to the renamed database collection
    STACKED_DAY_COLUMN = "Dia"
    STACKED_MONTH_COLUMN = "Mês"
    STACKED_YEAR_COLUMN = "Ano"
    STACKED_DATE_COLUMN = "Data"
    STACKED_RATE_COLUMN = "Taxa Índice(%)"
    STACKED_VALUE_COLUMN = "Valor Índice(R$)"
    STACKED_ADJ_RATE_COLUMN = "Taxa Índice + Adicional(%)"
    STACKED_ADJ_VALUE_COLUMN = "Valor Índice + Adicional(R$)"
    
    # Dictionary to rename columns when showing stacked dataframes
    COLLECTION_RENAME_DICT = {
        DB_DAY_COLUMN: STACKED_DAY_COLUMN,
        DB_MONTH_COLUMN: STACKED_MONTH_COLUMN,
        DB_YEAR_COLUMN: STACKED_YEAR_COLUMN,
        DB_RATE_COLUMN: STACKED_RATE_COLUMN,
    }
    
    # Non stacked datafame columns
    TRANSPOSED_MONTHS_COLUMNS = date.MONTHS_LIST
    TRANSPOSED_YEARLY_RATE_COLUMN = "Anual(%)"
    
    def __init__(self, mongo_client: pymongo.MongoClient, database_name: str, collection_name: str, title) -> None:
        self._mongo_client = mongo_client
        self._database_name = database_name
        self._collection_name = collection_name
        self._title = title
        self.update_dataframe_from_db()
        self._link = None
    
    
    def get_database_name(self) -> str:
        return self._database_name

    def get_collection_name(self) -> str:
        return self._collection_name

    def get_title(self) -> str:
        return self._title


    def set_link_for_scraping(self, link: str) -> None:
        self._link = link

    def get_link_for_scraping(self) -> str:
        return self._link


    def update_dataframe_from_db(self) -> None:
        # Get the raw dataframe from database
        db = self._mongo_client.get_database(self._database_name)
        items = db.get_collection(self._collection_name).find().sort(self.DB_ID_COLUMN, pymongo.ASCENDING)
        self._raw_dataframe = pd.DataFrame(list(items))
        
        # Get the stacked dataframe
        self._stacked_dataframe = self.__get_stacked_dataframe()
        
        # Get the renamed and transposed dataframe
        self._transposed_stacked_dataframe = self.__get_transposed_stacked_dataframe()


    def get_raw_dataframe(self) -> pd.DataFrame:
        """_id  day  month   year  value"""
        return self._raw_dataframe.copy()


    def __get_stacked_dataframe(self) -> pd.DataFrame:
        df = self.get_raw_dataframe()
               
        # Adding the date column
        df[self.STACKED_DATE_COLUMN] = pd.to_datetime(
            df[[
                self.DB_YEAR_COLUMN,
                self.DB_MONTH_COLUMN,
                self.DB_DAY_COLUMN,
            ]]
        )
        
        # Renaming some columns
        df = df.rename(columns=self.COLLECTION_RENAME_DICT, inplace=False)
        
        # Organizing the columns
        return df[[
            self.STACKED_DAY_COLUMN,
            self.STACKED_MONTH_COLUMN,
            self.STACKED_YEAR_COLUMN,
            self.STACKED_DATE_COLUMN,
            self.STACKED_RATE_COLUMN,
        ]]

    def get_stacked_dataframe(self) -> pd.DataFrame:
        """Dia  Mês   Ano  Data  Taxa(%)"""
        return self._stacked_dataframe.copy()


    def get_stacked_dataframe_from_dates(self, initial_date: datetime, final_date: datetime) -> pd.DataFrame:
        """Dia  Mês   Ano  Data  Taxa(%)"""
        return date.get_dataframe_from_dates(
            self.get_stacked_dataframe(),
            self.STACKED_DATE_COLUMN,
            initial_date,
            final_date,
        )


    def get_stacked_dataframe_from_values(self, initial_value: float, initial_date: datetime, final_date: datetime) -> pd.DataFrame:
        """Dia  Mês   Ano  Data  Taxa(%)  Valor(R$)"""
        df = self.get_stacked_dataframe_from_dates(initial_date, final_date)
        interest.set_cumulative_values_by_rates(df, self.STACKED_RATE_COLUMN, DBCollection.STACKED_VALUE_COLUMN, initial_value)
        return df


    def get_stacked_dataframe_adjusted_from_values(self, initial_value: float, initial_date: datetime, final_date: datetime, rate_value: float, rate_type: str) -> pd.DataFrame:
        """Dia  Mês   Ano  Data  Taxa(%)  Valor(R$)  Valor ajustado(R$)  Taxa ajustada(%)"""
        df = self.get_stacked_dataframe_from_values(initial_value, initial_date, final_date)
        
        if rate_type == interest.PREFIXED_RATE:
            df[self.STACKED_ADJ_RATE_COLUMN] = interest.get_monthly_rates_from_prefixed_yearly_rate(rate_value)
            interest.set_cumulative_values_by_rates(df, self.STACKED_ADJ_RATE_COLUMN, self.STACKED_ADJ_VALUE_COLUMN, initial_value)
            df[self.STACKED_ADJ_VALUE_COLUMN] -= initial_value
            df[self.STACKED_ADJ_VALUE_COLUMN] += df[self.STACKED_VALUE_COLUMN]
            df[self.STACKED_ADJ_RATE_COLUMN] += df[self.STACKED_RATE_COLUMN]
        
        elif rate_type == interest.PROPORTIONAL_RATE:
            df[self.STACKED_ADJ_VALUE_COLUMN] = (df[self.STACKED_VALUE_COLUMN] - initial_value) * (rate_value / 100)
            df[self.STACKED_ADJ_VALUE_COLUMN] += initial_value
            df[self.STACKED_ADJ_RATE_COLUMN] = df[self.STACKED_RATE_COLUMN] * (rate_value / 100)
        
        else:
            df[self.STACKED_ADJ_VALUE_COLUMN] = df[self.STACKED_VALUE_COLUMN]
            df[self.STACKED_ADJ_RATE_COLUMN] = df[self.STACKED_RATE_COLUMN]
        
        return df


    def get_years_from_stacked_dataframe(self, unique=True) -> list:
        df = self.get_stacked_dataframe()
        if unique:
            return pd.unique(df[self.STACKED_YEAR_COLUMN]).tolist()
        else:
            return df[self.STACKED_YEAR_COLUMN].tolist()


    def __get_transposed_stacked_dataframe(self):
        df = self.get_stacked_dataframe()
        
        # Transpose
        df = df.pivot(
            index=self.STACKED_YEAR_COLUMN,
            columns=self.STACKED_MONTH_COLUMN,
            values=self.STACKED_RATE_COLUMN,
        )
        
        # Rename and sort
        df = df.rename(columns=date.MONTHS_DICT, inplace=False)
        df = df.sort_index(ascending=False, inplace=False)
        
        # Add yearly rate column
        interest.set_yearly_rate_from_monthly_rates(df, self.TRANSPOSED_YEARLY_RATE_COLUMN, self.TRANSPOSED_MONTHS_COLUMNS)
        return df

    def get_transposed_stacked_dataframe(self):
        """Janeiro Fevereiro Março Abril Maio Junho Julho Agosto Setembro Outubro Novembro Dezembro"""
        return self._transposed_stacked_dataframe.copy()



class IPCACollection(DBCollection):
    def __init__(self, mongo_client: pymongo.MongoClient) -> None:
        super().__init__(mongo_client, "economic_indexers", "ipca", "IPCA")
        self.set_link_for_scraping(r"https://www.valor.srv.br/indices/ipca.php")

class CDICollection(DBCollection):
    def __init__(self, mongo_client: pymongo.MongoClient) -> None:
        super().__init__(mongo_client, "economic_indexers", "cdi", "CDI")
        self.set_link_for_scraping(r"https://www.valor.srv.br/indices/cdi.php")

class SELICCollection(DBCollection):
    def __init__(self, mongo_client: pymongo.MongoClient) -> None:
        super().__init__(mongo_client, "economic_indexers", "selic", "SELIC")
        self.set_link_for_scraping(r"https://www.valor.srv.br/indices/selic.php")

class FGTSCollection(DBCollection):
    def __init__(self, mongo_client: pymongo.MongoClient) -> None:
        super().__init__(mongo_client, "economic_indexers", "fgts", "FGTS")
        self.set_link_for_scraping(r"http://www.yahii.com.br/fgts03a06.html")

class PoupancaCollection(DBCollection):
    def __init__(self, mongo_client: pymongo.MongoClient) -> None:
        super().__init__(mongo_client, "economic_indexers", "poupanca", "POUPANCA")
        self.set_link_for_scraping(r"http://www.yahii.com.br/poupanca.html")



class EconomicIndexers:
    def __init__(self) -> None:
        self.mongo_client = init_connection()

        self.db_collection_dict = {}
        self.ipca = self.__add_to_db_collection_dict(IPCACollection(self.mongo_client))
        self.cdi = self.__add_to_db_collection_dict(CDICollection(self.mongo_client))
        self.selic = self.__add_to_db_collection_dict(SELICCollection(self.mongo_client))
        self.fgts = self.__add_to_db_collection_dict(FGTSCollection(self.mongo_client))
        self.poup = self.__add_to_db_collection_dict(PoupancaCollection(self.mongo_client))

    def __add_to_db_collection_dict(self, db_collection: DBCollection, ) -> DBCollection:
        self.db_collection_dict[db_collection.get_title()] = db_collection
        return db_collection

    def get_db_collection_by_indexer(self, indexer_reference: str) -> DBCollection:
        return self.db_collection_dict.get(indexer_reference)

    def get_db_collection_titles_list(self) -> list:
        return [collection.get_title() for collection in self.db_collection_dict.values()]


if __name__ == "__main__":

    indexers = EconomicIndexers()
    
    ipca = indexers.get_db_collection_by_indexer("IPCA")
    
    print(ipca.get_raw_dataframe())
    print(ipca.get_stacked_dataframe())
    print(ipca.get_stacked_dataframe_from_dates(datetime(2000,1,1), datetime(2000,12,1)))
    print(ipca.get_stacked_dataframe_from_values(1000, datetime(2000,1,1), datetime(2000,12,1)))
    print(ipca.get_stacked_dataframe_adjusted_from_values(1000, datetime(2000,1,1), datetime(2000,12,1), 200, interest.PROPORTIONAL_RATE))
    print(ipca.get_transposed_stacked_dataframe())

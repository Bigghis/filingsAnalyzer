import os
# from queries import get_query
from ..models.utils import get_embeddings
from .K10 import K10Query
from ..sec.sec import get_recent_folders, download_filings
from ..config import DB_PERSIST_DIRECTORY, SOURCE_SEC_DIRECTORY
from ..db.K10 import K10_DB

FILING_TYPE_10K = "10-K"

class QueryEngine:
    def __init__(self, symbol, type=FILING_TYPE_10K, key=None, save_to_txt_files=True, num_years=3):
        self.symbol = symbol
        self.type = type
        self.key = key
        self.save_to_txt_files = save_to_txt_files
        self.num_years = num_years
        self.available_years = []
        self.available_docs = []
        self.retriever = None
        self.queryInstance = None
        self._init_db()
        self._init_query()


    def _init_db(self):
        download_filings(self.symbol, self.type)
        self.persist_directory = f"{DB_PERSIST_DIRECTORY}/{self.symbol}/{self.type}_items_1_1a_7_7a_8"
        self.embeddings = get_embeddings()
        if self.type == FILING_TYPE_10K:
            self.db = K10_DB(self.persist_directory,
                             self.symbol,
                             self.embeddings,
                             save_to_txt_files=self.save_to_txt_files,
                             num_years=self.num_years)

            self.available_docs = self.db.get_available_documents()
            self.available_years = self.db.get_available_years()
            self.retriever = self.db.get_retriever_chain(self.available_years)
        else:
            raise ValueError(f"Invalid type: {self.type}")


    def _init_query(self):
        if self.type == FILING_TYPE_10K:
            self.queryInstance = K10Query(self.symbol, self.available_years)
        else:
            raise ValueError(f"Type Filings not supported: {self.type}")


    def _check_valid_key(self, key):
        if key in self.queryInstance.get_all_queries():
            return True
        else:
            return False


    def query(self):
        res = None
        if self._check_valid_key(self.key):
            if self.retriever and self.available_docs:
                if self.type == FILING_TYPE_10K:
                    query = self.queryInstance.get_query(self.key)
                    res = self.retriever.invoke(query)
                else:
                    raise ValueError(f"query() not implemented for type: {self.type}")
                return res
            else:
                raise ValueError("retriever, or available docs not found")
        else:
            raise ValueError("Invalid query key")


    def get_all_queries(self):
        """
        Returns all available keys for queries for a company's filings.
        """
        return self.queryInstance.get_all_queries()


    def get_query(self, key):
        """
        Returns the string query for a given key.
        """
        if self._check_valid_key(key):
            return self.queryInstance.get_query(key)
        else:
            raise ValueError("Invalid query key")

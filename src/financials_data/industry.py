import yfinance as yf
import pandas as pd
from ..utils.utils import sanitize_dataframe

class Industry:
    def __init__(self, key):
        self.key = key
        self.industry = yf.Industry(key)

    def get_overview(self):
        return self.industry.overview

    def get_top_companies(self):
        # Get initial top companies data
        res = sanitize_dataframe(self.industry.top_companies)
        
        for company in res:
            symbol = company['symbol']
            ticker = yf.Ticker(symbol)
            fast_info = ticker.fast_info
            
            # Update the dictionary with fast_info data
            company.update(fast_info)
        
        return res

import yfinance as yf
import pandas as pd
# from utils.utils import sanitize_dataframe

class Sector:
    def __init__(self, key):
        self.key = key
        self.sector = yf.Sector(key)

    def get_overview(self):
        return self.sector.overview

    # def get_top_companies(self):
    #     return sanitize_dataframe(self.sector.top_companies)

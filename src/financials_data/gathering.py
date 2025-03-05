import yfinance as yf
import pandas as pd
from ..utils.utils import sanitize_dataframe, sanitize_datetime_dataframe

class Gathering:
    def __init__(self, symbol):
        # uncomment to enable debug mode
        # yf.enable_debug_mode()

        self.symbol = symbol
        # Handle multiple symbols if comma-separated
        self.symbols = [s.strip() for s in symbol.split(',') if s.strip()]
        if not self.symbols:
            self.symbols = [symbol] 
        
        if len(self.symbols) > 1:
            self.ticker = yf.Tickers(self.symbols)
        else:
            self.ticker = yf.Ticker(self.symbols[0])
    

    def get_info(self):
        # print(self.ticker.upgrades_downgrades)
        #print(self.ticker.earnings_history)
        # print(self.ticker.revenue_estimate)
        #print(self.ticker.earnings)
        return self.ticker.info


    def get_prices(self, period, start_date=None, end_date=None):
        return yf.download(self.symbols, period=period, start=start_date, end=end_date)
    
    
    def get_holders(self):
        """Get and format holder information."""
        return {
            "institutional": sanitize_dataframe(self.ticker.institutional_holders),
            "insider_roster": sanitize_dataframe(self.ticker.insider_roster_holders),
            "major_holders": sanitize_dataframe(self.ticker.major_holders),
            "mutual_fund": sanitize_dataframe(self.ticker.mutualfund_holders)
        }
    
    def get_insider_transactions(self):
        """Get and format insider transactions and purchases."""
        return {
            "transactions": sanitize_dataframe(self.ticker.insider_transactions),
            "purchases": sanitize_dataframe(self.ticker.insider_purchases)
        }

    def get_balance_sheet(self, quarterly: bool = False):
        if quarterly:
            return sanitize_datetime_dataframe(self.ticker.quarterly_balance_sheet)
        else:
            return sanitize_datetime_dataframe(self.ticker.balance_sheet)
    
    def get_cash_flow(self, quarterly: bool = False):
        if quarterly:
            return sanitize_datetime_dataframe(self.ticker.quarterly_cashflow)
        else:
            return sanitize_datetime_dataframe(self.ticker.cashflow)
    
    def get_income_statement(self, quarterly: bool = False):
        if quarterly:
            return sanitize_datetime_dataframe(self.ticker.quarterly_income_stmt)
        else:
            return sanitize_datetime_dataframe(self.ticker.income_stmt)
    
    def get_dividends(self):
        """Get and format dividends data."""
        if self.ticker.dividends is None or self.ticker.dividends.empty:
            return {"data": []}
        
        # Convert Series to list of dictionaries with date handling
        dividends_list = [
            {
                "date": date.strftime("%Y-%m-%d"),
                "amount": float(amount)  # Ensure float values are JSON serializable
            }
            for date, amount in self.ticker.dividends.items()
        ]
        
        return {
            "data": dividends_list,
            "count": len(dividends_list)
        }
    
    def get_news(self):
        """Get and format news data."""
        if not self.ticker.news:
            return {"data": []}
        
        cleaned_news = []
        for news_item in self.ticker.news:
            # Create a clean news item with only the fields we want
            clean_item = {
                "title": news_item.get("title", ""),
                "publisher": news_item.get("publisher", ""),
                "link": news_item.get("link", ""),
                "providerPublishTime": news_item.get("providerPublishTime", ""),
                "type": news_item.get("type", ""),
                "relatedTickers": news_item.get("relatedTickers", []),
                "thumbnail": news_item.get("thumbnail", {}),
            }
            cleaned_news.append(clean_item)
        
        return {
            "data": cleaned_news,
            "count": len(cleaned_news)
        }


    # def get_earnings(self):
    #     return sanitize_datetime_dataframe(self.ticker.earnings_dates)
    
    # def get_institutional_holders(self):
    #     return self.ticker.institutional_holders
    
    # def get_insider_roster_holders(self):
    #     return self.ticker.insider_roster_holders
    
    # def get_mutualfund_holders(self):
    #     return self.ticker.mutualfund_holders



    def get_ticker(self):
        return self.ticker
    
    def get_capital_gains(self):
        return self.ticker.capital_gains


# def get_financials_data(ticker: str):
#     return yf.Ticker(ticker).financials

# print(get_financials_data("AAPL"))
#   
  
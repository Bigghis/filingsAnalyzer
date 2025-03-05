import os
import yfinance as yf

from financials_data.gathering import Gathering

# gathering = Gathering("mli")
#print(gathering.get_info())

# ticker  = gathering.get_ticker()
ticker = yf.Ticker("MED")

# ['1d', '5d', '1mo', '3mo', '1y', '5y', 'ytd', 'max']")

data1 = yf.download('MLI', period="5y")

print("\nData1 Info:")
print("Shape:", data1.shape)
print("\nColumns:", data1.columns.tolist())
print("\nIndex range:")
print("Start:", data1.index[0])
print("End:", data1.index[-1])


# data = ticker.history(period="1mo")

print(data1)


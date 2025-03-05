
import re
import pandas as pd
from fastapi import HTTPException
# Regex pattern for valid ticker symbols
# Allows comma-separated list of tickers, each 1-5 uppercase letters/numbers, optionally followed by a dot and more letters
TICKER_PATTERN = re.compile(r'^[A-Z0-9]{1,5}(\.[A-Z]{1,2})?(?:\s*,\s*[A-Z0-9]{1,5}(\.[A-Z]{1,2})?)*$')

def validate_ticker(ticker):
    if not TICKER_PATTERN.match(ticker):
        raise HTTPException(
            status_code=400,
            detail="Invalid ticker format. Ticker should be 1-5 characters, uppercase letters/numbers only."
        )

def validate_str_key(key):
    if not isinstance(key, str):
        raise HTTPException(
            status_code=400,
            detail="Invalid key format. Key should be a string."
        )

def sanitize_dataframe(df, orient="records"):
    """Sanitize DataFrame by converting problematic values to clean strings."""
    if df is None:
        return pd.DataFrame()
    
    df = df.copy()

    # Convert Int64 to float64 first to handle NA values properly
    for col in df.select_dtypes(include=['Int64']).columns:
        df[col] = df[col].astype('float64')

    # Replace all NaN values with empty strings    
    df = df.fillna("")
    
    # print(df.select_dtypes(include=['float64', 'int64']).columns)
    # Handle datetime columns
    datetime_cols = df.select_dtypes(include=['datetime64']).columns
    for col in datetime_cols:
        df[col] = df[col].astype(str).replace('NaT', '')
    
    # Handle numeric columns
    numeric_cols = df.select_dtypes(include=['float64', 'int64']).columns
    for col in numeric_cols:
        df[col] = df[col].astype(str).replace('nan', '')
        # df[col] = df[col].astype(str).replace('NaN', '')

    
    return df.reset_index().to_dict(orient=orient)


def sanitize_datetime_dataframe(df):
    """Convert DataFrame to dictionary with proper date formatting and NaN handling."""
    if df is None or df.empty:
        return {}
    
    # Create a copy and handle the data
    df = df.copy()
    
    # Convert the index (dates) to string format 'YYYY-MM-DD'
    result = {}
    for date in df.columns:
        date_str = date.strftime('%Y-%m-%d')
        
        # Create a dictionary for each date
        values = {}
        for index in df.index:
            value = df.loc[index, date]
            # Handle NaN values
            if pd.isna(value):
                values[index] = None
            else:
                # Convert float values to integers if they're whole numbers
                values[index] = int(value) if value.is_integer() else float(value)
        
        result[date_str] = values
    
    return result


def map_sort_field(sortField):
    
    sortField = sortField.lower()
    if sortField == "symbol":
        return "ticker"
    elif sortField == "marketcap":
        return "lastclosemarketcap.lasttwelvemonths"
    elif sortField == "regularmarketprice":
        return "eodprice"
    elif sortField == "trailingpe":
        return "peratio.lasttwelvemonths"
    elif sortField == "forwardpe":
        return "peratio.lasttwelvemonths"
    elif sortField == "dividendyield":
        return "forward_dividend_yield"
    elif sortField == "twoHundredDayAverageChangePercent":
        return "twohundreddayaveragechangepercent"
    else:
        return "ticker"
         
    # elif sortField == "twoHundredDayAverageChange":
    #     return "twohundreddayaveragechange"
    # elif sortField == "twoHundredDayAverage":
    #     return "twohundreddayaverage"
    return sortField

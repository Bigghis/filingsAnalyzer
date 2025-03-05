from typing import Annotated, Dict, Any
from fastapi import APIRouter, HTTPException
from fastapi_cache.decorator import cache
from redis.exceptions import RedisError
import logging
from ...utils.utils import validate_ticker
from src.financials_data.gathering import Gathering
import pandas as pd
from src.api.cache.config import CACHE_EXPIRATION_1HOUR, CACHE_EXPIRATION_1DAY
from src.api.cache.utils import custom_key_builder, use_cache
logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/prices",
    tags=["prices"]
)


async def get_prices_without_cache(symbol: str, period: str, start_date: str, end_date: str) -> Dict[str, Any]:
    """Fallback function when cache is unavailable"""
    gathering = Gathering(symbol)
    prices = gathering.get_prices(period, start_date, end_date)
    
    # Reset the index and flatten the column names
    prices = prices.reset_index()
    
    # Convert Timestamp to string format
    if 'Date' in prices.columns:
        prices['Date'] = prices['Date'].dt.strftime('%Y-%m-%d %H:%M:%S')
    
    if isinstance(prices.columns, pd.MultiIndex):
        prices.columns = [
            'Date' if col[0] == 'Date' else f"{col[0]}_{col[1]}" 
            for col in prices.columns
        ]
    
    # Convert DataFrame to JSON-compatible format
    prices_json = {
        "data": prices.to_dict(orient="records")
    }
    
    return prices_json

@router.get("/historical", response_model=Dict[str, Any])
@use_cache(
    expire=CACHE_EXPIRATION_1HOUR,
    namespace="stock_prices"
)
async def get_stock_prices(
        symbol: str,
        period: str,
        start_date: str = None,
        end_date: str = None,
    ):
    try:
        # Log cache attempt
        #cache_key = custom_key_builder(get_stock_prices, kwargs={'symbol': symbol, 'period': period})
        #logger.info(f"Attempting to fetch data with cache key: {cache_key}")

        # Validate inputs
        validate_ticker(symbol)
        valid_periods = ['1d', '5d', '1mo', '3mo', '1y', '5y', 'ytd', 'max']
        if period not in valid_periods:
            raise HTTPException(
                status_code=400,
                detail="Invalid period"
            )

        # Try to get data (will be cached by decorator)
        prices_json = await get_prices_without_cache(symbol, period, start_date, end_date)
        
        # Log successful response
        logger.info(f"Data fetched successfully for {symbol}")
        return prices_json

    except RedisError as e:
        logger.error(f"Cache error for {symbol}: {str(e)}")
        return await get_prices_without_cache(symbol, period, start_date, end_date)

    except Exception as e:
        logger.error(f"Error processing request for {symbol}: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Error processing request: {str(e)}"
        )
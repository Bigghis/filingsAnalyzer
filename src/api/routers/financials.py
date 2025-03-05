from typing import Annotated, Dict, Any
from fastapi import APIRouter, Depends, HTTPException
from fastapi_cache.decorator import cache
from redis.exceptions import RedisError
from src.financials_data.gathering import Gathering
from ..auth.security import get_current_user
from ..auth.models import User
from ...utils.utils import validate_ticker
from src.api.cache.config import CACHE_EXPIRATION_1DAY
from src.api.cache.utils import custom_key_builder, use_cache
import logging

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/financials",
    tags=["financials"]
)

@router.get("/info", response_model=Dict[str, Any])
@use_cache(
    expire=CACHE_EXPIRATION_1DAY,
    namespace="stock_info"
)
async def get_stock_info(symbol: str):
    """
    Get detailed stock information including company details, financial metrics, and market data.
    Returns a dictionary containing fields like address, industry, financials, etc.
    """
    try:
        # Validate ticker format
        validate_ticker(symbol)
        gathering = Gathering(symbol)
        info = gathering.get_info()
        if not info:
            raise HTTPException(status_code=404, detail="No information found for this ticker")
        return info
    except RedisError as e:
        logger.error(f"Cache error for {symbol}: {str(e)}")
        # Continue without cache
        return await get_stock_info(symbol)
    except Exception as e:
        logger.error(f"Error fetching data for {symbol}: {str(e)}")
        raise HTTPException(status_code=400, detail=f"Error fetching data: {str(e)}")

@router.get("/balance", response_model=Dict[str, Any])
@use_cache(
    expire=CACHE_EXPIRATION_1DAY,
    namespace="balance_sheet"
)
async def get_balance_sheet(symbol: str, quarterly: bool = False):
    """
    Get balance sheet data for a given ticker.
    """
    try:
        validate_ticker(symbol)
        gathering = Gathering(symbol)
        balance = gathering.get_balance_sheet(quarterly)
        if not balance:
            raise HTTPException(status_code=404, detail="No balance sheet data found for this ticker")
        return balance
    except RedisError as e:
        logger.error(f"Cache error for {symbol}: {str(e)}")
        # Continue without cache
        return await get_balance_sheet(symbol, quarterly)
    except Exception as e:
        logger.error(f"Error fetching data for {symbol}: {str(e)}")
        raise HTTPException(status_code=400, detail=f"Error fetching data: {str(e)}")

@router.get("/cashflow", response_model=Dict[str, Any])
@use_cache(
    expire=CACHE_EXPIRATION_1DAY,
    namespace="cash_flow"
)
async def get_cash_flow(symbol: str, quarterly: bool = False):
    """
    Get cash flow data for a given ticker.
    """
    try:
        validate_ticker(symbol)
        gathering = Gathering(symbol)
        cashflow = gathering.get_cash_flow(quarterly)
        if not cashflow:
            raise HTTPException(status_code=404, detail="No cash flow data found for this ticker")
        return cashflow
    except RedisError as e:
        logger.error(f"Cache error for {symbol}: {str(e)}")
        # Continue without cache
        return await get_cash_flow(symbol, quarterly)
    except Exception as e:
        logger.error(f"Error fetching data for {symbol}: {str(e)}")
        raise HTTPException(status_code=400, detail=f"Error fetching data: {str(e)}")

@router.get("/income", response_model=Dict[str, Any])
@use_cache(
    expire=CACHE_EXPIRATION_1DAY,
    namespace="income_statement"
)
async def get_income_statement(symbol: str, quarterly: bool = False):
    """
    Get income statement data for a given ticker.
    """ 
    try:
        validate_ticker(symbol)
        gathering = Gathering(symbol)
        income = gathering.get_income_statement(quarterly)
        if not income:
            raise HTTPException(status_code=404, detail="No income statement data found for this ticker")
        return income
    except RedisError as e:
        logger.error(f"Cache error for {symbol}: {str(e)}")
        # Continue without cache
        return await get_income_statement(symbol, quarterly)
    except Exception as e:
        logger.error(f"Error fetching data for {symbol}: {str(e)}")
        raise HTTPException(status_code=400, detail=f"Error fetching data: {str(e)}")

from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException
from src.financials_data.gathering import Gathering
from ..auth.security import get_current_user
from ..auth.models import User
from typing import Dict, Any
from ...utils.utils import validate_ticker

router = APIRouter(
    prefix="/stock",
    tags=["stock"]
)

@router.get("/news", response_model=Dict[str, Any])
async def get_stock_news(
        symbol: str,
        # current_user: Annotated[User, Depends(get_current_user)]
    ):
    """
    Get news data for a given ticker.
    """
    # Validate ticker format
    validate_ticker(symbol)
    try:
        gathering = Gathering(symbol)
        news = gathering.get_news()
        if not news:
            raise HTTPException(status_code=404, detail="No news found for this ticker")
        return news
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error fetching data: {str(e)}")
    

@router.get("/dividends", response_model=Dict[str, Any])
async def get_stock_dividends(
        symbol: str,
        # current_user: Annotated[User, Depends(get_current_user)]
    ):
    """Get dividends data for a given ticker."""
    validate_ticker(symbol)
    try:
        gathering = Gathering(symbol)
        dividends = gathering.get_dividends()
        return dividends
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error fetching data: {str(e)}")





# @router.get("/capital_gains", response_model=Dict[str, Any])
# async def get_capital_gains(
#         symbol: str,
#         # current_user: Annotated[User, Depends(get_current_user)]
#     ):
#     validate_ticker(symbol)
#     try:
#         gathering = Gathering(symbol)
#         # print(dir(gathering))
#         capital_gains = gathering.get_capital_gains()
#         return capital_gains
#     except Exception as e:
#         raise HTTPException(status_code=400, detail=f"Error fetching data: {str(e)}")

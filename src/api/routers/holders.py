from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException
from src.financials_data.gathering import Gathering
from ..auth.security import get_current_user
from ..auth.models import User
from typing import Dict, Any
from ...utils.utils import validate_ticker


router = APIRouter(
    prefix="/holders",
    tags=["holders"]
)


@router.get("/insiders", response_model=Dict[str, Any])
async def get_insiders(
        symbol: str,
        # period: str,
        # current_user: Annotated[User, Depends(get_current_user)]
    ):

    validate_ticker(symbol)
    gathering = Gathering(symbol)
    insiders = gathering.get_insider_transactions()
    # Convert DataFrame to JSON-compatible format
    if insiders is not None:
        insiders_json = {
            "data": insiders
        }
    else:
        insiders_json = {"data": []}

    return insiders_json

@router.get("/info", response_model=Dict[str, Any])
async def get_holders(
        symbol: str,
        # period: str,
        # current_user: Annotated[User, Depends(get_current_user)]
    ):

    validate_ticker(symbol)
    gathering = Gathering(symbol)
    holders = gathering.get_holders()

    if holders is not None:
        holders_json = {
            "data": holders
        }
    else:
        holders_json = {"data": []}

    return holders_json



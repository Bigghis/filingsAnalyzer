from typing import Annotated
from fastapi import APIRouter, HTTPException
from ...financials_data.industry import Industry
from ...financials_data.gathering import Gathering
from ..auth.security import get_current_user
from ..auth.models import User
from typing import Dict, Any, List
from ...utils.utils import validate_str_key

router = APIRouter(
    prefix="/industry",
    tags=["industry"]
)

@router.get("/overview", response_model=Dict[str, Any])
async def get_overview(
        key: str,
        # current_user: Annotated[User, Depends(get_current_user)]
    ):
    validate_str_key(key)
    try:
        industry = Industry(key)
        return industry.get_overview()
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error fetching data: {str(e)}")

@router.get("/top_companies", response_model=List[Dict[str, Any]])
async def get_top_companies(
        key: str,
        # current_user: Annotated[User, Depends(get_current_user)]
    ):
    validate_str_key(key)
    try:
        industry = Industry(key)
        return industry.get_top_companies()
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error fetching data: {str(e)}")

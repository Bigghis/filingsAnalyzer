from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException
from ...financials_data.screener import Screener
from ...financials_data.gathering import Gathering
from ..auth.security import get_current_user
from ..auth.models import User
from typing import Dict, Any
from ...utils.utils import validate_ticker

router = APIRouter(
    prefix="/screener",
    tags=["screener"]
)

@router.get("/predefined", response_model=Dict[str, Any])
async def get_predefined_bodies(
        # current_user: Annotated[User, Depends(get_current_user)]
    ):
    """
    Get screener data.
    """
    try:
        screener = Screener()
        screener_data = screener.get_predefined_bodies()
        if not screener_data:
            raise HTTPException(status_code=404, detail="No screener data found")
        return screener_data
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error fetching data: {str(e)}")
    
@router.get("/valid_equity_maps", response_model=Dict[str, Any])
async def get_valid_equity_maps(
        # current_user: Annotated[User, Depends(get_current_user)]
    ):
    try:    
        screener = Screener()
        return screener.get_valid_equity_maps() 
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error fetching data: {str(e)}")   


@router.get("/valid_equity_fields", response_model=Dict[str, Any])
async def get_valid_equity_fields(
        # current_user: Annotated[User, Depends(get_current_user)]
    ):
    try:    
        screener = Screener()
        return screener.get_valid_equity_fields() 
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error fetching data: {str(e)}")       
    
@router.post("/run", response_model=Dict[str, Any])
async def run(
        criteria: Dict[str, Any],
        # current_user: Annotated[User, Depends(get_current_user)]
    ):
    try:
        screener = Screener()
        return screener.run(criteria)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error fetching data: {str(e)}")
from fastapi import APIRouter, Depends, HTTPException, WebSocket, WebSocketDisconnect
from typing import Optional, List, Dict, Any
from ...queries.K10 import K10Query
from ...queries.QueryEngine import QueryEngine
import json
import asyncio
from typing import Annotated
from jose import jwt, JWTError

from ..auth.models import User
from ..auth.security import get_current_user, SECRET_KEY, ALGORITHM
from ..auth.database import get_user

WS_TIMEOUT_SECONDS = 300  # 5 minutes timeout

router = APIRouter(
    prefix="/queries",
    tags=["queries"]
)

@router.get("/execute/")
async def execute_query(
    current_user: Annotated[User, Depends(get_current_user)],
    symbol: str,
    key: str,
    filing_type: str = "10-K",
    save_to_txt: bool = True,
    num_years: int = 3
) -> Dict[str, Any]:
    """Execute a specific query for a company's filings"""
    try:
        engine = QueryEngine(
            symbol=symbol,
            type=filing_type,
            key=key,
            save_to_txt_files=save_to_txt,
            num_years=num_years
        )
        result = engine.query()
        
        if not result:
            raise HTTPException(
                status_code=404, 
                detail=f"No results found for query '{key}' on {symbol}'s {filing_type} filings"
            )
            
        return {
            "symbol": symbol,
            "query_key": key,
            "filing_type": filing_type,
            "result": result
        }
        
    except ValueError as ve:
        raise HTTPException(status_code=400, detail=str(ve))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/available/")
async def get_available_queries(
    current_user: Annotated[User, Depends(get_current_user)],
    symbol: str,
    filing_type: str = "10-K",
    num_years: int = 3
) -> Dict[str, Any]:
    """Get all available queries for a company's filings"""
    try:
        engine = QueryEngine(
            symbol=symbol,
            type=filing_type,
            key="dummy",
            num_years=num_years
        )
        queries = engine.get_all_queries()
        
        return {
            "symbol": symbol,
            "filing_type": filing_type,
            "available_queries": queries
        }
        
    except ValueError as ve:
        raise HTTPException(status_code=400, detail=str(ve))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/query/")
async def get_query_text(
    current_user: Annotated[User, Depends(get_current_user)],
    symbol: str,
    key: str,
    filing_type: str = "10-K",
    num_years: int = 3
) -> Dict[str, Any]:
    """Get the query text for a specific query key"""
    try:
        engine = QueryEngine(
            symbol=symbol,
            type=filing_type,
            key=key,
            num_years=num_years
        )
        query_text = engine.get_query(key)
        
        return {
            "symbol": symbol,
            "filing_type": filing_type,
            "key": key,
            "query_text": query_text
        }
        
    except ValueError as ve:
        raise HTTPException(status_code=400, detail=str(ve))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.websocket("/ws/execute/")
async def websocket_execute_query(
    websocket: WebSocket,
):
    """Execute a query via WebSocket connection"""
    await websocket.accept()
    
    try:
        async with asyncio.timeout(WS_TIMEOUT_SECONDS):
            # Receive the initial parameters as JSON
            data = await websocket.receive_json()
            
            # Extract parameters
            symbol = data.get("symbol")
            key = data.get("key")
            filing_type = data.get("filing_type", "10-K")
            save_to_txt = data.get("save_to_txt", True)
            num_years = data.get("num_years", 3)
            
            # Validate required parameters
            if not symbol or not key:
                await websocket.send_json({
                    "status": "error",
                    "message": "symbol and key are required parameters"
                })
                return
                
            # Send acknowledgment
            await websocket.send_json({
                "status": "processing",
                "message": f"Processing query '{key}' for {symbol}"
            })
            
            # Create query engine and execute query
            engine = QueryEngine(
                symbol=symbol,
                type=filing_type,
                key=key,
                save_to_txt_files=save_to_txt,
                num_years=num_years
            )
            
            # Execute query
            result = engine.query()
            
            if not result:
                await websocket.send_json({
                    "status": "error",
                    "message": f"No results found for query '{key}' on {symbol}'s {filing_type} filings"
                })
                return
                
            # Send final result
            await websocket.send_json({
                "status": "complete",
                "data": {
                    "symbol": symbol,
                    "query_key": key,
                    "filing_type": filing_type,
                    "result": result
                }
            })
            
    except WebSocketDisconnect:
        # Handle client disconnect
        print(f"Client disconnected")
    except ValueError as ve:
        await websocket.send_json({
            "status": "error",
            "message": str(ve)
        })
    except Exception as e:
        await websocket.send_json({
            "status": "error",
            "message": str(e)
        })
    finally:
        try:
            await websocket.close()
        except:
            pass

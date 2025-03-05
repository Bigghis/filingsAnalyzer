from fastapi import APIRouter, HTTPException
from src.api.cache.redis_client import RedisManager
import logging

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/health",
    tags=["health"]
)

@router.get("/")
async def check_cache_health():
    """Check if Redis cache is healthy"""
    try:
        redis_client = await RedisManager.get_client()
        await redis_client.ping()
        return {"status": "healthy", "cache": "connected"}
    except Exception as e:
        logger.error(f"Cache health check failed: {str(e)}")
        raise HTTPException(
            status_code=503,
            detail="Cache service unhealthy"
        ) 
    


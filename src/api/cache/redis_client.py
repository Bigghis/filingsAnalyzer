from redis import asyncio as aioredis
from redis.exceptions import RedisError
from fastapi import HTTPException
import logging
from typing import Optional
from .config import host, port, db, socket_timeout, retry_on_timeout, max_connections, health_check_interval, CACHE_ENABLED

logger = logging.getLogger(__name__)

class RedisManager:
    _instance: Optional[aioredis.Redis] = None

    @classmethod
    async def get_client(cls) -> Optional[aioredis.Redis]:
        """Get or create Redis client with retries"""
        if not CACHE_ENABLED:
            logger.info("Cache is disabled, skipping Redis connection")
            return None
            
        try:
            if cls._instance:
                # Use ping to check connection
                await cls._instance.ping()
                return cls._instance
            
            cls._instance = aioredis.Redis(
                host=host,
                port=port,
                db=db,
                decode_responses=True,
                socket_timeout=socket_timeout,
                retry_on_timeout=retry_on_timeout,
                max_connections=max_connections,
                health_check_interval=health_check_interval,
            )
            # Test the connection
            await cls._instance.ping()
            logger.info("Successfully connected to Redis")
            return cls._instance
        except RedisError as e:
            logger.error(f"Redis connection error: {str(e)}")
            cls._instance = None  # Reset instance on failure
            return None

    @classmethod
    async def close(cls):
        """Close Redis connection"""
        if cls._instance:
            try:
                await cls._instance.close()
                cls._instance = None
                logger.info("Redis connection closed")
            except RedisError as e:
                logger.error(f"Error closing Redis connection: {str(e)}") 
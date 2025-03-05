from functools import wraps
from fastapi_cache.decorator import cache as fastapi_cache
from .config import CACHE_ENABLED
import logging

logger = logging.getLogger(__name__)

def use_cache(expire=3600, namespace="default"):
    """
    Decorator that applies caching only if CACHE_ENABLED is True
    Args:
        expire: Cache expiration time in seconds (default: 3600)
        namespace: Cache namespace (default: "default")
    """
    def decorator(func):
        if not CACHE_ENABLED:
            # Return the original function if caching is disabled
            @wraps(func)
            async def wrapper(*func_args, **func_kwargs):
                return await func(*func_args, **func_kwargs)
            return wrapper
            
        try:
            # Apply FastAPI cache decorator with custom_key_builder
            return fastapi_cache(
                expire=expire,
                namespace=namespace,
                key_builder=custom_key_builder
            )(func)
        except AssertionError:
            # If FastAPICache is not initialized, log warning and return original function
            logger.warning("Cache not initialized, running without cache")
            @wraps(func)
            async def wrapper(*func_args, **func_kwargs):
                return await func(*func_args, **func_kwargs)
            return wrapper
            
    return decorator


def custom_key_builder(func, *args, **kwargs):
    """Custom key builder for cache"""
    # Convert args and kwargs to a string representation
    prefix = f"{func.__module__}:{func.__name__}"
    
    # Access the actual kwargs from the function parameters
    func_kwargs = kwargs.get('kwargs', {})
    # Get only the parameters we want to use in the cache key
    cache_key = f"{prefix}:symbol={func_kwargs.get('symbol', '')}"

    if func_kwargs.get('period', '') != '':
        cache_key += f":period={func_kwargs.get('period', '')}"
    
    if func_kwargs.get('quarterly', '') != '':
        cache_key += f":quarterly={func_kwargs.get('quarterly', '')}"

    print("cache_key= ", cache_key)
    return cache_key
    return cache_key
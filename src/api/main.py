from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi_cache import FastAPICache
from fastapi_cache.backends.redis import RedisBackend
from fastapi_cache.coder import Coder
import logging
from typing import Optional
from .routers import queries, auth, financials, prices, holders, stock, screener, industry, sector, health
from .auth.database import init_db
import os
from .cache.redis_client import RedisManager
import json
import sys
from src.api.cache.config import CACHE_ENABLED

app = FastAPI(
    title="Financial Analyst API",
    description="API for financial analysis",
    version="1.0.0"
)

PREFIX = "/api/v1"

# Configure CORS
origins = [
    "http://localhost:5173",  # Vite default port
    "http://localhost:3000",  # In case you use a different port
    "http://127.0.0.1:5173",
    "http://127.0.0.1:3000",
    # Add any other origins you want to allow
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins not recommended for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize the database
init_db()

# Configure logging at application startup
def setup_logging():
    # Create logger
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)

    # Create console handler with a higher log level
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.INFO)

    # Create formatter
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    console_handler.setFormatter(formatter)

    # Add console handler to the logger
    logger.addHandler(console_handler)

    return logger

# Setup logging before anything else
logger = setup_logging()

class CustomCoder(Coder):
    @classmethod
    def decode(cls, value: str) -> dict:
        # Value is already a string, no need to decode
        return json.loads(value)

    @classmethod
    def encode(cls, value: dict) -> str:
        return json.dumps(value)

@app.on_event("startup")
async def startup():
    """Startup event handler"""
    if CACHE_ENABLED:
        try:
            redis_client = await RedisManager.get_client()
            if redis_client is None:
                logger.warning("Redis client initialization failed. Application starting without cache service")
                return
                
            FastAPICache.init(
                RedisBackend(redis_client), 
                prefix="fastapi-cache",
                key_builder=None,
                expire=3600,
                coder=CustomCoder
            )
            logger.info("Cache service initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize cache service: {str(e)}")
            logger.warning("Application starting without cache service")
    else:
        logger.info("Cache service disabled via configuration")

@app.on_event("shutdown")
async def shutdown():
    """Shutdown event handler"""
    logger.info("Shutting down application")
    await RedisManager.close()

# Include routers
app.include_router(auth.router, prefix=PREFIX)
app.include_router(queries.router, prefix=PREFIX)
app.include_router(financials.router, prefix=PREFIX)
app.include_router(prices.router, prefix=PREFIX)
app.include_router(holders.router, prefix=PREFIX)
app.include_router(stock.router, prefix=PREFIX)
app.include_router(screener.router, prefix=PREFIX)
app.include_router(industry.router, prefix=PREFIX)
app.include_router(sector.router, prefix=PREFIX)
app.include_router(health.router, prefix=PREFIX)
# Add test-specific configuration
if os.getenv("TESTING"):
    from tests.mocks import MockQueryEngine
    import sys
    sys.modules['queries.QueryEngine'].QueryEngine = MockQueryEngine

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
import redis
import os
import json
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

router = APIRouter()

class ParserSettings(BaseModel):
    parser: str

def get_redis():
    redis_url = os.getenv("REDIS_URL", "redis://localhost:6379/0")
    return redis.from_url(redis_url)

@router.get("/")
async def get_settings():
    """
    Retrieve parser settings from Redis.
    Returns default value of 'pyresparser' if no setting is found.
    """
    try:
        redis_client = get_redis()
        settings = redis_client.get("settings:parser_preference")
        
        if settings:
            return {"parser": settings.decode('utf-8')}
        
        # Return default settings if none found
        return {"parser": "pyresparser"}
        
    except redis.RedisError as e:
        logger.error(f"Redis error while getting settings: {str(e)}")
        # Return default settings on Redis error
        return {"parser": "pyresparser"}
    except Exception as e:
        logger.error(f"Unexpected error while getting settings: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.post("/")
async def update_settings(settings: ParserSettings):
    """
    Update parser settings in Redis.
    """
    try:
        redis_client = get_redis()
        redis_client.set("settings:parser_preference", settings.parser)
        logger.info(f"Updated parser preference to: {settings.parser}")
        return {"status": "success", "parser": settings.parser}
        
    except redis.RedisError as e:
        logger.error(f"Redis error while updating settings: {str(e)}")
        raise HTTPException(
            status_code=503, 
            detail="Failed to save settings due to database error"
        )
    except Exception as e:
        logger.error(f"Unexpected error while updating settings: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error") 
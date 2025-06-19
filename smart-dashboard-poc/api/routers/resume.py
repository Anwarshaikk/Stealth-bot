import os
import uuid
import json
from fastapi import APIRouter, UploadFile, File, HTTPException, Query, Depends
from typing import List, Optional
from pyresparser import ResumeParser
from fastapi.responses import JSONResponse
from api.models import Candidate
import redis
from redis import Redis
import logging
from ..deps import get_redis_conn
from ..services.docai_parser import parse_with_docai
from ..services.gpt4_parser import parse_with_gpt4

router = APIRouter()
logger = logging.getLogger(__name__)

def get_redis() -> Redis:
    """Get Redis connection."""
    redis_url = os.getenv("REDIS_URL", "redis://localhost:6379/0")
    return redis.from_url(redis_url)

def ensure_storage_dir():
    """Ensure the storage directory exists."""
    save_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "storage", "resumes")
    os.makedirs(save_dir, exist_ok=True)
    return save_dir

@router.get("/", response_model=List[Candidate])
async def list_candidates(
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
    redis: Redis = Depends(get_redis)
):
    """Get a list of all candidates with pagination."""
    # Get all candidate keys
    candidate_keys = redis.keys("candidate:*")
    candidates = []
    
    # Get candidates for the requested page
    for key in candidate_keys[skip:skip + limit]:
        candidate_data = redis.get(key)
        if candidate_data:
            candidates.append(Candidate.parse_raw(candidate_data))
    
    return candidates

@router.get("/{candidate_id}", response_model=Candidate)
async def get_candidate(candidate_id: str, redis: Redis = Depends(get_redis)):
    """Get a specific candidate by their ID."""
    candidate_data = redis.get(f"candidate:{candidate_id}")
    if not candidate_data:
        raise HTTPException(status_code=404, detail="Candidate not found")
    return Candidate.parse_raw(candidate_data)

@router.post("/resume/upload")
async def create_resume(file: UploadFile = File(...)):
    try:
        # Create a temporary file to store the upload
        temp_path = f"/tmp/{file.filename}"
        permanent_path = f"uploads/{file.filename}"
        
        # Ensure the uploads directory exists
        os.makedirs("uploads", exist_ok=True)
        
        # Save the uploaded file
        with open(temp_path, "wb+") as file_object:
            file_object.write(await file.read())
            
        # Move to permanent location
        os.rename(temp_path, permanent_path)
        
        # Get Redis connection
        redis_conn = get_redis_conn()
        
        # Get parser preference from Redis
        parser_preference = redis_conn.get("settings:parser_preference")
        if parser_preference:
            parser_preference = parser_preference.decode("utf-8")
        else:
            parser_preference = "pyresparser"  # Default
            
        logger.info(f"Using '{parser_preference}' for resume parsing.")
        
        # Parse the resume using the selected parser
        try:
            if parser_preference == "docai":
                parsed_data = parse_with_docai(permanent_path)
            elif parser_preference == "gpt-4":
                parsed_data = parse_with_gpt4(permanent_path)
            else:  # Default to pyresparser
                parsed_data = ResumeParser(permanent_path).get_extracted_data()
                
            # Store the parsed data in Redis
            resume_key = f"resume:{file.filename}"
            redis_conn.hset(resume_key, mapping={
                "name": parsed_data.get("name", ""),
                "email": parsed_data.get("email", ""),
                "mobile_number": parsed_data.get("mobile_number", ""),
                "skills": ",".join(parsed_data.get("skills", [])),
                "experience": str(parsed_data.get("experience", [])),
                "education": str(parsed_data.get("education", [])),
                "file_path": permanent_path,
                "parser_used": parser_preference
            })
            
            return {
                "message": "Resume uploaded and parsed successfully",
                "parser_used": parser_preference,
                "parsed_data": parsed_data
            }
            
        except Exception as parsing_error:
            logger.error(f"Error parsing resume with {parser_preference}: {str(parsing_error)}")
            raise HTTPException(
                status_code=500,
                detail=f"Error parsing resume with {parser_preference}: {str(parsing_error)}"
            )
            
    except Exception as e:
        logger.error(f"Error processing resume upload: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Error processing resume upload: {str(e)}"
        )

from fastapi import APIRouter, Depends, HTTPException
from redis import Redis
from rq import Queue
from datetime import datetime
from uuid import uuid4
import json
from typing import List

from ..models import ApplyRequest, Application, ApplicationStatusUpdate
from ..deps import get_redis

router = APIRouter()

def get_queue(redis: Redis = Depends(get_redis)) -> Queue:
    return Queue(connection=redis)

@router.post("/")
async def apply_for_jobs(
    request: ApplyRequest,
    redis: Redis = Depends(get_redis),
    queue: Queue = Depends(get_queue)
):
    """Queue job applications for processing by the worker."""
    applications = []
    now = datetime.utcnow().isoformat()

    for job in request.jobs:
        # Create an application record
        application = Application(
            application_id=uuid4(),
            candidate_id=request.candidate_id,
            job_title=job.title,
            company=job.company,
            job_url=job.url,
            created_at=now,
            updated_at=now
        )

        # Store application in Redis
        redis_key = f"application:{application.application_id}"
        redis.set(redis_key, application.json())

        # Add to list of applications for this candidate
        candidate_apps_key = f"candidate:{request.candidate_id}:applications"
        redis.sadd(candidate_apps_key, str(application.application_id))

        # Queue the job application task
        queue.enqueue(
            "workers.apply_bot.apply_for_job",
            {
                "candidate_id": request.candidate_id,
                "job_url": job.url,
                "application_id": str(application.application_id)
            }
        )

        applications.append(application)

    return {
        "message": f"Successfully queued {len(applications)} job applications",
        "applications": applications
    }

@router.get("/applications", response_model=List[Application])
async def list_applications(redis: Redis = Depends(get_redis)):
    """List all tracked applications."""
    applications = []
    
    # Use scan_iter to efficiently iterate through all application keys
    for key in redis.scan_iter("application:*"):
        application_data = redis.get(key)
        if application_data:
            application = Application.parse_raw(application_data)
            applications.append(application)
    
    return applications

@router.patch("/applications/{application_id}", response_model=Application)
async def update_application_status(
    application_id: str,
    status_update: ApplicationStatusUpdate,
    redis: Redis = Depends(get_redis)
):
    """Update the status of a specific application."""
    # Construct the Redis key for the application
    redis_key = f"application:{application_id}"
    
    # Try to get the application from Redis
    application_data = redis.get(redis_key)
    if not application_data:
        raise HTTPException(status_code=404, detail="Application not found")
    
    # Parse the existing application data
    application = Application.parse_raw(application_data)
    
    # Update the status and updated_at timestamp
    application.status = status_update.status
    application.updated_at = datetime.utcnow().isoformat()
    
    # Save the updated application back to Redis
    redis.set(redis_key, application.json())
    
    return application

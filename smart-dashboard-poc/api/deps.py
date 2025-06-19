import os
from celery import Celery

def make_celery():
    redis_url = os.getenv("REDIS_URL", "redis://localhost:6379/0")
    return Celery("smartdash", broker=redis_url)

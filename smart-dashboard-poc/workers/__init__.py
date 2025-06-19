import os
from celery import Celery
from .fetch_jobs import rank_jobs
from .apply_bot import apply_job

redis_url = os.getenv("REDIS_URL", "redis://localhost:6379/0")
celery_app = Celery("smartdash", broker=redis_url)

celery_app.task(name="workers.fetch_jobs.rank_jobs")(rank_jobs)
celery_app.task(name="workers.apply_bot.apply_job")(apply_job) 
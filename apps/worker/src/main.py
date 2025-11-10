"""
Async Worker for background jobs.
"""

from celery import Celery
import os

# Configure Celery
redis_url = os.getenv("REDIS_URL", "redis://localhost:6379/2")

app = Celery(
    "pulse_worker",
    broker=redis_url,
    backend=redis_url,
    include=[
        "src.jobs.payments_webhooks",
        "src.jobs.video_finalize",
        "src.jobs.analytics",
        "src.jobs.cleanup",
    ]
)

# Celery configuration
app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    task_track_started=True,
    task_time_limit=3600,  # 1 hour max
    worker_prefetch_multiplier=1,
)

if __name__ == "__main__":
    app.start()


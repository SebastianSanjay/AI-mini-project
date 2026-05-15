from celery import Celery
from config import settings

celery_app = Celery(
    "linguafuse_worker",
    broker=settings.CELERY_BROKER_URL,
    backend=settings.CELERY_RESULT_BACKEND,
    include=["workers.tasks"]
)

celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    # Settings for long-running AI tasks
    task_acks_late=True,
    worker_prefetch_multiplier=1,
)

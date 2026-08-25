from celery import Celery

from src.core.config import settings

celery_app = Celery("video_downloader", broker=settings.celery_broker_url)

celery_app.conf.update(
    task_serializer="json",
    result_serializer="json",
    accept_content=["json"],
    timezone="UTC",
    enable_utc=True,
    task_track_started=True,
    task_acks_late=True,
    worker_prefetch_multiplier=1,
    include=["src.tasks.download"])

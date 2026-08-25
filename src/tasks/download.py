import redis
from celery import Celery
from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from src.core.config import settings
from src.core.utils import sanitize_filename
from src.models.download import DownloadStatus, DownloadTask

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
)

redis_client = redis.from_url(settings.redis_url, decode_responses=True)

sync_engine = create_engine(settings.database_url.replace("+asyncpg", ""))


def _progress_hook(task_id: str):
    def hook(d: dict) -> None:
        status = d.get("status", "")
        key = f"task:{task_id}:progress"
        if status == "downloading":
            total = d.get("total_bytes") or d.get("total_bytes_estimate") or 0
            downloaded = d.get("downloaded_bytes", 0)
            percent = (downloaded / total * 100) if total else 0
            redis_client.hset(key, mapping={
                "status": "downloading",
                "percent": f"{percent:.1f}",
                "speed": d.get("_speed_str", ""),
                "eta": d.get("_eta_str", ""),
                "downloaded": str(downloaded),
                "total": str(total),
            })
            redis_client.expire(key, 3600)
        elif status == "finished":
            redis_client.hset(key, mapping={
                "status": "completed",
                "percent": "100.0",
                "filename": d.get("filename", ""),
            })
            redis_client.expire(key, 3600)

    return hook


def _update_db_status(
    task_id: str,
    status: DownloadStatus,
    error: str | None = None,
    filename: str | None = None,
) -> None:
    with Session(sync_engine) as session:
        task = session.get(DownloadTask, task_id)
        if task:
            task.status = status
            if error:
                task.error_message = error
            if filename:
                task.filename = filename
            session.commit()


@celery_app.task
def download_video_task(task_id: str, url: str, title: str = "unknown", mode: str = "video", quality: str = "best") -> dict:
    from src.services.downloader import download_video

    output_name = sanitize_filename(title)
    try:
        hook = _progress_hook(task_id)
        filename = download_video(url, settings.downloads_path, progress_hook=hook, output_name=output_name, mode=mode, quality=quality)
        _update_db_status(task_id, DownloadStatus.completed, filename=filename)
        return {"task_id": task_id, "status": "completed", "filename": filename}
    except Exception as exc:
        redis_client.hset(
            f"task:{task_id}:progress",
            mapping={"status": "failed", "error": str(exc)},
        )
        _update_db_status(task_id, DownloadStatus.failed, error=str(exc))
        raise

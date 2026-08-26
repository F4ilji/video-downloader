import logging
from pathlib import Path

from src.core.config import settings
from src.tasks.celery_app import celery_app

logger = logging.getLogger(__name__)


@celery_app.task
def cleanup_downloads() -> dict:
    downloads_dir = Path(settings.downloads_path)
    if not downloads_dir.exists():
        return {"deleted": 0}

    deleted = 0
    for f in downloads_dir.iterdir():
        if f.is_file() and f.suffix in (".mp4", ".webm", ".mkv", ".avi", ".mov", ".m4a", ".json"):
            try:
                f.unlink()
                deleted += 1
                logger.info("Deleted: %s", f.name)
            except OSError as e:
                logger.error("Failed to delete %s: %s", f.name, e)

    return {"deleted": deleted}

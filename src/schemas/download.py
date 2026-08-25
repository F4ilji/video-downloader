import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict, HttpUrl

from src.models.download import DownloadStatus


class DownloadRequest(BaseModel):
    url: HttpUrl


class DownloadResponse(BaseModel):
    task_id: uuid.UUID
    celery_task_id: str | None = None
    status: DownloadStatus
    url: str


class TaskStatus(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    task_id: uuid.UUID
    celery_task_id: str | None = None
    status: DownloadStatus
    url: str
    title: str | None = None
    filename: str | None = None
    thumbnail: str | None = None
    duration: int | None = None
    progress: float = 0.0
    error_message: str | None = None
    created_at: datetime
    updated_at: datetime

import uuid
from datetime import datetime
from enum import Enum

from pydantic import BaseModel, ConfigDict, HttpUrl

from src.models.download import DownloadStatus


class DownloadMode(str, Enum):
    video = "video"
    audio = "audio"


class VideoQuality(str, Enum):
    best = "best"
    high = "high"
    medium = "medium"
    low = "low"


class DownloadRequest(BaseModel):
    url: HttpUrl
    mode: DownloadMode = DownloadMode.video
    quality: VideoQuality = VideoQuality.best


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

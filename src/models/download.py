import enum
import uuid
from datetime import datetime

from sqlalchemy import DateTime, String, Text, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    pass


class DownloadStatus(enum.StrEnum):
    pending = "pending"
    downloading = "downloading"
    completed = "completed"
    failed = "failed"


class DownloadTask(Base):
    __tablename__ = "download_tasks"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    celery_task_id: Mapped[str | None] = mapped_column(String(255), unique=True, index=True)
    url: Mapped[str] = mapped_column(Text)
    status: Mapped[DownloadStatus] = mapped_column(String(20), default=DownloadStatus.pending)
    title: Mapped[str | None] = mapped_column(Text)
    filename: Mapped[str | None] = mapped_column(Text)
    thumbnail: Mapped[str | None] = mapped_column(Text)
    duration: Mapped[int | None] = mapped_column()
    progress: Mapped[float] = mapped_column(default=0.0)
    error_message: Mapped[str | None] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

import asyncio
import json
import uuid
from collections.abc import AsyncGenerator
from pathlib import Path

import redis.asyncio as aioredis
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import FileResponse, StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.config import settings
from src.core.database import get_db
from src.core.utils import sanitize_filename
from src.models.download import DownloadTask
from src.schemas.download import DownloadMode, DownloadRequest, DownloadResponse, TaskStatus, VideoQuality
from src.services.downloader import extract_info

router = APIRouter()

redis_client = aioredis.from_url(settings.redis_url, decode_responses=True)

SSE_MAX_DURATION = 1800  # 30 minutes


@router.get("/health")
async def api_health() -> dict[str, str]:
    return {"status": "ok"}


@router.post("/download", response_model=DownloadResponse)
async def create_download(
    req: DownloadRequest,
    db: AsyncSession = Depends(get_db),  # noqa: B008
) -> DownloadResponse:
    url = str(req.url)
    task_id = uuid.uuid4()

    try:
        info = await asyncio.to_thread(extract_info, url)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to extract info: {e}") from e

    title = sanitize_filename(info.get("title", "unknown"))

    from src.tasks.download import download_video_task
    celery_result = download_video_task.delay(str(task_id), url, title, req.mode.value, req.quality.value)

    task = DownloadTask(
        id=task_id,
        celery_task_id=celery_result.id,
        url=url,
        title=title,
        thumbnail=info.get("thumbnail"),
        duration=info.get("duration"),
    )
    db.add(task)
    await db.commit()

    key = f"task:{task_id}:progress"
    await redis_client.hset(key, mapping={
        "status": "pending",
        "percent": "0",
        "url": url,
        "title": title,
        "thumbnail": info.get("thumbnail", ""),
    })
    await redis_client.expire(key, 3600)

    return DownloadResponse(
        task_id=task_id,
        celery_task_id=celery_result.id,
        status="pending",
        url=url,
    )


@router.get("/tasks/{task_id}", response_model=TaskStatus)
async def get_task_status(
    task_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),  # noqa: B008
) -> TaskStatus:
    result = await db.get(DownloadTask, task_id)
    if not result:
        raise HTTPException(status_code=404, detail="Task not found")

    key = f"task:{task_id}:progress"
    data = await redis_client.hgetall(key)

    return TaskStatus(
        task_id=task_id,
        celery_task_id=result.celery_task_id,
        status=data.get("status", result.status),
        url=result.url,
        title=result.title,
        filename=data.get("filename") or result.filename,
        thumbnail=result.thumbnail,
        duration=result.duration,
        progress=float(data.get("percent", result.progress)),
        error_message=data.get("error"),
        created_at=result.created_at,
        updated_at=result.updated_at,
    )


async def _sse_generator(task_id: uuid.UUID) -> AsyncGenerator[str, None]:
    key = f"task:{task_id}:progress"
    elapsed = 0

    while elapsed < SSE_MAX_DURATION:
        data = await redis_client.hgetall(key)
        if not data:
            yield f"data: {json.dumps({'error': 'Task not found'})}\n\n"
            return

        status = data.get("status", "unknown")
        payload = json.dumps({
            "status": status,
            "percent": data.get("percent", "0"),
            "speed": data.get("speed", ""),
            "eta": data.get("eta", ""),
            "filename": data.get("filename", ""),
            "error": data.get("error", ""),
        })
        yield f"data: {payload}\n\n"

        if status in ("completed", "failed"):
            return

        await asyncio.sleep(1)
        elapsed += 1

    yield f"data: {json.dumps({'error': 'SSE timeout'})}\n\n"


@router.get("/tasks/{task_id}/progress")
async def task_progress_sse(task_id: uuid.UUID) -> StreamingResponse:
    return StreamingResponse(
        _sse_generator(task_id),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "X-Accel-Buffering": "no",
        },
    )


@router.get("/download/{filename:path}")
async def serve_file(filename: str):
    file_path = Path(settings.downloads_path) / filename
    if not file_path.exists():
        raise HTTPException(status_code=404, detail="File not found")
    return FileResponse(
        path=file_path,
        media_type="video/mp4",
        filename=file_path.name,
    )


@router.get("/downloads")
async def list_downloads():
    downloads_dir = Path(settings.downloads_path)
    if not downloads_dir.exists():
        return []
    files = []
    for f in sorted(downloads_dir.iterdir(), key=lambda x: x.stat().st_mtime, reverse=True):
        if f.is_file() and f.suffix in ('.mp4', '.webm', '.mkv', '.avi', '.mov'):
            files.append({
                "filename": f.name,
                "size": f.stat().st_size,
                "url": f"/api/download/{f.name}",
            })
    return files

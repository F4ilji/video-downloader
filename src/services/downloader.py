from collections.abc import Callable
from typing import Any

import yt_dlp

from src.core.config import settings

QUALITY_FORMATS = {
    "best": "bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best",
    "high": "bestvideo[height<=1080][ext=mp4]+bestaudio[ext=m4a]/best[height<=1080][ext=mp4]/best",
    "medium": "bestvideo[height<=720][ext=mp4]+bestaudio[ext=m4a]/best[height<=720][ext=mp4]/best",
    "low": "bestvideo[height<=480][ext=mp4]+bestaudio[ext=m4a]/best[height<=480][ext=mp4]/best",
}


def _default_opts(
    output_path: str,
    output_name: str = "%(title)s [%(id)s]",
    progress_hook: Callable | None = None,
    mode: str = "video",
    quality: str = "best",
) -> dict[str, Any]:
    if mode == "audio":
        fmt = "bestaudio/best"
        merge_output: str | None = None
    else:
        fmt = QUALITY_FORMATS.get(quality, QUALITY_FORMATS["best"])
        merge_output = "mp4"

    opts: dict[str, Any] = {
        "outtmpl": f"{output_path}/{output_name}.%(ext)s",
        "format": fmt,
        "quiet": True,
        "no_warnings": True,
        "socket_timeout": 30,
        "retries": 10,
        "fragment_retries": 10,
        "concurrent_fragment_downloads": 16,
    }
    if merge_output:
        opts["merge_output_format"] = merge_output
    if settings.proxy:
        opts["proxy"] = settings.proxy
    if progress_hook:
        opts["progress_hooks"] = [progress_hook]
    return opts


def extract_info(url: str) -> dict[str, Any]:
    opts: dict[str, Any] = {"quiet": True, "no_warnings": True, "skip_download": True}
    if settings.proxy:
        opts["proxy"] = settings.proxy
    with yt_dlp.YoutubeDL(opts) as ydl:
        info = ydl.extract_info(url, download=False)
        return ydl.sanitize_info(info)  # type: ignore[no-any-return]


def download_video(
    url: str,
    output_path: str,
    output_name: str = "%(title)s [%(id)s]",
    progress_hook: Callable | None = None,
    mode: str = "video",
    quality: str = "best",
) -> str:
    opts = _default_opts(output_path, output_name, progress_hook, mode, quality)
    with yt_dlp.YoutubeDL(opts) as ydl:
        info = ydl.extract_info(url, download=True)
        if info is None:
            raise yt_dlp.utils.DownloadError("No info extracted")
        filename = ydl.prepare_filename(info)
        return filename

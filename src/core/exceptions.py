class AppError(Exception):
    def __init__(self, message: str = "Internal error", status_code: int = 500, code: str = "INTERNAL_ERROR") -> None:
        self.message = message
        self.status_code = status_code
        self.code = code
        super().__init__(self.message)


class UrlValidationError(AppError):
    def __init__(self, message: str = "Ссылка не распознана. Убедитесь, что это валидная ссылка на видео") -> None:
        super().__init__(message, status_code=400, code="URL_INVALID")


class DownloadError(AppError):
    def __init__(self, message: str | None = None) -> None:
        super().__init__(
            message or "Не удалось получить информацию о видео. Возможно, видео недоступно или было удалено",
            status_code=400,
            code="DOWNLOAD_FAILED",
        )


class TaskNotFoundError(AppError):
    def __init__(self, task_id: str | None = None) -> None:
        detail = f" (ID: {task_id})" if task_id else ""
        super().__init__(
            f"Задача не найдена. Возможно, она была удалена{detail}",
            status_code=404,
            code="TASK_NOT_FOUND",
        )


class ResourceNotFoundError(AppError):
    def __init__(self, filename: str | None = None) -> None:
        detail = f" ({filename})" if filename else ""
        super().__init__(
            f"Файл не найден. Возможно, он был удалён{detail}",
            status_code=404,
            code="FILE_NOT_FOUND",
        )


class TimeoutAppError(AppError):
    def __init__(self, message: str = "Превышено время ожидания. Попробуйте позже") -> None:
        super().__init__(message, status_code=504, code="TIMEOUT")


__all__ = [
    "AppError",
    "UrlValidationError",
    "DownloadError",
    "TaskNotFoundError",
    "ResourceNotFoundError",
    "TimeoutAppError",
]

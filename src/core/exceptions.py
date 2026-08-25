class AppError(Exception):
    def __init__(self, message: str = "Internal error") -> None:
        self.message = message
        super().__init__(self.message)


class DownloadError(AppError):
    def __init__(self, message: str = "Download failed") -> None:
        super().__init__(message)


class UrlValidationError(AppError):
    def __init__(self, message: str = "Invalid URL") -> None:
        super().__init__(message)


class TaskNotFoundError(AppError):
    def __init__(self, task_id: str) -> None:
        super().__init__(f"Task {task_id} not found")

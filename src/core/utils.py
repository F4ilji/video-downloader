import re


def sanitize_filename(title: str, max_length: int = 200) -> str:
    sanitized = re.sub(r'[<>:"/\\|?*]', "_", title)
    sanitized = sanitized.replace("%", "%%")
    return sanitized[:max_length]

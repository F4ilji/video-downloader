FROM python:3.12-slim

RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        ffmpeg \
        libmagic1 \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /code

COPY pyproject.toml .
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -e ".[dev]"

COPY src/ src/
COPY tests/ tests/

RUN mkdir -p /downloads && chmod 755 /downloads

CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000"]

# Video Downloader

Сервис для скачивания видео с YouTube и других платформ.

## Возможности

- Скачивание видео с YouTube, VK, Rutube и других платформ
- Выбор качества видео (best, high, medium, low)
- Скачивание аудио
- Прогресс скачивания в реальном времени

## Запуск

```bash
docker compose up -d
```

## Технологии

- Python 3.12 + FastAPI
- Celery + Redis (очередь задач)
- PostgreSQL (хранение задач)
- yt-dlp (скачивание видео)
- Vue 3 (фронтенд)

## API

- `POST /api/download` — скачивание видео
- `GET /api/tasks/{task_id}` — статус задачи
- `GET /api/tasks` — список задач

## Конфигурация

Переменные окружения (с префиксом `APP_`):

- `APP_DATABASE_URL` — URL базы данных
- `APP_REDIS_URL` — URL Redis
- `APP_DOWNLOADS_PATH` — путь для сохранения видео
- `APP_PROXY` — прокси (socks5://host:port)
- `APP_YT_CLIENT` — клиент YouTube (по умолчанию: mweb)

## Обход ограничений YouTube

### Вариант 1: PO Token Provider (рекомендуется)

1. Запустите PO Token сервер:
   ```bash
   docker run -d -p 4416:4416 brainicism/bgutil-ytdlp-pot-provider
   ```

2. Установите плагин:
   ```bash
   pip install bgutil-ytdlp-pot-provider
   ```

3. Перезапустите сервис:
   ```bash
   docker compose down && docker compose up -d
   ```

### Вариант 2: Cookies

1. Экспортируйте cookies из браузера:
   ```bash
   yt-dlp --cookies-from-browser chrome --cookies cookies.txt --skip-download "https://www.youtube.com"
   ```

2. Добавьте volume в docker-compose.yml:
   ```yaml
   volumes:
     - ./cookies.txt:/cookies.txt
   ```

3. Добавьте переменную окружения:
   ```yaml
   environment:
     - APP_YT_DLP_COOKIES_PATH=/cookies.txt
   ```

## Лицензия

MIT

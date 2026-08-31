# Memory
*Generated from facts.jsonl at 2026-08-31T08:53:42.947Z*

## infra
- [2026-08-26] Production deployment uses .env file for secrets, not hardcoded values in docker-compose.yml → Must create .env from .env.example before deploying (confidence: 0.95)

## tasks
- [2026-08-26] Duplicate Celery app in download.py (line 10) caused tasks to register on wrong app instance. Server worker couldn't route tasks properly. Fixed by importing from celery_app.py. → Always import celery_app from central config, never create local instances in task modules (confidence: 0.95)

## general
- [2026-08-25] *Generated from facts.jsonl at 2026-08-25T13:06:16.114Z* → N/A (confidence: 0.8)
- [2026-08-25] - [2026-08-25] AGENTS.md заполнен для video-downloader: Python 3.12, FastAPI, Celery, Redis, PostgreSQL, Vue.js 3, yt-dlp. Clean Architecture. Docker compose service=api. Preflight: pytest, ruff, mypy. → Все последующие задачи должны следовать описанной архитектуре и conventions из AGENTS.md (confidence: 1) → N/A (confidence: 0.8)
- [2026-08-25] - [2026-08-25] Pre-flight настроен и работает через Docker: compileall, ruff, pytest. Docker сервисы: api (8000), worker, redis (6380), postgres (5433). config.json: service="api". → Плагин opencode выполняет pre-flight проверки через docker compose exec -T api. (confidence: 1) → N/A (confidence: 0.8)

## downloader
- [2026-08-25] YouTube требует свежие cookies для обхода проверки на бота. Cookies устаревают через несколько часов/дней. Решение: экспортировать cookies из браузера через --cookies-from-browser. → Пользователи должны регулярно обновлять cookies.txt для работы с YouTube. (confidence: 0.95)
- [2026-08-25] Добавлена автоматизация обновления YouTube cookies: скрипт scripts/update-cookies.sh с cron каждые 30 минут и автоматический retry при ошибке бота. → Пользователи могут запустить ./scripts/update-cookies.sh setup-cron для автоматического обновления cookies. (confidence: 0.95)
- [2026-08-25] Заменена зависимость от cookies на PO Token Provider (bgutil-ytdlp-pot-provider). Теперь видео скачиваются без cookies, автоматически генерируя PO Token. → Сервис работает на любом сервере без необходимости установки браузера или ручного обновления cookies. (confidence: 0.95)
- [2026-08-25] Прокси xray работает корректно. Для исправления проблемы с SSL нужно было добавить debug логирование и outbound для direct соединения. → Прокси xray работает, YouTube доступен через прокси. (confidence: 0.95)
- [2026-08-25] cookies.txt из корня проекта работает для обхода LOGIN_REQUIRED. cookies.txt монтируется в api/worker как /cookies.txt:ro. → Для видео с ограничениями (age-restricted, приватные) нужно обновлять cookies.txt из браузера. (confidence: 0.95)
- [2026-08-25] Создан Dockerfile.cookie-provider и scripts/cookie_provider.py для автоматического обновления YouTube cookies через Playwright → Теперь cookies обновляются автоматически каждые 30 минут,不需要 ручного вмешательства (confidence: 0.95)

## frontend
- [2026-08-25] Frontend uses vanilla CSS with CSS custom properties for design tokens (defined in App.vue :root). No Tailwind. Font: Inter from Google Fonts. Color palette follows strict minimalist spec: #FFFFFF/#FAFAFA backgrounds, #09090B/#6B7280 text, #38BDF8 accent. → All future frontend styling should reference CSS custom properties (--bg-base, --text-primary, --accent, etc.) rather than hardcoded colors. Keep consistent with the minimalist design system. (confidence: 0.95)
- [2026-08-25] DownloadForm now auto-checks URL on input (600ms debounce) and shows inline preview with thumbnail, title, audio checkbox, quality dropdown. No modal. ProgressBar uses SVG circle with stroke-dashoffset animation. → New UX flow: paste URL → preview appears → set options → download. Circular progress uses CSS transition on stroke-dashoffset property. (confidence: 0.95)

## api
- [2026-08-25] New endpoint GET /api/video-info?url= returns video metadata (title, thumbnail, duration) without starting a download. Uses extract_info() from downloader service. → Frontend can now fetch video preview info before user commits to download. Endpoint may be slow (2-5s) due to yt-dlp metadata extraction. (confidence: 0.95)


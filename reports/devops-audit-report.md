# DevOps Audit Report

**Дата:** 2026-04-04  
**Репозиторий:** c:/Users/ndppd/Desktop/.cursor  
**Аудитор:** DevOps Agent

---

## 1. Управление зависимостями

### 1.1. [`tg_bot/requirements.txt`](tg_bot/requirements.txt:1) — пустой файл зависимостей

- **Категория:** Dependency Management
- **Критичность:** HIGH
- **Описание:** Файл [`tg_bot/requirements.txt`](tg_bot/requirements.txt:1) содержит только комментарии: "Бот использует только стандартную библиотеку Python. Отдельные pip-зависимости сейчас не требуются." Однако код [`tg_bot/main.py`](tg_bot/main.py:9) импортирует модули `telegram_api` и `state_store`, которые не являются частью стандартной библиотеки Python. Это означает, что либо эти модули — локальные файлы (что требует проверки), либо зависимости не задокументированы.
- **Рекомендации:**
  1. Проверить, являются ли `telegram_api` и `state_store` локальными модулями. Если да — добавить комментарий с указанием их расположения.
  2. Если бот использует внешнюю библиотеку для Telegram API (например, `python-telegram-bot` или `aiogram`), добавить её в `requirements.txt` с фиксированной версией.
  3. Использовать формат `package==x.y.z` для всех зависимостей (pinning).
  4. Добавить `pip-compile` или `pip-tools` для управления транзитивными зависимостями.

### 1.2. Отсутствие `pyproject.toml` / `setup.cfg`

- **Категория:** Project Configuration
- **Критичность:** MEDIUM
- **Описание:** Проект не использует современные стандарты упаковки Python (PEP 517/518). Отсутствует `pyproject.toml`, который является стандартом де-факто для определения метаданных проекта, зависимостей, конфигурации линтеров и тестовых фреймворков.
- **Рекомендации:**
  1. Создать `pyproject.toml` с минимальной конфигурацией:
     ```toml
     [project]
     name = "cursor-tg-bot"
     version = "0.1.0"
     requires-python = ">=3.11"
     dependencies = []

     [tool.ruff]
     line-length = 120

     [tool.pytest.ini_options]
     testpaths = ["tests"]
     ```
  2. Перенести зависимости из `requirements.txt` в `pyproject.toml`.
  3. Добавить `requirements.txt` как артефакт для `pip install -r requirements.txt` (генерировать через `pip-compile`).

### 1.3. Отсутствие lock-файла (requirements.txt.lock / Pipfile.lock / poetry.lock)

- **Категория:** Reproducible Builds
- **Критичность:** HIGH
- **Описание:** Нет механизма гарантировать воспроизводимость сборок. Без lock-файла каждый `pip install` может установить разные версии транзитивных зависимостей, что приводит к недетерминированным результатам в CI и production.
- **Рекомендации:**
  1. Внедрить `pip-tools`: запустить `pip-compile requirements.in -o requirements.txt`.
  2. Альтернатива: перейти на `uv` (быстрый менеджер зависимостей) с `uv pip compile`.
  3. Зафиксировать lock-файл в VCS.

### 1.4. Версия Python в CI/CD — только 3.11

- **Категория:** CI/CD Matrix
- **Критичность:** LOW
- **Описание:** Workflow [`repo-validation.yml`](.github/workflows/repo-validation.yml:19) использует только Python 3.11. Это не позволяет обнаружить проблемы совместимости с другими версиями (3.12, 3.13).
- **Рекомендации:**
  1. Добавить матрицу тестирования:
     ```yaml
     strategy:
       matrix:
         python-version: ["3.11", "3.12", "3.13"]
     ```
  2. Указать `requires-python = ">=3.11"` в `pyproject.toml`.

### 1.5. Отсутствие `.python-version` файла

- **Категория:** Developer Experience
- **Критичность:** LOW
- **Описание:** Нет файла `.python-version` для менеджеров версий Python (pyenv, uv). Разработчики могут использовать несовместимые версии.
- **Рекомендации:**
  1. Создать файл `.python-version` с содержимым `3.11`.
  2. Добавить проверку версии в CI.

---

## 2. CI/CD конфигурация

### 2.1. [`repo-validation.yml`](.github/workflows/repo-validation.yml:1) — отсутствие security scanning

- **Категория:** Security
- **Критичность:** HIGH
- **Описание:** Workflow не включает сканирование уязвимостей зависимостей (Dependabot) и статический анализ безопасности кода (CodeQL).
- **Рекомендации:**
  1. Включить Dependabot — создать `.github/dependabot.yml`:
     ```yaml
     version: 2
     updates:
       - package-ecosystem: "pip"
         directory: "/tg_bot"
         schedule:
           interval: "weekly"
       - package-ecosystem: "github-actions"
         directory: "/"
         schedule:
           interval: "weekly"
     ```
  2. Добавить CodeQL analysis workflow:
     ```yaml
     name: "CodeQL"
     on:
       push:
         branches: [main]
       pull_request:
         branches: [main]
       schedule:
         - cron: '0 6 * * 1'
     jobs:
       analyze:
         runs-on: ubuntu-latest
         permissions:
           security-events: write
         steps:
           - uses: actions/checkout@v4
           - uses: github/codeql-action/init@v3
             with:
               languages: python
           - uses: github/codeql-action/analyze@v3
     ```

### 2.2. Отсутствие автоматического релиза / версионирования

- **Категория:** Release Management
- **Критичность:** MEDIUM
- **Описание:** Нет workflow для автоматического создания релизов, тегирования и генерации changelog.
- **Рекомендации:**
  1. Добавить workflow на основе Conventional Commits:
     ```yaml
     name: Release
     on:
       push:
         branches: [main]
     jobs:
       release:
         runs-on: ubuntu-latest
         permissions:
           contents: write
           issues: write
           pull-requests: write
         steps:
           - uses: googleapis/release-please-action@v4
             with:
               token: ${{ secrets.GITHUB_TOKEN }}
               release-type: simple
     ```
  2. Альтернатива: использовать `semantic-release` или `python-semantic-release`.

### 2.3. Отсутствие coverage reporting

- **Категория:** Quality Gates
- **Критичность:** MEDIUM
- **Описание:** CI не измеряет и не отчитывается о покрытии кода тестами. Нет конфигурации pytest/coverage.
- **Рекомендации:**
  1. Создать директорию `tests/` с тестами для `tg_bot/`.
  2. Добавить шаг coverage в workflow:
     ```yaml
     - name: Run tests with coverage
       run: |
         pip install pytest pytest-cov
         pytest --cov=tg_bot --cov-report=xml
     - name: Upload coverage
       uses: codecov/codecov-action@v4
     ```

### 2.4. Отсутствие линтинга и форматирования в CI

- **Категория:** Code Quality
- **Критичность:** MEDIUM
- **Описание:** Workflow не запускает линтеры (ruff, flake8, mypy) или форматтеры (black).
- **Рекомендации:**
  1. Добавить шаг линтинга:
     ```yaml
     - name: Lint
       run: |
         pip install ruff mypy
         ruff check .
         ruff format --check .
         mypy tg_bot/
     ```

### 2.5. Дублирование jobs для Unix/Windows без общей конфигурации

- **Категория:** CI/CD Best Practices
- **Критичность:** LOW
- **Описание:** Jobs `validate-unix` и `validate-windows` дублируют шаги. При добавлении новых шагов нужно обновлять оба job.
- **Рекомендации:**
  1. Использовать матрицу:
     ```yaml
     jobs:
       validate:
         runs-on: ${{ matrix.os }}
         strategy:
           matrix:
             os: [ubuntu-latest, windows-latest]
         steps:
           # общие шаги
     ```

### 2.6. Отсутствие триггеров для schedule и manual dispatch

- **Категория:** CI/CD Triggers
- **Критичность:** LOW
- **Описание:** Workflow запускается только на push/pull_request. Нет периодического запуска (cron) для мониторинга деградации и ручного запуска (workflow_dispatch).
- **Рекомендации:**
  1. Добавить триггеры:
     ```yaml
     on:
       pull_request:
       push:
         branches: [main]
       schedule:
         - cron: '0 9 * * 1'  # каждый понедельник в 9:00 UTC
       workflow_dispatch:
     ```

---

## 3. Инфраструктура деплоя

### 3.1. [`tg_bot/install_service.py`](tg_bot/install_service.py:1) — установка служб без секрет-менеджмента

- **Категория:** Secret Management
- **Критичность:** CRITICAL
- **Описание:** Сервис запускается с токеном Telegram из `.env` файла. Файл `.env` находится в `.gitignore`, но нет механизма безопасной доставки секретов на production-машину. Токен хранится в plaintext.
- **Рекомендации:**
  1. Для production: использовать secrets manager (HashiCorp Vault, AWS Secrets Manager, Azure Key Vault).
  2. Для systemd: использовать `EnvironmentFile=` с ограниченным доступом (`chmod 600`).
  3. Добавить валидацию прав доступа к `.env` файлу при запуске:
     ```python
     import stat
     mode = env_path.stat().st_mode
     if mode & stat.S_IRGRP or mode & stat.S_IROTH:
         raise RuntimeError(".env file must be readable only by owner (chmod 600)")
     ```

### 3.2. Отсутствие Docker/containerization

- **Категория:** Infrastructure
- **Критичность:** HIGH
- **Описание:** Бот деплоится напрямую на хост через systemd/launchd/schtasks. Нет контейнеризации, что усложняет:
  - Воспроизводимость окружения
  - Масштабирование
  - Изоляцию зависимостей
  - Rollback
- **Рекомендации:**
  1. Создать `Dockerfile`:
     ```dockerfile
     FROM python:3.11-slim
     WORKDIR /app
     COPY tg_bot/requirements.txt .
     RUN pip install --no-cache-dir -r requirements.txt
     COPY tg_bot/ .
     RUN useradd -m appuser && chown -R appuser:appuser /app
     USER appuser
     CMD ["python", "main.py"]
     ```
  2. Создать `docker-compose.yml`:
     ```yaml
     services:
       tg-bot:
         build:
           context: .
           dockerfile: Dockerfile
         env_file:
           - tg_bot/.env
         restart: unless-stopped
         volumes:
           - tg-bot-data:/app/runtime
     volumes:
       tg-bot-data:
     ```
  3. Добавить `.dockerignore`.

### 3.3. Отсутствие health check endpoint

- **Категория:** Monitoring / Reliability
- **Критичность:** HIGH
- **Описание:** Бот не предоставляет HTTP health check endpoint. systemd/launchd могут определить только crash процесса, но не деградацию (например, потеря связи с Telegram API).
- **Рекомендации:**
  1. Добавить простой HTTP health endpoint в `main.py` (через встроенный `http.server` или aiohttp):
     ```python
     from http.server import HTTPServer, BaseHTTPRequestHandler
     class HealthHandler(BaseHTTPRequestHandler):
         def do_GET(self):
             if self.path == "/health":
                 self.send_response(200)
                 self.end_headers()
                 self.wfile.write(b"OK")
             else:
                 self.send_response(404)
     ```
  2. Для Docker: добавить `HEALTHCHECK`:
     ```dockerfile
     HEALTHCHECK --interval=30s --timeout=5s --retries=3 \
       CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8080/health')"
     ```
  3. Для systemd: добавить `ExecStartPre` проверку.

### 3.4. Отсутствие мониторинга и алертинга

- **Категория:** Observability
- **Критичность:** HIGH
- **Описание:** Нет интеграции с системами мониторинга (Prometheus, Grafana, Sentry). Heartbeat-файлы ([`tg_bot/main.py`](tg_bot/main.py:318)) пишутся в локальную файловую систему, но не отправляются во внешнюю систему.
- **Рекомендации:**
  1. Добавить метрики (prometheus-client):
     ```python
     from prometheus_client import Counter, start_http_server
     events_processed = Counter('tg_bot_events_processed_total', 'Total events processed')
     ```
  2. Интегрировать Sentry для отслеживания ошибок:
     ```python
     import sentry_sdk
     sentry_sdk.init(dsn=os.environ["SENTRY_DSN"])
     ```
  3. Настроить алерты на:
     - Отсутствие heartbeat > 5 минут
     - Rate limit от Telegram API
     - Ошибки обработки событий

### 3.5. Отсутствие graceful shutdown

- **Категория:** Reliability
- **Критичность:** MEDIUM
- **Описание:** [`tg_bot/main.py`](tg_bot/main.py:293) использует бесконечный `while True` цикл без обработки сигналов (SIGTERM, SIGINT). При остановке сервиса данные могут быть потеряны (необработанные события, несохранённый offset).
- **Рекомендации:**
  1. Добавить обработчик сигналов:
     ```python
     import signal
     import threading

     shutdown_event = threading.Event()

     def handle_signal(signum, frame):
         logging.info("Received signal %s, shutting down...", signum)
         shutdown_event.set()

     signal.signal(signal.SIGTERM, handle_signal)
     signal.signal(signal.SIGINT, handle_signal)

     while not shutdown_event.is_set():
         # ... основной цикл
         shutdown_event.wait(timeout=config.poll_interval_sec)
     ```
  2. Сохранять текущий offset перед выходом.

### 3.6. Отсутствие rate limiting и retry policy

- **Категория:** Reliability
- **Критичность:** MEDIUM
- **Описание:** При ошибке Telegram API бот ждёт фиксированное время ([`tg_bot/main.py`](tg_bot/main.py:327): `time.sleep(max(config.poll_interval_sec, 5))`). Нет экспоненциального backoff, что может привести к rate limit бану.
- **Рекомендации:**
  1. Реализовать exponential backoff с jitter:
     ```python
     import random

     def calculate_backoff(attempt, base=5, max_wait=300):
         wait = min(base * (2 ** attempt), max_wait)
         return wait + random.uniform(0, wait * 0.1)  # jitter
     ```
  2. Отслеживать HTTP 429 (Too Many Requests) и соблюдать `Retry-After` заголовок.

### 3.7. systemd service — отсутствие Security Hardening

- **Категория:** Security
- **Критичность:** MEDIUM
- **Описание:** systemd unit ([`tg_bot/install_service.py`](tg_bot/install_service.py:38)) не использует security директивы.
- **Рекомендации:**
  1. Добавить security hardening в unit:
     ```ini
     [Service]
     NoNewPrivileges=true
     ProtectSystem=strict
     ProtectHome=true
     ReadWritePaths=/path/to/tg_bot/runtime
     PrivateTmp=true
     ProtectKernelTunables=true
     ProtectControlGroups=true
     RestrictSUIDSGID=true
     ```

### 3.8. Отсутствие CI/CD для деплоя

- **Категория:** CI/CD
- **Критичность:** MEDIUM
- **Описание:** Нет автоматического деплоя после прохождения валидации. Деплой выполняется вручную через `bootstrap.py`.
- **Рекомендации:**
  1. Для self-hosted runner: добавить job deploy:
     ```yaml
     deploy:
       needs: validate
       if: github.ref == 'refs/heads/main'
       runs-on: self-hosted
       steps:
         - uses: actions/checkout@v4
         - name: Deploy
           run: |
             cd tg_bot
             python bootstrap.py --no-service
             systemctl --user restart cursor_tg_bot
     ```

---

## Сводная таблица проблем

| # | Файл | Строка | Категория | Критичность | Описание |
|---|------|--------|-----------|-------------|----------|
| 1 | `tg_bot/install_service.py` | 176 | Secret Management | **CRITICAL** | Токен Telegram в plaintext без защиты |
| 2 | `tg_bot/requirements.txt` | 1 | Dependency Management | **HIGH** | Пустой файл, зависимости не задокументированы |
| 3 | Отсутствует | — | Reproducible Builds | **HIGH** | Нет lock-файла зависимостей |
| 4 | Отсутствует | — | Infrastructure | **HIGH** | Нет Docker/containerization |
| 5 | `tg_bot/main.py` | 293 | Monitoring | **HIGH** | Нет health check endpoint |
| 6 | Отсутствует | — | Observability | **HIGH** | Нет мониторинга/алертинга |
| 7 | `.github/workflows/repo-validation.yml` | 1 | Security | **HIGH** | Нет Dependabot/CodeQL scanning |
| 8 | `tg_bot/main.py` | 293 | Reliability | **MEDIUM** | Нет graceful shutdown |
| 9 | `tg_bot/main.py` | 327 | Reliability | **MEDIUM** | Нет exponential backoff |
| 10 | `tg_bot/install_service.py` | 38 | Security | **MEDIUM** | systemd без security hardening |
| 11 | Отсутствует | — | Release Management | **MEDIUM** | Нет автоматического релиза |
| 12 | Отсутствует | — | Quality Gates | **MEDIUM** | Нет coverage reporting |
| 13 | Отсутствует | — | Code Quality | **MEDIUM** | Нет линтинга в CI |
| 14 | Отсутствует | — | CI/CD | **MEDIUM** | Нет CI/CD деплоя |
| 15 | Отсутствует | — | Project Configuration | **MEDIUM** | Нет pyproject.toml |
| 16 | `.github/workflows/repo-validation.yml` | 19 | CI/CD Matrix | **LOW** | Только Python 3.11 |
| 17 | `.github/workflows/repo-validation.yml` | 1 | CI/CD Triggers | **LOW** | Нет schedule/workflow_dispatch |
| 18 | `.github/workflows/repo-validation.yml` | 10 | CI/CD Best Practices | **LOW** | Дублирование jobs |
| 19 | Отсутствует | — | Developer Experience | **LOW** | Нет .python-version |

---

## Приоритетный план действий

### Фаза 1: Критические исправления (неделя 1)
1. Задокументировать зависимости в `requirements.txt` с фиксированными версиями
2. Внедрить lock-файл (pip-tools или uv)
3. Добавить валидацию прав доступа к `.env` файлу
4. Создать `.github/dependabot.yml`

### Фаза 2: Безопасность и надёжность (неделя 2)
1. Добавить graceful shutdown в `main.py`
2. Реализовать exponential backoff с jitter
3. Добавить health check endpoint
4. Создать Dockerfile и docker-compose.yml

### Фаза 3: CI/CD улучшение (неделя 3)
1. Добавить CodeQL scanning
2. Добавить линтинг в CI
3. Добавить матрицу Python версий
4. Настроить автоматический релиз

### Фаза 4: Observability (неделя 4)
1. Интегрировать Sentry для error tracking
2. Добавить Prometheus метрики
3. Настроить алерты
4. Добавить security hardening для systemd

<p align="center">
  <img src="assets/banner.png" alt="Геркулес Агент" width="100%">
</p>

# Геркулес Агент ☤

<p align="center">
  <a href="https://hermes-agent.nousresearch.com/docs/"><img src="https://img.shields.io/badge/Docs-hermes--agent.nousresearch.com-FFD700?style=for-the-badge" alt="Документация"></a>
  <a href="https://discord.gg/NousResearch"><img src="https://img.shields.io/badge/Discord-5865F2?style=for-the-badge&logo=discord&logoColor=white" alt="Discord"></a>
  <a href="https://github.com/NousResearch/hermes-agent/blob/main/LICENSE"><img src="https://img.shields.io/badge/License-MIT-green?style=for-the-badge" alt="License: MIT"></a>
  <a href="https://nousresearch.com"><img src="https://img.shields.io/badge/Built%20by-Nous%20Research-blueviolet?style=for-the-badge" alt="Built by Nous Research"></a>
  <a href="README.zh-CN.md"><img src="https://img.shields.io/badge/Lang-中文-red?style=for-the-badge" alt="中文"></a>
</p>

**Самосовершенствующийся ИИ-агент от [Nous Research](https://nousresearch.com).** Это единственный агент со встроенным циклом обучения — он создает навыки на основе опыта, улучшает их в процессе использования, подталкивает себя к сохранению знаний, ищет в своих прошлых беседах и строит углубленную модель того, кто вы есть в разных сессиях. Запустите его на VPS за $5, кластере GPU или бессерверной инфраструктуре, которая почти ничего не стоит в простое. Он не привязан к вашему ноутбуку — общайтесь с ним из Telegram, пока он работает на облачной VM.

Используйте любую модель, которую хотите — [Nous Portal](https://portal.nousresearch.com), [OpenRouter](https://openrouter.ai) (200+ моделей), [NovitaAI](https://novita.ai) (AI-native облако для Model API, Agent Sandbox и GPU Cloud), [NVIDIA NIM](https://build.nvidia.com) (Nemotron), [Xiaomi MiMo](https://platform.xiaomimimo.com), [z.ai/GLM](https://z.ai), [Kimi/Moonshot](https://platform.moonshot.ai), [MiniMax](https://www.minimax.io), [Hugging Face](https://huggingface.co), OpenAI, или ваш собственный endpoint. Переключайтесь с помощью `hermes model` — никаких изменений в коде, никакой привязки.

<table>
<tr><td><b>Настоящий терминальный интерфейс</b></td><td>Полный TUI с многострочным редактированием, автодополнением команд по слешу, историей разговоров, прерыванием и перенаправлением, а также потоковой выдачей результатов инструментов.</td></tr>
<tr><td><b>Работает там, где вы</b></td><td>Telegram, Discord, Slack, WhatsApp, Signal и CLI — все из единого процесса шлюза. Транскрипция голосовых сообщений, кроссплатформенная непрерывность разговоров.</td></tr>
<tr><td><b>Замкнутый цикл обучения</b></td><td>Память, курируемая агентом, с периодическими подталкиваниями. Автономное создание навыков после сложных задач. Навыки самосовершенствуются в процессе использования. Поиск по сессиям FTS5 с суммаризацией LLM для извлечения информации из прошлых сессий. Диалектическая модель пользователя в стиле [Honcho](https://github.com/plastic-labs/honcho). Совместимость с открытым стандартом [agentskills.io](https://agentskills.io).</td></tr>
<tr><td><b>Запланированные автоматизации</b></td><td>Встроенный планировщик cron с доставкой на любую платформу. Ежедневные отчеты, ночные резервные копии, еженедельные аудиты — все на естественном языке, работает без присмотра.</td></tr>
<tr><td><b>Делегирует и распараллеливает</b></td><td>Запускает изолированные субагенты для параллельных рабочих потоков. Пишите скрипты Python, которые вызывают инструменты через RPC, сводя многошаговые конвейеры к поворотам с нулевой стоимостью контекста.</td></tr>
<tr><td><b>Работает где угодно, не только на вашем ноутбуке</b></td><td>Семь бэкендов терминала — локальный, Docker, SSH, Singularity, Modal, Daytona и Vercel Sandbox. Daytona и Modal предлагают бессерверное сохранение — среда вашего агента гибернирует в простое и пробуждается по запросу, почти ничего не стоит между сессиями. Запустите его на VPS за $5 или кластере GPU.</td></tr>
<tr><td><b>Готов к исследованиям</b></td><td>Генерация траекторий пакетами, сжатие траекторий для обучения следующего поколения моделей, вызывающих инструменты.</td></tr>
</table>

---

## Архитектура Геркулеса

```text
Пользователь
  ↓
/start (start)
  ↓ Task(orchestrator)
Orchestrator
  ↓↓↓
Специалисты / субагенты
  ↓
Синтез → start → пользователь
```

**Архитектурные инварианты:**

1. **Цепочка:** `user → /start → Task(orchestrator) → Task(specialists)`
2. **Нет Task tool → `MULTI_AGENT_PIPELINE_BLOCKED`** (HARD FAIL, не silent fallback)
3. **L1 writer fan-out > 6** → реструктуризация через суб-оркестраторы
4. **Reader-ветки** без лимита, **writer-ветки:** 3+ → escalate

---

## Компоненты Геркулеса

| Директория | Назначение | Ключевые файлы |
|------------|------------|----------------|
| [`agents/`](agents/) | 33 определения агентов (4 координационных + 29 специалистов) | [`orchestrator.md`](agents/orchestrator.md), [`start.md`](agents/start.md), [`code.md`](agents/code.md) |
| [`rules/`](rules/) | 4 файла `.mdc`, применяемые всегда — глобальные ограничения | [`orchestrator.mdc`](rules/orchestrator.mdc), [`specialists.mdc`](rules/specialists.mdc) |
| [`skills/`](skills/) | 32 сценария рабочего процесса (`SKILL.md`) | [`orchestrator/SKILL.md`](skills/orchestrator/SKILL.md), [`start-workflow/SKILL.md`](skills/start-workflow/SKILL.md) |
| [`docs/`](docs/) | 37 markdown файлов документации | [`delegation-chain.md`](docs/delegation-chain.md), [`MAINTENANCE_RUNBOOK.md`](docs/MAINTENANCE_RUNBOOK.md) |
| [`scripts/`](scripts/) | 8 скриптов × 3 платформы (`.py`/`.sh`/`.ps1`) | [`run-full-repo-benchmark.py`](scripts/run-full-repo-benchmark.py), [`check-policy-encoding.py`](scripts/check-policy-encoding.py) |
| [`benchmarks/`](benchmarks/) | Контракты поведения + транскрипты-примеры (пройденные/не пройденные) | [`behavior-contracts.json`](benchmarks/behavior-contracts.json), [`transcript-cases.json`](benchmarks/transcript-cases.json) |
| [`profiles/`](profiles/) | Расширения, специфичные для проекта (изолированные от ядра) | [`msnmp/`](profiles/msnmp/) — конвейер пентеста |
| [`reports/`](reports/) | Отчеты аудита (архитектура, безопасность, документация, DevOps) | [`architecture-review-comprehensive.md`](reports/architecture-review-comprehensive.md) |
| [`.github/workflows/`](.github/workflows/) | CI валидация при push/PR | [`repo-validation.yml`](.github/workflows/repo-validation.yml) |

---

## Быстрая установка Геркулеса

### Linux, macOS, WSL2, Termux

```bash
curl -fsSL https://raw.githubusercontent.com/NousResearch/hermes-agent/main/scripts/install.sh | bash
```

### Windows (нативная, PowerShell) — Ранняя бета

> **Внимание:** Нативная поддержка Windows находится в **ранней бета-версии**. Она устанавливается и работает, но не была так широко протестирована, как наши пути для Linux/macOS/WSL2. Пожалуйста, [сообщайте об ошибках](https://github.com/NousResearch/hermes-agent/issues), когда столкнетесь с проблемами. Для наиболее проверенной настройки Windows сегодня запустите однострочник для Linux выше внутри **WSL2**.

Выполните это в PowerShell:

```powershell
iex (irm https://raw.githubusercontent.com/NousResearch/hermes-agent/main/scripts/install.ps1)
```

Установщик обрабатывает все: uv, Python 3.11, Node.js, ripgrep, ffmpeg, **и портативный Git Bash** (MinGit, распакованный в `%LOCALAPPDATA%\hermes\git` — не требует прав администратора, полностью изолирован от любой системной установки Git). Hermes использует этот встроенный Git Bash для выполнения команд оболочки.

Если у вас уже установлен Git, установщик обнаружит его и использует вместо этого. В противном случае загрузка MinGit размером ~45 МБ — это все, что вам нужно — он не будет касаться или мешать какому-либо системному Git.

> **Android / Termux:** Проверенный ручной путь документирован в [руководстве Termux](https://hermes-agent.nousresearch.com/docs/getting-started/termux). В Termux Hermes устанавливает кураторский экстра `.[termux]`, потому что полный экстра `.[all]` в настоящее время включает несовместимые с Android голосовые зависимости.
>
> **Windows:** Нативная поддержка Windows поддерживается как **ранняя бета** — однострочник PowerShell выше устанавливает все, но ожидайте шероховатостей и, пожалуйста, сообщайте об ошибках, когда столкнетесь с ними. Если вы предпочитаете использовать WSL2 (наш наиболее проверенный путь для Windows), команда для Linux также работает там. Нативная установка Windows находится в `%LOCALAPPDATA%\hermes`; установки WSL2 находятся в `~/.hermes`, как и в Linux. Единственная функция Hermes, которая в настоящее время требует именно WSL2, — это панель чата в браузере (она использует POSIX PTY — классический CLI и шлюз работают нативно).

После установки:

```bash
source ~/.bashrc    # перезагрузить оболочку (или: source ~/.zshrc)
hermes              # начать чат!
```

---

## Начало работы

```bash
hermes              # Интерактивный CLI — начать разговор
hermes model        # Выбрать ваш LLM-провайдер и модель
hermes tools        # Настроить, какие инструменты включены
hermes config set   # Установить отдельные значения конфигурации
hermes gateway      # Запустить шлюз обмена сообщениями (Telegram, Discord и т.д.)
hermes setup        # Запустить полный мастер настройки (конфигурирует все сразу)
hermes claw migrate # Мигрировать из OpenClaw (если вы переходите из OpenClaw)
hermes update       # Обновить до последней версии
hermes doctor       # Диагностировать любые проблемы
```

📖 **[Полная документация →](https://hermes-agent.nousresearch.com/docs/)**

## CLI vs Сообщения Краткое руководство

Hermes имеет две точки входа: запустите терминальный интерфейс с помощью `hermes`, или запустите шлюз и общайтесь с ним из Telegram, Discord, Slack, WhatsApp, Signal или Email. Как только вы окажетесь в разговоре, многие команды слеша будут общими для обоих интерфейсов.

| Действие | CLI | Платформы сообщений |
|---------|-----|---------------------|
| Начать чат | `hermes` | Запустите `hermes gateway setup` + `hermes gateway start`, затем отправьте боту сообщение |
| Начать новый разговор | `/new` или `/reset` | `/new` или `/reset` |
| Изменить модель | `/model [провайдер:модель]` | `/model [провайдер:модель]` |
| Установить личность | `/personality [имя]` | `/personality [имя]` |
| Повторить или отменить последний ход | `/retry`, `/undo` | `/retry`, `/undo` |
| Сжать контекст / проверить использование | `/compress`, `/usage`, `/insights [--дни N]` | `/compress`, `/usage`, `/insights [дни]` |
| Просмотреть навыки | `/skills` или `/<имя-навыка>` | `/<имя-навыка>` |
| Прервать текущую работу | `Ctrl+C` или отправить новое сообщение | `/stop` или отправить новое сообщение |
| Статус, специфичный для платформы | `/platforms` | `/status`, `/sethome` |

Полные списки команд см. в [руководстве CLI](https://hermes-agent.nousresearch.com/docs/user-guide/cli) и [руководстве шлюза сообщений](https://hermes-agent.nousresearch.com/docs/user-guide/messaging).

---

## Документация

Вся документация находится по адресу **[hermes-agent.nousresearch.com/docs](https://hermes-agent.nousresearch.com/docs/)**:

| Раздел | Что охватывается |
|---------|---------------|
| [Быстрый старт](https://hermes-agent.nousresearch.com/docs/getting-started/quickstart) | Установка → настройка → первый разговор за 2 минуты |
| [Использование CLI](https://hermes-agent.nousresearch.com/docs/user-guide/cli) | Команды, привязки клавиш, личности, сессии |
| [Конфигурация](https://hermes-agent.nousresearch.com/docs/user-guide/configuration) | Файл конфигурации, провайдеры, модели, все опции |
| [Шлюз сообщений](https://hermes-agent.nousresearch.com/docs/user-guide/messaging) | Telegram, Discord, Slack, WhatsApp, Signal, Home Assistant |
| [Безопасность](https://hermes-agent.nousresearch.com/docs/user-guide/security) | Одобрение команд, сопряжение DM, изоляция контейнеров |
| [Инструменты и наборы инструментов](https://hermes-agent.nousresearch.com/docs/user-guide/features/tools) | 40+ инструментов, система наборов инструментов, бэкенды терминалов |
| [Система навыков](https://hermes-agent.nousresearch.com/docs/user-guide/features/skills) | Процедурная память, Skills Hub, создание навыков |
| [Память](https://hermes-agent.nousresearch.com/docs/user-guide/features/memory) | Постоянная память, профили пользователей, лучшие практики |
| [Интеграция MCP](https://hermes-agent.nousresearch.com/docs/user-guide/features/mcp) | Подключение любого сервера MCP для расширенных возможностей |
| [Планирование Cron](https://hermes-agent.nousresearch.com/docs/user-guide/features/cron) | Запланированные задачи с доставкой на платформу |
| [Файлы контекста](https://hermes-agent.nousresearch.com/docs/user-guide/features/context-files) | Контекст проекта, который формирует каждый разговор |
| [Архитектура](https://hermes-agent.nousresearch.com/docs/developer-guide/architecture) | Структура проекта, цикл агента, ключевые классы |
| [Участие](https://hermes-agent.nousresearch.com/docs/developer-guide/contributing) | Настройка разработки, стиль кода, процесс PR |
| [Справочник CLI](https://hermes-agent.nousresearch.com/docs/reference/cli-commands) | Все команды и флаги |
| [Переменные окружения](https://hermes-agent.nousresearch.com/docs/reference/environment-variables) | Полный справочник переменных окружения |

---

## Миграция из OpenClaw

Если вы переходите из OpenClaw, Hermes может автоматически импортировать ваши настройки, память, навыки и ключи API.

**Во время первой настройки:** Мастер настройки (`hermes setup`) автоматически обнаруживает `~/.openclaw` и предлагает выполнить миграцию перед началом настройки.

**В любое время после установки:**

```bash
hermes claw migrate              # Интерактивная миграция (полный пресет)
hermes claw migrate --dry-run    # Предварительный просмотр того, что будет мигрировано
hermes claw migrate --preset user-data   # Миграция без секретов
hermes claw migrate --overwrite  # Перезапись существующих конфликтов
```

Что импортируется:
- **SOUL.md** — файл персоны
- **Память** — записи MEMORY.md и USER.md
- **Навыки** — пользовательские навыки → `~/.hermes/skills/openclaw-imports/`
- **Список разрешенных команд** — шаблоны одобрения
- **Настройки сообщений** — конфигурации платформ, разрешенные пользователи, рабочая директория
- **Ключи API** — разрешенные секреты (Telegram, OpenRouter, OpenAI, Anthropic, ElevenLabs)
- **TTS ресурсы** — рабочие файлы аудио
- **Инструкции для рабочей среды** — AGENTS.md (с `--workspace-target`)

См. `hermes claw migrate --help` для всех опций или используйте навык `openclaw-migration` для интерактивной миграции под руководством агента с предварительным просмотром.

---

## Участие

Мы приветствуем ваш вклад! См. [Руководство по участию](https://hermes-agent.nousresearch.com/docs/developer-guide/contributing) для настройки разработки, стиля кода и процесса PR.

Краткое руководство для участников — клонируйте и запускайте с помощью `setup-hermes.sh`:

```bash
git clone https://github.com/NousResearch/hermes-agent.git
cd hermes-agent
./setup-hermes.sh     # устанавливает uv, создает venv, устанавливает .[all], создает символическую ссылку ~/.local/bin/hermes
./hermes              # автоматически определяет venv, не нужно `source` заранее
```

Ручной путь (эквивалент вышеизложенного):

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
uv venv .venv --python 3.11
source .venv/bin/activate
uv pip install -e ".[all,dev]"
scripts/run_tests.sh
```

---

## Сообщество

- 💬 [Discord](https://discord.gg/NousResearch)
- 📚 [Skills Hub](https://agentskills.io)
- 🐛 [Issues](https://github.com/NousResearch/hermes-agent/issues)
- 🔌 [computer-use-linux](https://github.com/avifenesh/computer-use-linux) — MCP сервер управления рабочим столом Linux для Hermes и других хостов MCP, с деревьями доступности AT-SPI, вводом Wayland/X11, скриншотами и таргетингом окон композитора.
- 🔌 [HermesClaw](https://github.com/AaronWong1999/hermesclaw) — Мост WeChat от сообщества: Запустите Hermes Agent и OpenClaw на одном аккаунте WeChat.

---

## Лицензия

MIT — см. [LICENSE](LICENSE).

Разработано [Nous Research](https://nousresearch.com).

---

## Архитектура Геркулеса

```text
Пользователь
  ↓
/start (start)
  ↓ Task(orchestrator)
Orchestrator
  ↓↓↓
Специалисты / субагенты
  ↓
Синтез → start → пользователь
```

**Архитектурные инварианты:**

1. **Цепочка:** `user → /start → Task(orchestrator) → Task(specialists)`
2. **Нет Task tool → `MULTI_AGENT_PIPELINE_BLOCKED`** (HARD FAIL, не silent fallback)
3. **L1 writer fan-out > 6** → реструктуризация через суб-оркестраторы
4. **Reader-ветки** без лимита, **writer-ветки:** 3+ → escalate

---

## Компоненты Геркулеса

| Директория | Назначение | Ключевые файлы |
|------------|------------|----------------|
| [`agents/`](agents/) | 33 определения агентов (4 координационных + 29 специалистов) | [`orchestrator.md`](agents/orchestrator.md), [`start.md`](agents/start.md), [`code.md`](agents/code.md) |
| [`rules/`](rules/) | 4 файла `.mdc`, применяемые всегда — глобальные ограничения | [`orchestrator.mdc`](rules/orchestrator.mdc), [`specialists.mdc`](rules/specialists.mdc) |
| [`skills/`](skills/) | 32 сценария рабочего процесса (`SKILL.md`) | [`orchestrator/SKILL.md`](skills/orchestrator/SKILL.md), [`start-workflow/SKILL.md`](skills/start-workflow/SKILL.md) |
| [`docs/`](docs/) | 37 markdown файлов документации | [`delegation-chain.md`](docs/delegation-chain.md), [`MAINTENANCE_RUNBOOK.md`](docs/MAINTENANCE_RUNBOOK.md) |
| [`scripts/`](scripts/) | 8 скриптов × 3 платформы (`.py`/`.sh`/`.ps1`) | [`run-full-repo-benchmark.py`](scripts/run-full-repo-benchmark.py), [`check-policy-encoding.py`](scripts/check-policy-encoding.py) |
| [`benchmarks/`](benchmarks/) | Контракты поведения + транскрипты-примеры (пройденные/не пройденные) | [`behavior-contracts.json`](benchmarks/behavior-contracts.json), [`transcript-cases.json`](benchmarks/transcript-cases.json) |
| [`profiles/`](profiles/) | Расширения, специфичные для проекта (изолированные от ядра) | [`msnmp/`](profiles/msnmp/) — конвейер пентеста |
| [`reports/`](reports/) | Отчеты аудита (архитектура, безопасность, документация, DevOps) | [`architecture-review-comprehensive.md`](reports/architecture-review-comprehensive.md) |
| [`.github/workflows/`](.github/workflows/) | CI валидация при push/PR | [`repo-validation.yml`](.github/workflows/repo-validation.yml) |

---

## Быстрая установка Геркулеса

### Linux, macOS, WSL2, Termux

```bash
curl -fsSL https://raw.githubusercontent.com/NousResearch/hermes-agent/main/scripts/install.sh | bash
```

### Windows (нативная, PowerShell) — Ранняя бета

> **Внимание:** Нативная поддержка Windows находится в **ранней бета-версии**. Она устанавливается и работает, но не была так широко протестирована, как наши пути для Linux/macOS/WSL2. Пожалуйста, [сообщайте об ошибках](https://github.com/NousResearch/hermes-agent/issues), когда столкнетесь с проблемами. Для наиболее проверенной настройки Windows сегодня запустите однострочник для Linux выше внутри **WSL2**.

Выполните это в PowerShell:

```powershell
iex (irm https://raw.githubusercontent.com/NousResearch/hermes-agent/main/scripts/install.ps1)
```

Установщик обрабатывает все: uv, Python 3.11, Node.js, ripgrep, ffmpeg, **и портативный Git Bash** (MinGit, распакованный в `%LOCALAPPDATA%\hermes\git` — не требует прав администратора, полностью изолирован от любой системной установки Git). Hermes использует этот встроенный Git Bash для выполнения команд оболочки.

Если у вас уже установлен Git, установщик обнаружит его и использует вместо этого. В противном случае загрузка MinGit размером ~45 МБ — это все, что вам нужно — он не будет касаться или мешать какому-либо системному Git.

> **Android / Termux:** Проверенный ручной путь документирован в [руководстве Termux](https://hermes-agent.nousresearch.com/docs/getting-started/termux). В Termux Hermes устанавливает кураторский экстра `.[termux]`, потому что полный экстра `.[all]` в настоящее время включает несовместимые с Android голосовые зависимости.
>
> **Windows:** Нативная поддержка Windows поддерживается как **ранняя бета** — однострочник PowerShell выше устанавливает все, но ожидайте шероховатостей и, пожалуйста, сообщайте об ошибках, когда столкнетесь с ними. Если вы предпочитаете использовать WSL2 (наш наиболее проверенный путь для Windows), команда для Linux также работает там. Нативная установка Windows находится в `%LOCALAPPDATA%\hermes`; установки WSL2 находятся в `~/.hermes`, как и в Linux. Единственная функция Hermes, которая в настоящее время требует именно WSL2, — это панель чата в браузере (она использует POSIX PTY — классический CLI и шлюз работают нативно).

После установки:

```bash
source ~/.bashrc    # перезагрузить оболочку (или: source ~/.zshrc)
hermes              # начать чат!
```

---

## Начало работы

```bash
hermes              # Интерактивный CLI — начать разговор
hermes model        # Выбрать ваш LLM-провайдер и модель
hermes tools        # Настроить, какие инструменты включены
hermes config set   # Установить отдельные значения конфигурации
hermes gateway      # Запустить шлюз обмена сообщениями (Telegram, Discord и т.д.)
hermes setup        # Запустить полный мастер настройки (конфигурирует все сразу)
hermes claw migrate # Мигрировать из OpenClaw (если вы переходите из OpenClaw)
hermes update       # Обновить до последней версии
hermes doctor       # Диагностировать любые проблемы
```

📖 **[Полная документация →](https://hermes-agent.nousresearch.com/docs/)**

## CLI vs Сообщения Краткое руководство

Hermes имеет две точки входа: запустите терминальный интерфейс с помощью `hermes`, или запустите шлюз и общайтесь с ним из Telegram, Discord, Slack, WhatsApp, Signal или Email. Как только вы окажетесь в разговоре, многие команды слеша будут общими для обоих интерфейсов.

| Действие | CLI | Платформы сообщений |
|---------|-----|---------------------|
| Начать чат | `hermes` | Запустите `hermes gateway setup` + `hermes gateway start`, затем отправьте боту сообщение |
| Начать новый разговор | `/new` или `/reset` | `/new` или `/reset` |
| Изменить модель | `/model [провайдер:модель]` | `/model [провайдер:модель]` |
| Установить личность | `/personality [имя]` | `/personality [имя]` |
| Повторить или отменить последний ход | `/retry`, `/undo` | `/retry`, `/undo` |
| Сжать контекст / проверить использование | `/compress`, `/usage`, `/insights [--дни N]` | `/compress`, `/usage`, `/insights [дни]` |
| Просмотреть навыки | `/skills` или `/<имя-навыка>` | `/<имя-навыка>` |
| Прервать текущую работу | `Ctrl+C` или отправить новое сообщение | `/stop` или отправить новое сообщение |
| Статус, специфичный для платформы | `/platforms` | `/status`, `/sethome` |

Полные списки команд см. в [руководстве CLI](https://hermes-agent.nousresearch.com/docs/user-guide/cli) и [руководстве шлюза сообщений](https://hermes-agent.nousresearch.com/docs/user-guide/messaging).

---

## Документация

Вся документация находится по адресу **[hermes-agent.nousresearch.com/docs](https://hermes-agent.nousresearch.com/docs/)**:

| Раздел | Что охватывается |
|---------|---------------|
| [Быстрый старт](https://hermes-agent.nousresearch.com/docs/getting-started/quickstart) | Установка → настройка → первый разговор за 2 минуты |
| [Использование CLI](https://hermes-agent.nousresearch.com/docs/user-guide/cli) | Команды, привязки клавиш, личности, сессии |
| [Конфигурация](https://hermes-agent.nousresearch.com/docs/user-guide/configuration) | Файл конфигурации, провайдеры, модели, все опции |
| [Шлюз сообщений](https://hermes-agent.nousresearch.com/docs/user-guide/messaging) | Telegram, Discord, Slack, WhatsApp, Signal, Home Assistant |
| [Безопасность](https://hermes-agent.nousresearch.com/docs/user-guide/security) | Одобрение команд, сопряжение DM, изоляция контейнеров |
| [Инструменты и наборы инструментов](https://hermes-agent.nousresearch.com/docs/user-guide/features/tools) | 40+ инструментов, система наборов инструментов, бэкенды терминалов |
| [Система навыков](https://hermes-agent.nousresearch.com/docs/user-guide/features/skills) | Процедурная память, Skills Hub, создание навыков |
| [Память](https://hermes-agent.nousresearch.com/docs/user-guide/features/memory) | Постоянная память, профили пользователей, лучшие практики |
| [Интеграция MCP](https://hermes-agent.nousresearch.com/docs/user-guide/features/mcp) | Подключение любого сервера MCP для расширенных возможностей |
| [Планирование Cron](https://hermes-agent.nousresearch.com/docs/user-guide/features/cron) | Запланированные задачи с доставкой на платформу |
| [Файлы контекста](https://hermes-agent.nousresearch.com/docs/user-guide/features/context-files) | Контекст проекта, который формирует каждый разговор |
| [Архитектура](https://hermes-agent.nousresearch.com/docs/developer-guide/architecture) | Структура проекта, цикл агента, ключевые классы |
| [Участие](https://hermes-agent.nousresearch.com/docs/developer-guide/contributing) | Настройка разработки, стиль кода, процесс PR |
| [Справочник CLI](https://hermes-agent.nousresearch.com/docs/reference/cli-commands) | Все команды и флаги |
| [Переменные окружения](https://hermes-agent.nousresearch.com/docs/reference/environment-variables) | Полный справочник переменных окружения |

---

## Миграция из OpenClaw

Если вы переходите из OpenClaw, Hermes может автоматически импортировать ваши настройки, память, навыки и ключи API.

**Во время первой настройки:** Мастер настройки (`hermes setup`) автоматически обнаруживает `~/.openclaw` и предлагает выполнить миграцию перед началом настройки.

**В любое время после установки:**

```bash
hermes claw migrate              # Интерактивная миграция (полный пресет)
hermes claw migrate --dry-run    # Предварительный просмотр того, что будет мигрировано
hermes claw migrate --preset user-data   # Миграция без секретов
hermes claw migrate --overwrite  # Перезапись существующих конфликтов
```

Что импортируется:
- **SOUL.md** — файл персоны
- **Память** — записи MEMORY.md и USER.md
- **Навыки** — пользовательские навыки → `~/.hermes/skills/openclaw-imports/`
- **Список разрешенных команд** — шаблоны одобрения
- **Настройки сообщений** — конфигурации платформ, разрешенные пользователи, рабочая директория
- **Ключи API** — разрешенные секреты (Telegram, OpenRouter, OpenAI, Anthropic, ElevenLabs)
- **TTS ресурсы** — рабочие файлы аудио
- **Инструкции для рабочей среды** — AGENTS.md (с `--workspace-target`)

См. `hermes claw migrate --help` для всех опций или используйте навык `openclaw-migration` для интерактивной миграции под руководством агента с предварительным просмотром.

---

## Участие

Мы приветствуем ваш вклад! См. [Руководство по участию](https://hermes-agent.nousresearch.com/docs/developer-guide/contributing) для настройки разработки, стиля кода и процесса PR.

Краткое руководство для участников — клонируйте и запускайте с помощью `setup-hermes.sh`:

```bash
git clone https://github.com/NousResearch/hermes-agent.git
cd hermes-agent
./setup-hermes.sh     # устанавливает uv, создает venv, устанавливает .[all], создает символическую ссылку ~/.local/bin/hermes
./hermes              # автоматически определяет venv, не нужно `source` заранее
```

Ручной путь (эквивалент вышеизложенного):

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
uv venv .venv --python 3.11
source .venv/bin/activate
uv pip install -e ".[all,dev]"
scripts/run_tests.sh
```

---

## Сообщество

- 💬 [Discord](https://discord.gg/NousResearch)
- 📚 [Skills Hub](https://agentskills.io)
- 🐛 [Issues](https://github.com/NousResearch/hermes-agent/issues)
- 🔌 [computer-use-linux](https://github.com/avifenesh/computer-use-linux) — MCP сервер управления рабочим столом Linux для Hermes и других хостов MCP, с деревьями доступности AT-SPI, вводом Wayland/X11, скриншотами и таргетингом окон композитора.
- 🔌 [HermesClaw](https://github.com/AaronWong1999/hermesclaw) — Мост WeChat от сообщества: Запустите Hermes Agent и OpenClaw на одном аккаунте WeChat.

---

## Лицензия

MIT — см. [LICENSE](LICENSE).

Разработано [Nous Research](https://nousresearch.com).

---

## Архитектура Геркулеса

```text
Пользователь
  ↓
/start (start)
  ↓ Task(orchestrator)
Orchestrator
  ↓↓↓
Специалисты / субагенты
  ↓
Синтез → start → пользователь
```

**Архитектурные инварианты:**

1. **Цепочка:** `user → /start → Task(orchestrator) → Task(specialists)`
2. **Нет Task tool → `MULTI_AGENT_PIPELINE_BLOCKED`** (HARD FAIL, не silent fallback)
3. **L1 writer fan-out > 6** → реструктуризация через суб-оркестраторы
4. **Reader-ветки** без лимита, **writer-ветки:** 3+ → escalate

---

## Компоненты Геркулеса

| Директория | Назначение | Ключевые файлы |
|------------|------------|----------------|
| [`agents/`](agents/) | 33 определения агентов (4 координационных + 29 специалистов) | [`orchestrator.md`](agents/orchestrator.md), [`start.md`](agents/start.md), [`code.md`](agents/code.md) |
| [`rules/`](rules/) | 4 файла `.mdc`, применяемые всегда — глобальные ограничения | [`orchestrator.mdc`](rules/orchestrator.mdc), [`specialists.mdc`](rules/specialists.mdc) |
| [`skills/`](skills/) | 32 сценария рабочего процесса (`SKILL.md`) | [`orchestrator/SKILL.md`](skills/orchestrator/SKILL.md), [`start-workflow/SKILL.md`](skills/start-workflow/SKILL.md) |
| [`docs/`](docs/) | 37 markdown файлов документации | [`delegation-chain.md`](docs/delegation-chain.md), [`MAINTENANCE_RUNBOOK.md`](docs/MAINTENANCE_RUNBOOK.md) |
| [`scripts/`](scripts/) | 8 скриптов × 3 платформы (`.py`/`.sh`/`.ps1`) | [`run-full-repo-benchmark.py`](scripts/run-full-repo-benchmark.py), [`check-policy-encoding.py`](scripts/check-policy-encoding.py) |
| [`benchmarks/`](benchmarks/) | Контракты поведения + транскрипты-примеры (пройденные/не пройденные) | [`behavior-contracts.json`](benchmarks/behavior-contracts.json), [`transcript-cases.json`](benchmarks/transcript-cases.json) |
| [`profiles/`](profiles/) | Расширения, специфичные для проекта (изолированные от ядра) | [`msnmp/`](profiles/msnmp/) — конвейер пентеста |
| [`reports/`](reports/) | Отчеты аудита (архитектура, безопасность, документация, DevOps) | [`architecture-review-comprehensive.md`](reports/architecture-review-comprehensive.md) |
| [`.github/workflows/`](.github/workflows/) | CI валидация при push/PR | [`repo-validation.yml`](.github/workflows/repo-validation.yml) |

---

## Быстрая установка Геркулеса

### Linux, macOS, WSL2, Termux

```bash
curl -fsSL https://raw.githubusercontent.com/NousResearch/hermes-agent/main/scripts/install.sh | bash
```

### Windows (нативная, PowerShell) — Ранняя бета

> **Внимание:** Нативная поддержка Windows находится в **ранней бета-версии**. Она устанавливается и работает, но не была так широко протестирована, как наши пути для Linux/macOS/WSL2. Пожалуйста, [сообщайте об ошибках](https://github.com/NousResearch/hermes-agent/issues), когда столкнетесь с проблемами. Для наиболее проверенной настройки Windows сегодня запустите однострочник для Linux выше внутри **WSL2**.

Выполните это в PowerShell:

```powershell
iex (irm https://raw.githubusercontent.com/NousResearch/hermes-agent/main/scripts/install.ps1)
```

Установщик обрабатывает все: uv, Python 3.11, Node.js, ripgrep, ffmpeg, **и портативный Git Bash** (MinGit, распакованный в `%LOCALAPPDATA%\hermes\git` — не требует прав администратора, полностью изолирован от любой системной установки Git). Hermes использует этот встроенный Git Bash для выполнения команд оболочки.

Если у вас уже установлен Git, установщик обнаружит его и использует вместо этого. В противном случае загрузка MinGit размером ~45 МБ — это все, что вам нужно — он не будет касаться или мешать какому-либо системному Git.

> **Android / Termux:** Проверенный ручной путь документирован в [руководстве Termux](https://hermes-agent.nousresearch.com/docs/getting-started/termux). В Termux Hermes устанавливает кураторский экстра `.[termux]`, потому что полный экстра `.[all]` в настоящее время включает несовместимые с Android голосовые зависимости.
>
> **Windows:** Нативная поддержка Windows поддерживается как **ранняя бета** — однострочник PowerShell выше устанавливает все, но ожидайте шероховатостей и, пожалуйста, сообщайте об ошибках, когда столкнетесь с ними. Если вы предпочитаете использовать WSL2 (наш наиболее проверенный путь для Windows), команда для Linux также работает там. Нативная установка Windows находится в `%LOCALAPPDATA%\hermes`; установки WSL2 находятся в `~/.hermes`, как и в Linux. Единственная функция Hermes, которая в настоящее время требует именно WSL2, — это панель чата в браузере (она использует POSIX PTY — классический CLI и шлюз работают нативно).

После установки:

```bash
source ~/.bashrc    # перезагрузить оболочку (или: source ~/.zshrc)
hermes              # начать чат!
```

---

## Начало работы

```bash
hermes              # Интерактивный CLI — начать разговор
hermes model        # Выбрать ваш LLM-провайдер и модель
hermes tools        # Настроить, какие инструменты включены
hermes config set   # Установить отдельные значения конфигурации
hermes gateway      # Запустить шлюз обмена сообщениями (Telegram, Discord и т.д.)
hermes setup        # Запустить полный мастер настройки (конфигурирует все сразу)
hermes claw migrate # Мигрировать из OpenClaw (если вы переходите из OpenClaw)
hermes update       # Обновить до последней версии
hermes doctor       # Диагностировать любые проблемы
```

📖 **[Полная документация →](https://hermes-agent.nousresearch.com/docs/)**

## CLI vs Сообщения Краткое руководство

Hermes имеет две точки входа: запустите терминальный интерфейс с помощью `hermes`, или запустите шлюз и общайтесь с ним из Telegram, Discord, Slack, WhatsApp, Signal или Email. Как только вы окажетесь в разговоре, многие команды слеша будут общими для обоих интерфейсов.

| Действие | CLI | Платформы сообщений |
|---------|-----|---------------------|
| Начать чат | `hermes` | Запустите `hermes gateway setup` + `hermes gateway start`, затем отправьте боту сообщение |
| Начать новый разговор | `/new` или `/reset` | `/new` или `/reset` |
| Изменить модель | `/model [провайдер:модель]` | `/model [провайдер:модель]` |
| Установить личность | `/personality [имя]` | `/personality [имя]` |
| Повторить или отменить последний ход | `/retry`, `/undo` | `/retry`, `/undo` |
| Сжать контекст / проверить использование | `/compress`, `/usage`, `/insights [--дни N]` | `/compress`, `/usage`, `/insights [дни]` |
| Просмотреть навыки | `/skills` или `/<имя-навыка>` | `/<имя-навыка>` |
| Прервать текущую работу | `Ctrl+C` или отправить новое сообщение | `/stop` или отправить новое сообщение |
| Статус, специфичный для платформы | `/platforms` | `/status`, `/sethome` |

Полные списки команд см. в [руководстве CLI](https://hermes-agent.nousresearch.com/docs/user-guide/cli) и [руководстве шлюза сообщений](https://hermes-agent.nousresearch.com/docs/user-guide/messaging).

---

## Документация

Вся документация находится по адресу **[hermes-agent.nousresearch.com/docs](https://hermes-agent.nousresearch.com/docs/)**:

| Раздел | Что охватывается |
|---------|---------------|
| [Быстрый старт](https://hermes-agent.nousresearch.com/docs/getting-started/quickstart) | Установка → настройка → первый разговор за 2 минуты |
| [Использование CLI](https://hermes-agent.nousresearch.com/docs/user-guide/cli) | Команды, привязки клавиш, личности, сессии |
| [Конфигурация](https://hermes-agent.nousresearch.com/docs/user-guide/configuration) | Файл конфигурации, провайдеры, модели, все опции |
| [Шлюз сообщений](https://hermes-agent.nousresearch.com/docs/user-guide/messaging) | Telegram, Discord, Slack, WhatsApp, Signal, Home Assistant |
| [Безопасность](https://hermes-agent.nousresearch.com/docs/user-guide/security) | Одобрение команд, сопряжение DM, изоляция контейнеров |
| [Инструменты и наборы инструментов](https://hermes-agent.nousresearch.com/docs/user-guide/features/tools) | 40+ инструментов, система наборов инструментов, бэкенды терминалов |
| [Система навыков](https://hermes-agent.nousresearch.com/docs/user-guide/features/skills) | Процедурная память, Skills Hub, создание навыков |
| [Память](https://hermes-agent.nousresearch.com/docs/user-guide/features/memory) | Постоянная память, профили пользователей, лучшие практики |
| [Интеграция MCP](https://hermes-agent.nousresearch.com/docs/user-guide/features/mcp) | Подключение любого сервера MCP для расширенных возможностей |
| [Планирование Cron](https://hermes-agent.nousresearch.com/docs/user-guide/features/cron) | Запланированные задачи с доставкой на платформу |
| [Файлы контекста](https://hermes-agent.nousresearch.com/docs/user-guide/features/context-files) | Контекст проекта, который формирует каждый разговор |
| [Архитектура](https://hermes-agent.nousresearch.com/docs/developer-guide/architecture) | Структура проекта, цикл агента, ключевые классы |
| [Участие](https://hermes-agent.nousresearch.com/docs/developer-guide/contributing) | Настройка разработки, стиль кода, процесс PR |
| [Справочник CLI](https://hermes-agent.nousresearch.com/docs/reference/cli-commands) | Все команды и флаги |
| [Переменные окружения](https://hermes-agent.nousresearch.com/docs/reference/environment-variables) | Полный справочник переменных окружения |

---

## Миграция из OpenClaw

Если вы переходите из OpenClaw, Hermes может автоматически импортировать ваши настройки, память, навыки и ключи API.

**Во время первой настройки:** Мастер настройки (`hermes setup`) автоматически обнаруживает `~/.openclaw` и предлагает выполнить миграцию перед началом настройки.

**В любое время после установки:**

```bash
hermes claw migrate              # Интерактивная миграция (полный пресет)
hermes claw migrate --dry-run    # Предварительный просмотр того, что будет мигрировано
hermes claw migrate --preset user-data   # Миграция без секретов
hermes claw migrate --overwrite  # Перезапись существующих конфликтов
```

Что импортируется:
- **SOUL.md** — файл персоны
- **Память** — записи MEMORY.md и USER.md
- **Навыки** — пользовательские навыки → `~/.hermes/skills/openclaw-imports/`
- **Список разрешенных команд** — шаблоны одобрения
- **Настройки сообщений** — конфигурации платформ, разрешенные пользователи, рабочая директория
- **Ключи API** — разрешенные секреты (Telegram, OpenRouter, OpenAI, Anthropic, ElevenLabs)
- **TTS ресурсы** — рабочие файлы аудио
- **Инструкции для рабочей среды** — AGENTS.md (с `--workspace-target`)

См. `hermes claw migrate --help` для всех опций или используйте навык `openclaw-migration` для интерактивной миграции под руководством агента с предварительным просмотром.

---

## Участие

Мы приветствуем ваш вклад! См. [Руководство по участию](https://hermes-agent.nousresearch.com/docs/developer-guide/contributing) для настройки разработки, стиля кода и процесса PR.

Краткое руководство для участников — клонируйте и запускайте с помощью `setup-hermes.sh`:

```bash
git clone https://github.com/NousResearch/hermes-agent.git
cd hermes-agent
./setup-hermes.sh     # устанавливает uv, создает venv, устанавливает .[all], создает символическую ссылку ~/.local/bin/hermes
./hermes              # автоматически определяет venv, не нужно `source` заранее
```

Ручной путь (эквивалент вышеизложенного):

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
uv venv .venv --python 3.11
source .venv/bin/activate
uv pip install -e ".[all,dev]"
scripts/run_tests.sh
```

---

## Сообщество

- 💬 [Discord](https://discord.gg/NousResearch)
- 📚 [Skills Hub](https://agentskills.io)
- 🐛 [Issues](https://github.com/NousResearch/hermes-agent/issues)
- 🔌 [computer-use-linux](https://github.com/avifenesh/computer-use-linux) — MCP сервер управления рабочим столом Linux для Hermes и других хостов MCP, с деревьями доступности AT-SPI, вводом Wayland/X11, скриншотами и таргетингом окон композитора.
- 🔌 [HermesClaw](https://github.com/AaronWong1999/hermesclaw) — Мост WeChat от сообщества: Запустите Hermes Agent и OpenClaw на одном аккаунте WeChat.

---

## Лицензия

MIT — см. [LICENSE](LICENSE).

Разработано [Nous Research](https://nousresearch.com).

---

## Архитектура Геркулеса

```text
Пользователь
  ↓
/start (start)
  ↓ Task(orchestrator)
Orchestrator
  ↓↓↓
Специалисты / субагенты
  ↓
Синтез → start → пользователь
```

**Архитектурные инварианты:**

1. **Цепочка:** `user → /start → Task(orchestrator) → Task(specialists)`
2. **Нет Task tool → `MULTI_AGENT_PIPELINE_BLOCKED`** (HARD FAIL, не silent fallback)
3. **L1 writer fan-out > 6** → реструктуризация через суб-оркестраторы
4. **Reader-ветки** без лимита, **writer-ветки:** 3+ → escalate

---

## Компоненты Геркулеса

| Директория | Назначение | Ключевые файлы |
|------------|------------|----------------|
| [`agents/`](agents/) | 33 определения агентов (4 координационных + 29 специалистов) | [`orchestrator.md`](agents/orchestrator.md), [`start.md`](agents/start.md), [`code.md`](agents/code.md) |
| [`rules/`](rules/) | 4 файла `.mdc`, применяемые всегда — глобальные ограничения | [`orchestrator.mdc`](rules/orchestrator.mdc), [`specialists.mdc`](rules/specialists.mdc) |
| [`skills/`](skills/) | 32 сценария рабочего процесса (`SKILL.md`) | [`orchestrator/SKILL.md`](skills/orchestrator/SKILL.md), [`start-workflow/SKILL.md`](skills/start-workflow/SKILL.md) |
| [`docs/`](docs/) | 37 markdown файлов документации | [`delegation-chain.md`](docs/delegation-chain.md), [`MAINTENANCE_RUNBOOK.md`](docs/MAINTENANCE_RUNBOOK.md) |
| [`scripts/`](scripts/) | 8 скриптов × 3 платформы (`.py`/`.sh`/`.ps1`) | [`run-full-repo-benchmark.py`](scripts/run-full-repo-benchmark.py), [`check-policy-encoding.py`](scripts/check-policy-encoding.py) |
| [`benchmarks/`](benchmarks/) | Контракты поведения + транскрипты-примеры (пройденные/не пройденные) | [`behavior-contracts.json`](benchmarks/behavior-contracts.json), [`transcript-cases.json`](benchmarks/transcript-cases.json) |
| [`profiles/`](profiles/) | Расширения, специфичные для проекта (изолированные от ядра) | [`msnmp/`](profiles/msnmp/) — конвейер пентеста |
| [`reports/`](reports/) | Отчеты аудита (архитектура, безопасность, документация, DevOps) | [`architecture-review-comprehensive.md`](reports/architecture-review-comprehensive.md) |
| [`.github/workflows/`](.github/workflows/) | CI валидация при push/PR | [`repo-validation.yml`](.github/workflows/repo-validation.yml) |

---

## Быстрая установка Геркулеса

### Linux, macOS, WSL2, Termux

```bash
curl -fsSL https://raw.githubusercontent.com/NousResearch/hermes-agent/main/scripts/install.sh | bash
```

### Windows (нативная, PowerShell) — Ранняя бета

> **Внимание:** Нативная поддержка Windows находится в **ранней бета-версии**. Она устанавливается и работает, но не была так широко протестирована, как наши пути для Linux/macOS/WSL2. Пожалуйста, [сообщайте об ошибках](https://github.com/NousResearch/hermes-agent/issues), когда столкнетесь с проблемами. Для наиболее проверенной настройки Windows сегодня запустите однострочник для Linux выше внутри **WSL2**.

Выполните это в PowerShell:

```powershell
iex (irm https://raw.githubusercontent.com/NousResearch/hermes-agent/main/scripts/install.ps1)
```

Установщик обрабатывает все: uv, Python 3.11, Node.js, ripgrep, ffmpeg, **и портативный Git Bash** (MinGit, распакованный в `%LOCALAPPDATA%\hermes\git` — не требует прав администратора, полностью изолирован от любой системной установки Git). Hermes использует этот встроенный Git Bash для выполнения команд оболочки.

Если у вас уже установлен Git, установщик обнаружит его и использует вместо этого. В противном случае загрузка MinGit размером ~45 МБ — это все, что вам нужно — он не будет касаться или мешать какому-либо системному Git.

> **Android / Termux:** Проверенный ручной путь документирован в [руководстве Termux](https://hermes-agent.nousresearch.com/docs/getting-started/termux). В Termux Hermes устанавливает кураторский экстра `.[termux]`, потому что полный экстра `.[all]` в настоящее время включает несовместимые с Android голосовые зависимости.
>
> **Windows:** Нативная поддержка Windows поддерживается как **ранняя бета** — однострочник PowerShell выше устанавливает все, но ожидайте шероховатостей и, пожалуйста, сообщайте об ошибках, когда столкнетесь с ними. Если вы предпочитаете использовать WSL2 (наш наиболее проверенный путь для Windows), команда для Linux также работает там. Нативная установка Windows находится в `%LOCALAPPDATA%\hermes`; установки WSL2 находятся в `~/.hermes`, как и в Linux. Единственная функция Hermes, которая в настоящее время требует именно WSL2, — это панель чата в браузере (она использует POSIX PTY — классический CLI и шлюз работают нативно).

После установки:

```bash
source ~/.bashrc    # перезагрузить оболочку (или: source ~/.zshrc)
hermes              # начать чат!
```

---

## Начало работы

```bash
hermes              # Интерактивный CLI — начать разговор
hermes model        # Выбрать ваш LLM-провайдер и модель
hermes tools        # Настроить, какие инструменты включены
hermes config set   # Установить отдельные значения конфигурации
hermes gateway      # Запустить шлюз обмена сообщениями (Telegram, Discord и т.д.)
hermes setup        # Запустить полный мастер настройки (конфигурирует все сразу)
hermes claw migrate # Мигрировать из OpenClaw (если вы переходите из OpenClaw)
hermes update       # Обновить до последней версии
hermes doctor       # Диагностировать любые проблемы
```

📖 **[Полная документация →](https://hermes-agent.nousresearch.com/docs/)**

## CLI vs Сообщения Краткое руководство

Hermes имеет две точки входа: запустите терминальный интерфейс с помощью `hermes`, или запустите шлюз и общайтесь с ним из Telegram, Discord, Slack, WhatsApp, Signal или Email. Как только вы окажетесь в разговоре, многие команды слеша будут общими для обоих интерфейсов.

| Действие | CLI | Платформы сообщений |
|---------|-----|---------------------|
| Начать чат | `hermes` | Запустите `hermes gateway setup` + `hermes gateway start`, затем отправьте боту сообщение |
| Начать новый разговор | `/new` или `/reset` | `/new` или `/reset` |
| Изменить модель | `/model [провайдер:модель]` | `/model [провайдер:модель]` |
| Установить личность | `/personality [имя]` | `/personality [имя]` |
| Повторить или отменить последний ход | `/retry`, `/undo` | `/retry`, `/undo` |
| Сжать контекст / проверить использование | `/compress`, `/usage`, `/insights [--дни N]` | `/compress`, `/usage`, `/insights [дни]` |
| Просмотреть навыки | `/skills` или `/<имя-навыка>` | `/<имя-навыка>` |
| Прервать текущую работу | `Ctrl+C` или отправить новое сообщение | `/stop` или отправить новое сообщение |
| Статус, специфичный для платформы | `/platforms` | `/status`, `/sethome` |

Полные списки команд см. в [руководстве CLI](https://hermes-agent.nousresearch.com/docs/user-guide/cli) и [руководстве шлюза сообщений](https://hermes-agent.nousresearch.com/docs/user-guide/messaging).

---

## Документация

Вся документация находится по адресу **[hermes-agent.nousresearch.com/docs](https://hermes-agent.nousresearch.com/docs/)**:

| Раздел | Что охватывается |
|---------|---------------|
| [Быстрый старт](https://hermes-agent.nousresearch.com/docs/getting-started/quickstart) | Установка → настройка → первый разговор за 2 минуты |
| [Использование CLI](https://hermes-agent.nousresearch.com/docs/user-guide/cli) | Команды, привязки клавиш, личности, сессии |
| [Конфигурация](https://hermes-agent.nousresearch.com/docs/user-guide/configuration) | Файл конфигурации, провайдеры, модели, все опции |
| [Шлюз сообщений](https://hermes-agent.nousresearch.com/docs/user-guide/messaging) | Telegram, Discord, Slack, WhatsApp, Signal, Home Assistant |
| [Безопасность](https://hermes-agent.nousresearch.com/docs/user-guide/security) | Одобрение команд, сопряжение DM, изоляция контейнеров |
| [Инструменты и наборы инструментов](https://hermes-agent.nousresearch.com/docs/user-guide/features/tools) | 40+ инструментов, система наборов инструментов, бэкенды терминалов |
| [Система навыков](https://hermes-agent.nousresearch.com/docs/user-guide/features/skills) | Процедурная память, Skills Hub, создание навыков |
| [Память](https://hermes-agent.nousresearch.com/docs/user-guide/features/memory) | Постоянная память, профили пользователей, лучшие практики |
| [Интеграция MCP](https://hermes-agent.nousresearch.com/docs/user-guide/features/mcp) | Подключение любого сервера MCP для расширенных возможностей |
| [Планирование Cron](https://hermes-agent.nousresearch.com/docs/user-guide/features/cron) | Запланированные задачи с доставкой на платформу |
| [Файлы контекста](https://hermes-agent.nousresearch.com/docs/user-guide/features/context-files) | Контекст проекта, который формирует каждый разговор |
| [Архитектура](https://hermes-agent.nousresearch.com/docs/developer-guide/architecture) | Структура проекта, цикл агента, ключевые классы |
| [Участие](https://hermes-agent.nousresearch.com/docs/developer-guide/contributing) | Настройка разработки, стиль кода, процесс PR |
| [Справочник CLI](https://hermes-agent.nousresearch.com/docs/reference/cli-commands) | Все команды и флаги |
| [Переменные окружения](https://hermes-agent.nousresearch.com/docs/reference/environment-variables) | Полный справочник переменных окружения |

---

## Миграция из OpenClaw

Если вы переходите из OpenClaw, Hermes может автоматически импортировать ваши настройки, память, навыки и ключи API.

**Во время первой настройки:** Мастер настройки (`hermes setup`) автоматически обнаруживает `~/.openclaw` и предлагает выполнить миграцию перед началом настройки.

**В любое время после установки:**

```bash
hermes claw migrate              # Интерактивная миграция (полный пресет)
hermes claw migrate --dry-run    # Предварительный просмотр того, что будет мигрировано
hermes claw migrate --preset user-data   # Миграция без секретов
hermes claw migrate --overwrite  # Перезапись существующих конфликтов
```

Что импортируется:
- **SOUL.md** — файл персоны
- **Память** — записи MEMORY.md и USER.md
- **Навыки** — пользовательские навыки → `~/.hermes/skills/openclaw-imports/`
- **Список разрешенных команд** — шаблоны одобрения
- **Настройки сообщений** — конфигурации платформ, разрешенные пользователи, рабочая директория
- **Ключи API** — разрешенные секреты (Telegram, OpenRouter, OpenAI, Anthropic, ElevenLabs)
- **TTS ресурсы** — рабочие файлы аудио
- **Инструкции для рабочей среды** — AGENTS.md (с `--workspace-target`)

См. `hermes claw migrate --help` для всех опций или используйте навык `openclaw-migration` для интерактивной миграции под руководством агента с предварительным просмотром.

---

## Участие

Мы приветствуем ваш вклад! См. [Руководство по участию](https://hermes-agent.nousresearch.com/docs/developer-guide/contributing) для настройки разработки, стиля кода и процесса PR.

Краткое руководство для участников — клонируйте и запускайте с помощью `setup-hermes.sh`:

```bash
git clone https://github.com/NousResearch/hermes-agent.git
cd hermes-agent
./setup-hermes.sh     # устанавливает uv, создает venv, устанавливает .[all], создает символическую ссылку ~/.local/bin/hermes
./hermes              # автоматически определяет venv, не нужно `source` заранее
```

Ручной путь (эквивалент вышеизложенного):

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
uv venv .venv --python 3.11
source .venv/bin/activate
uv pip install -e ".[all,dev]"
scripts/run_tests.sh
```

---

## Сообщество

- 💬 [Discord](https://discord.gg/NousResearch)
- 📚 [Skills Hub](https://agentskills.io)
- 🐛 [Issues](https://github.com/NousResearch/hermes-agent/issues)
- 🔌 [computer-use-linux](https://github.com/avifenesh/computer-use-linux) — MCP сервер управления рабочим столом Linux для Hermes и других хостов MCP, с деревьями доступности AT-SPI, вводом Wayland/X11, скриншотами и таргетингом окон композитора.
- 🔌 [HermesClaw](https://github.com/AaronWong1999/hermesclaw) — Мост WeChat от сообщества: Запустите Hermes Agent и OpenClaw на одном аккаунте WeChat.

---

## Лицензия

MIT — см. [LICENSE](LICENSE).

Разработано [Nous Research](https://nousresearch.com).

---

## Архитектура Геркулеса

```text
Пользователь
  ↓
/start (start)
  ↓ Task(orchestrator)
Orchestrator
  ↓↓↓
Специалисты / субагенты
  ↓
Синтез → start → пользователь
```

**Архитектурные инварианты:**

1. **Цепочка:** `user → /start → Task(orchestrator) → Task(specialists)`
2. **Нет Task tool → `MULTI_AGENT_PIPELINE_BLOCKED`** (HARD FAIL, не silent fallback)
3. **L1 writer fan-out > 6** → реструктуризация через суб-оркестраторы
4. **Reader-ветки** без лимита, **writer-ветки:** 3+ → escalate

---

## Компоненты Геркулеса

| Директория | Назначение | Ключевые файлы |
|------------|------------|----------------|
| [`agents/`](agents/) | 33 определения агентов (4 координационных + 29 специалистов) | [`orchestrator.md`](agents/orchestrator.md), [`start.md`](agents/start.md), [`code.md`](agents/code.md) |
| [`rules/`](rules/) | 4 файла `.mdc`, применяемые всегда — глобальные ограничения | [`orchestrator.mdc`](rules/orchestrator.mdc), [`specialists.mdc`](rules/specialists.mdc) |
| [`skills/`](skills/) | 32 сценария рабочего процесса (`SKILL.md`) | [`orchestrator/SKILL.md`](skills/orchestrator/SKILL.md), [`start-workflow/SKILL.md`](skills/start-workflow/SKILL.md) |
| [`docs/`](docs/) | 37 markdown файлов документации | [`delegation-chain.md`](docs/delegation-chain.md), [`MAINTENANCE_RUNBOOK.md`](docs/MAINTENANCE_RUNBOOK.md) |
| [`scripts/`](scripts/) | 8 скриптов × 3 платформы (`.py`/`.sh`/`.ps1`) | [`run-full-repo-benchmark.py`](scripts/run-full-repo-benchmark.py), [`check-policy-encoding.py`](scripts/check-policy-encoding.py) |
| [`benchmarks/`](benchmarks/) | Контракты поведения + транскрипты-примеры (пройденные/не пройденные) | [`behavior-contracts.json`](benchmarks/behavior-contracts.json), [`transcript-cases.json`](benchmarks/transcript-cases.json) |
| [`profiles/`](profiles/) | Расширения, специфичные для проекта (изолированные от ядра) | [`msnmp/`](profiles/msnmp/) — конвейер пентеста |
| [`reports/`](reports/) | Отчеты аудита (архитектура, безопасность, документация, DevOps) | [`architecture-review-comprehensive.md`](reports/architecture-review-comprehensive.md) |
| [`.github/workflows/`](.github/workflows/) | CI валидация при push/PR | [`repo-validation.yml`](.github/workflows/repo-validation.yml) |

---

## Быстрая установка Геркулеса

### Linux, macOS, WSL2, Termux

```bash
curl -fsSL https://raw.githubusercontent.com/NousResearch/hermes-agent/main/scripts/install.sh | bash
```

### Windows (нативная, PowerShell) — Ранняя бета

> **Внимание:** Нативная поддержка Windows находится в **ранней бета-версии**. Она устанавливается и работает, но не была так широко протестирована, как наши пути для Linux/macOS/WSL2. Пожалуйста, [сообщайте об ошибках](https://github.com/NousResearch/hermes-agent/issues), когда столкнетесь с проблемами. Для наиболее проверенной настройки Windows сегодня запустите однострочник для Linux выше внутри **WSL2**.

Выполните это в PowerShell:

```powershell
iex (irm https://raw.githubusercontent.com/NousResearch/hermes-agent/main/scripts/install.ps1)
```

Установщик обрабатывает все: uv, Python 3.11, Node.js, ripgrep, ffmpeg, **и портативный Git Bash** (MinGit, распакованный в `%LOCALAPPDATA%\hermes\git` — не требует прав администратора, полностью изолирован от любой системной установки Git). Hermes использует этот встроенный Git Bash для выполнения команд оболочки.

Если у вас уже установлен Git, установщик обнаружит его и использует вместо этого. В противном случае загрузка MinGit размером ~45 МБ — это все, что вам нужно — он не будет касаться или мешать какому-либо системному Git.

> **Android / Termux:** Проверенный ручной путь документирован в [руководстве Termux](https://hermes-agent.nousresearch.com/docs/getting-started/termux). В Termux Hermes устанавливает кураторский экстра `.[termux]`, потому что полный экстра `.[all]` в настоящее время включает несовместимые с Android голосовые зависимости.
>
> **Windows:** Нативная поддержка Windows поддерживается как **ранняя бета** — однострочник PowerShell выше устанавливает все, но ожидайте шероховатостей и, пожалуйста, сообщайте об ошибках, когда столкнетесь с ними. Если вы предпочитаете использовать WSL2 (наш наиболее проверенный путь для Windows), команда для Linux также работает там. Нативная установка Windows находится в `%LOCALAPPDATA%\hermes`; установки WSL2 находятся в `~/.hermes`, как и в Linux. Единственная функция Hermes, которая в настоящее время требует именно WSL2, — это панель чата в браузере (она использует POSIX PTY — классический CLI и шлюз работают нативно).

После установки:

```bash
source ~/.bashrc    # перезагрузить оболочку (или: source ~/.zshrc)
hermes              # начать чат!
```

---

## Начало работы

```bash
hermes              # Интерактивный CLI — начать разговор
hermes model        # Выбрать ваш LLM-провайдер и модель
hermes tools        # Настроить, какие инструменты включены
hermes config set   # Установить отдельные значения конфигурации
hermes gateway      # Запустить шлюз обмена сообщениями (Telegram, Discord и т.д.)
hermes setup        # Запустить полный мастер настройки (конфигурирует все сразу)
hermes claw migrate # Мигрировать из OpenClaw (если вы переходите из OpenClaw)
hermes update       # Обновить до последней версии
hermes doctor       # Диагностировать любые проблемы
```

📖 **[Полная документация →](https://hermes-agent.nousresearch.com/docs/)**

## CLI vs Сообщения Краткое руководство

Hermes имеет две точки входа: запустите терминальный интерфейс с помощью `hermes`, или запустите шлюз и общайтесь с ним из Telegram, Discord, Slack, WhatsApp, Signal или Email. Как только вы окажетесь в разговоре, многие команды слеша будут общими для обоих интерфейсов.

| Действие | CLI | Платформы сообщений |
|---------|-----|---------------------|
| Начать чат | `hermes` | Запустите `hermes gateway setup` + `hermes gateway start`, затем отправьте боту сообщение |
| Начать новый разговор | `/new` или `/reset` | `/new` или `/reset` |
| Изменить модель | `/model [провайдер:модель]` | `/model [провайдер:модель]` |
| Установить личность | `/personality [имя]` | `/personality [имя]` |
| Повторить или отменить последний ход | `/retry`, `/undo` | `/retry`, `/undo` |
| Сжать контекст / проверить использование | `/compress`, `/usage`, `/insights [--дни N]` | `/compress`, `/usage`, `/insights [дни]` |
| Просмотреть навыки | `/skills` или `/<имя-навыка>` | `/<имя-навыка>` |
| Прервать текущую работу | `Ctrl+C` или отправить новое сообщение | `/stop` или отправить новое сообщение |
| Статус, специфичный для платформы | `/platforms` | `/status`, `/sethome` |

Полные списки команд см. в [руководстве CLI](https://hermes-agent.nousresearch.com/docs/user-guide/cli) и [руководстве шлюза сообщений](https://hermes-agent.nousresearch.com/docs/user-guide/messaging).

---

## Документация

Вся документация находится по адресу **[hermes-agent.nousresearch.com/docs](https://hermes-agent.nousresearch.com/docs/)**:

| Раздел | Что охватывается |
|---------|---------------|
| [Быстрый старт](https://hermes-agent.nousresearch.com/docs/getting-started/quickstart) | Установка → настройка → первый разговор за 2 минуты |
| [Использование CLI](https://hermes-agent.nousresearch.com/docs/user-guide/cli) | Команды, привязки клавиш, личности, сессии |
| [Конфигурация](https://hermes-agent.nousresearch.com/docs/user-guide/configuration) | Файл конфигурации, провайдеры, модели, все опции |
| [Шлюз сообщений](https://hermes-agent.nousresearch.com/docs/user-guide/messaging) | Telegram, Discord, Slack, WhatsApp, Signal, Home Assistant |
| [Безопасность](https://hermes-agent.nousresearch.com/docs/user-guide/security) | Одобрение команд, сопряжение DM, изоляция контейнеров |
| [Инструменты и наборы инструментов](https://hermes-agent.nousresearch.com/docs/user-guide/features/tools) | 40+ инструментов, система наборов инструментов, бэкенды терминалов |
| [Система навыков](https://hermes-agent.nousresearch.com/docs/user-guide/features/skills) | Процедурная память, Skills Hub, создание навыков |
| [Память](https://hermes-agent.nousresearch.com/docs/user-guide/features/memory) | Постоянная память, профили пользователей, лучшие практики |
| [Интеграция MCP](https://hermes-agent.nousresearch.com/docs/user-guide/features/mcp) | Подключение любого сервера MCP для расширенных возможностей |
| [Планирование Cron](https://hermes-agent.nousresearch.com/docs/user-guide/features/cron) | Запланированные задачи с доставкой на платформу |
| [Файлы контекста](https://hermes-agent.nousresearch.com/docs/user-guide/features/context-files) | Контекст проекта, который формирует каждый разговор |
| [Архитектура](https://hermes-agent.nousresearch.com/docs/developer-guide/architecture) | Структура проекта, цикл агента, ключевые классы |
| [Участие](https://hermes-agent.nousresearch.com/docs/developer-guide/contributing) | Настройка разработки, стиль кода, процесс PR |
| [Справочник CLI](https://hermes-agent.nousresearch.com/docs/reference/cli-commands) | Все команды и флаги |
| [Переменные окружения](https://hermes-agent.nousresearch.com/docs/reference/environment-variables) | Полный справочник переменных окружения |

---

## Миграция из OpenClaw

Если вы переходите из OpenClaw, Hermes может автоматически импортировать ваши настройки, память, навыки и ключи API.

**Во время первой настройки:** Мастер настройки (`hermes setup`) автоматически обнаруживает `~/.openclaw` и предлагает выполнить миграцию перед началом настройки.

**В любое время после установки:**

```bash
hermes claw migrate              # Интерактивная миграция (полный пресет)
hermes claw migrate --dry-run    # Предварительный просмотр того, что будет мигрировано
hermes claw migrate --preset user-data   # Миграция без секретов
hermes claw migrate --overwrite  # Перезапись существующих конфликтов
```

Что импортируется:
- **SOUL.md** — файл персоны
- **Память** — записи MEMORY.md и USER.md
- **Навыки** — пользовательские навыки → `~/.hermes/skills/openclaw-imports/`
- **Список разрешенных команд** — шаблоны одобрения
- **Настройки сообщений** — конфигурации платформ, разрешенные пользователи, рабочая директория
- **Ключи API** — разрешенные секреты (Telegram, OpenRouter, OpenAI, Anthropic, ElevenLabs)
- **TTS ресурсы** — рабочие файлы аудио
- **Инструкции для рабочей среды** — AGENTS.md (с `--workspace-target`)

См. `hermes claw migrate --help` для всех опций или используйте навык `openclaw-migration` для интерактивной миграции под руководством агента с предварительным просмотром.

---

## Участие

Мы приветствуем ваш вклад! См. [Руководство по участию](https://hermes-agent.nousresearch.com/docs/developer-guide/contributing) для настройки разработки, стиля кода и процесса PR.

Краткое руководство для участников — клонируйте и запускайте с помощью `setup-hermes.sh`:

```bash
git clone https://github.com/NousResearch/hermes-agent.git
cd hermes-agent
./setup-hermes.sh     # устанавливает uv, создает venv, устанавливает .[all], создает символическую ссылку ~/.local/bin/hermes
./hermes              # автоматически определяет venv, не нужно `source` заранее
```

Ручной путь (эквивалент вышеизложенного):

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
uv venv .venv --python 3.11
source .venv/bin/activate
uv pip install -e ".[all,dev]"
scripts/run_tests.sh
```

---

## Сообщество

- 💬 [Discord](https://discord.gg/NousResearch)
- 📚 [Skills Hub](https://agentskills.io)
- 🐛 [Issues](https://github.com/NousResearch/hermes-agent/issues)
- 🔌 [computer-use-linux](https://github.com/avifenesh/computer-use-linux) — MCP сервер управления рабочим столом Linux для Hermes и других хостов MCP, с деревьями доступности AT-SPI, вводом Wayland/X11, скриншотами и таргетингом окон композитора.
- 🔌 [HermesClaw](https://github.com/AaronWong1999/hermesclaw) — Мост WeChat от сообщества: Запустите Hermes Agent и OpenClaw на одном аккаунте WeChat.

---

## Лицензия

MIT — см. [LICENSE](LICENSE).

Разработано [Nous Research](https://nousresearch.com).

---

## Архитектура Геркулеса

```text
Пользователь
  ↓
/start (start)
  ↓ Task(orchestrator)
Orchestrator
  ↓↓↓
Специалисты / субагенты
  ↓
Синтез → start → пользователь
```

**Архитектурные инварианты:**

1. **Цепочка:** `user → /start → Task(orchestrator) → Task(specialists)`
2. **Нет Task tool → `MULTI_AGENT_PIPELINE_BLOCKED`** (HARD FAIL, не silent fallback)
3. **L1 writer fan-out > 6** → реструктуризация через суб-оркестраторы
4. **Reader-ветки** без лимита, **writer-ветки:** 3+ → escalate

---

## Компоненты Геркулеса

| Директория | Назначение | Ключевые файлы |
|------------|------------|----------------|
| [`agents/`](agents/) | 33 определения агентов (4 координационных + 29 специалистов) | [`orchestrator.md`](agents/orchestrator.md), [`start.md`](agents/start.md), [`code.md`](agents/code.md) |
| [`rules/`](rules/) | 4 файла `.mdc`, применяемые всегда — глобальные ограничения | [`orchestrator.mdc`](rules/orchestrator.mdc), [`specialists.mdc`](rules/specialists.mdc) |
| [`skills/`](skills/) | 32 сценария рабочего процесса (`SKILL.md`) | [`orchestrator/SKILL.md`](skills/orchestrator/SKILL.md), [`start-workflow/SKILL.md`](skills/start-workflow/SKILL.md) |
| [`docs/`](docs/) | 37 markdown файлов документации | [`delegation-chain.md`](docs/delegation-chain.md), [`MAINTENANCE_RUNBOOK.md`](docs/MAINTENANCE_RUNBOOK.md) |
| [`scripts/`](scripts/) | 8 скриптов × 3 платформы (`.py`/`.sh`/`.ps1`) | [`run-full-repo-benchmark.py`](scripts/run-full-repo-benchmark.py), [`check-policy-encoding.py`](scripts/check-policy-encoding.py) |
| [`benchmarks/`](benchmarks/) | Контракты поведения + транскрипты-примеры (пройденные/не пройденные) | [`behavior-contracts.json`](benchmarks/behavior-contracts.json), [`transcript-cases.json`](benchmarks/transcript-cases.json) |
| [`profiles/`](profiles/) | Расширения, специфичные для проекта (изолированные от ядра) | [`msnmp/`](profiles/msnmp/) — конвейер пентеста |
| [`reports/`](reports/) | Отчеты аудита (архитектура, безопасность, документация, DevOps) | [`architecture-review-comprehensive.md`](reports/architecture-review-comprehensive.md) |
| [`.github/workflows/`](.github/workflows/) | CI валидация при push/PR | [`repo-validation.yml`](.github/workflows/repo-validation.yml) |

---

## Быстрая установка Геркулеса

### Linux, macOS, WSL2, Termux

```bash
curl -fsSL https://raw.githubusercontent.com/NousResearch/hermes-agent/main/scripts/install.sh | bash
```

### Windows (нативная, PowerShell) — Ранняя бета

> **Внимание:** Нативная поддержка Windows находится в **ранней бета-версии**. Она устанавливается и работает, но не была так широко протестирована, как наши пути для Linux/macOS/WSL2. Пожалуйста, [сообщайте об ошибках](https://github.com/NousResearch/hermes-agent/issues), когда столкнетесь с проблемами. Для наиболее проверенной настройки Windows сегодня запустите однострочник для Linux выше внутри **WSL2**.

Выполните это в PowerShell:

```powershell
iex (irm https://raw.githubusercontent.com/NousResearch/hermes-agent/main/scripts/install.ps1)
```

Установщик обрабатывает все: uv, Python 3.11, Node.js, ripgrep, ffmpeg, **и портативный Git Bash** (MinGit, распакованный в `%LOCALAPPDATA%\hermes\git` — не требует прав администратора, полностью изолирован от любой системной установки Git). Hermes использует этот встроенный Git Bash для выполнения команд оболочки.

Если у вас уже установлен Git, установщик обнаружит его и использует вместо этого. В противном случае загрузка MinGit размером ~45 МБ — это все, что вам нужно — он не будет касаться или мешать какому-либо системному Git.

> **Android / Termux:** Проверенный ручной путь документирован в [руководстве Termux](https://hermes-agent.nousresearch.com/docs/getting-started/termux). В Termux Hermes устанавливает кураторский экстра `.[termux]`, потому что полный экстра `.[all]` в настоящее время включает несовместимые с Android голосовые зависимости.
>
> **Windows:** Нативная поддержка Windows поддерживается как **ранняя бета** — однострочник PowerShell выше устанавливает все, но ожидайте шероховатостей и, пожалуйста, сообщайте об ошибках, когда столкнетесь с ними. Если вы предпочитаете использовать WSL2 (наш наиболее проверенный путь для Windows), команда для Linux также работает там. Нативная установка Windows находится в `%LOCALAPPDATA%\hermes`; установки WSL2 находятся в `~/.hermes`, как и в Linux. Единственная функция Hermes, которая в настоящее время требует именно WSL2, — это панель чата в браузере (она использует POSIX PTY — классический CLI и шлюз работают нативно).

После установки:

```bash
source ~/.bashrc    # перезагрузить оболочку (или: source ~/.zshrc)
hermes              # начать чат!
```

---

## Начало работы

```bash
hermes              # Интерактивный CLI — начать разговор
hermes model        # Выбрать ваш LLM-провайдер и модель
hermes tools        # Настроить, какие инструменты включены
hermes config set   # Установить отдельные значения конфигурации
hermes gateway      # Запустить шлюз обмена сообщениями (Telegram, Discord и т.д.)
hermes setup        # Запустить полный мастер настройки (конфигурирует все сразу)
hermes claw migrate # Мигрировать из OpenClaw (если вы переходите из OpenClaw)
hermes update       # Обновить до последней версии
hermes doctor       # Диагностировать любые проблемы
```

📖 **[Полная документация →](https://hermes-agent.nousresearch.com/docs/)**

## CLI vs Сообщения Краткое руководство

Hermes имеет две точки входа: запустите терминальный интерфейс с помощью `hermes`, или запустите шлюз и общайтесь с ним из Telegram, Discord, Slack, WhatsApp, Signal или Email. Как только вы окажетесь в разговоре, многие команды слеша будут общими для обоих интерфейсов.

| Действие | CLI | Платформы сообщений |
|---------|-----|---------------------|
| Начать чат | `hermes` | Запустите `hermes gateway setup` + `hermes gateway start`, затем отправьте боту сообщение |
| Начать новый разговор | `/new` или `/reset` | `/new` или `/reset` |
| Изменить модель | `/model [провайдер:модель]` | `/model [провайдер:модель]` |
| Установить личность | `/personality [имя]` | `/personality [имя]` |
| Повторить или отменить последний ход | `/retry`, `/undo` | `/retry`, `/undo` |
| Сжать контекст / проверить использование | `/compress`, `/usage`, `/insights [--дни N]` | `/compress`, `/usage`, `/insights [дни]` |
| Просмотреть навыки | `/skills` или `/<имя-навыка>` | `/<имя-навыка>` |
| Прервать текущую работу | `Ctrl+C` или отправить новое сообщение | `/stop` или отправить новое сообщение |
| Статус, специфичный для платформы | `/platforms` | `/status`, `/sethome` |

Полные списки команд см. в [руководстве CLI](https://hermes-agent.nousresearch.com/docs/user-guide/cli) и [руководстве шлюза сообщений](https://hermes-agent.nousresearch.com/docs/user-guide/messaging).

---

## Документация

Вся документация находится по адресу **[hermes-agent.nousresearch.com/docs](https://hermes-agent.nousresearch.com/docs/)**:

| Раздел | Что охватывается |
|---------|---------------|
| [Быстрый старт](https://hermes-agent.nousresearch.com/docs/getting-started/quickstart) | Установка → настройка → первый разговор за 2 минуты |
| [Использование CLI](https://hermes-agent.nousresearch.com/docs/user-guide/cli) | Команды, привязки клавиш, личности, сессии |
| [Конфигурация](https://hermes-agent.nousresearch.com/docs/user-guide/configuration) | Файл конфигурации, провайдеры, модели, все опции |
| [Шлюз сообщений](https://hermes-agent.nousresearch.com/docs/user-guide/messaging) | Telegram, Discord, Slack, WhatsApp, Signal, Home Assistant |
| [Безопасность](https://hermes-agent.nousresearch.com/docs/user-guide/security) | Одобрение команд, сопряжение DM, изоляция контейнеров |
| [Инструменты и наборы инструментов](https://hermes-agent.nousresearch.com/docs/user-guide/features/tools) | 40+ инструментов, система наборов инструментов, бэкенды терминалов |
| [Система навыков](https://hermes-agent.nousresearch.com/docs/user-guide/features/skills) | Процедурная память, Skills Hub, создание навыков |
| [Память](https://hermes-agent.nousresearch.com/docs/user-guide/features/memory) | Постоянная память, профили пользователей, лучшие практики |
| [Интеграция MCP](https://hermes-agent.nousresearch.com/docs/user-guide/features/mcp) | Подключение любого сервера MCP для расширенных возможностей |
| [Планирование Cron](https://hermes-agent.nousresearch.com/docs/user-guide/features/cron) | Запланированные задачи с доставкой на платформу |
| [Файлы контекста](https://hermes-agent.nousresearch.com/docs/user-guide/features/context-files) | Контекст проекта, который формирует каждый разговор |
| [Архитектура](https://hermes-agent.nousresearch.com/docs/developer-guide/architecture) | Структура проекта, цикл агента, ключевые классы |
| [Участие](https://hermes-agent.nousresearch.com/docs/developer-guide/contributing) | Настройка разработки, стиль кода, процесс PR |
| [Справочник CLI](https://hermes-agent.nousresearch.com/docs/reference/cli-commands) | Все команды и флаги |
| [Переменные окружения](https://hermes-agent.nousresearch.com/docs/reference/environment-variables) | Полный справочник переменных окружения |

---

## Миграция из OpenClaw

Если вы переходите из OpenClaw, Hermes может автоматически импортировать ваши настройки, память, навыки и ключи API.

**Во время первой настройки:** Мастер настройки (`hermes setup`) автоматически обнаруживает `~/.openclaw` и предлагает выполнить миграцию перед началом настройки.

**В любое время после установки:**

```bash
hermes claw migrate              # Интерактивная миграция (полный пресет)
hermes claw migrate --dry-run    # Предварительный просмотр того, что будет мигрировано
hermes claw migrate --preset user-data   # Миграция без секретов
hermes claw migrate --overwrite  # Перезапись существующих конфликтов
```

Что импортируется:
- **SOUL.md** — файл персоны
- **Память** — записи MEMORY.md и USER.md
- **Навыки** — пользовательские навыки → `~/.hermes/skills/openclaw-imports/`
- **Список разрешенных команд** — шаблоны одобрения
- **Настройки сообщений** — конфигурации платформ, разрешенные пользователи, рабочая директория
- **Ключи API** — разрешенные секреты (Telegram, OpenRouter, OpenAI, Anthropic, ElevenLabs)
- **TTS ресурсы** — рабочие файлы аудио
- **Инструкции для рабочей среды** — AGENTS.md (с `--workspace-target`)

См. `hermes claw migrate --help` для всех опций или используйте навык `openclaw-migration` для интерактивной миграции под руководством агента с предварительным просмотром.

---

## Участие

Мы приветствуем ваш вклад! См. [Руководство по участию](https://hermes-agent.nousresearch.com/docs/developer-guide/contributing) для настройки разработки, стиля кода и процесса PR.

Краткое руководство для участников — клонируйте и запускайте с помощью `setup-hermes.sh`:

```bash
git clone https://github.com/NousResearch/hermes-agent.git
cd hermes-agent
./setup-hermes.sh     # устанавливает uv, создает venv, устанавливает .[all], создает символическую ссылку ~/.local/bin/hermes
./hermes              # автоматически определяет venv, не нужно `source` заранее
```

Ручной путь (эквивалент вышеизложенного):

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
uv venv .venv --python 3.11
source .venv/bin/activate
uv pip install -e ".[all,dev]"
scripts/run_tests.sh
```

---

## Сообщество

- 💬 [Discord](https://discord.gg/NousResearch)
- 📚 [Skills Hub](https://agentskills.io)
- 🐛 [Issues](https://github.com/NousResearch/hermes-agent/issues)
- 🔌 [computer-use-linux](https://github.com/avifenesh/computer-use-linux) — MCP сервер управления рабочим столом Linux для Hermes и других хостов MCP, с деревьями доступности AT-SPI, вводом Wayland/X11, скриншотами и таргетингом окон композитора.
- 🔌 [HermesClaw](https://github.com/AaronWong1999/hermesclaw) — Мост WeChat от сообщества: Запустите Hermes Agent и OpenClaw на одном аккаунте WeChat.

---

## Лицензия

MIT — см. [LICENSE](LICENSE).

Разработано [Nous Research](https://nousresearch.com).

---

## Архитектура Геркулеса

```text
Пользователь
  ↓
/start (start)
  ↓ Task(orchestrator)
Orchestrator
  ↓↓↓
Специалисты / субагенты
  ↓
Синтез → start → пользователь
```

**Архитектурные инварианты:**

1. **Цепочка:** `user → /start → Task(orchestrator) → Task(specialists)`
2. **Нет Task tool → `MULTI_AGENT_PIPELINE_BLOCKED`** (HARD FAIL, не silent fallback)
3. **L1 writer fan-out > 6** → реструктуризация через суб-оркестраторы
4. **Reader-ветки** без лимита, **writer-ветки:** 3+ → escalate

---

## Компоненты Геркулеса

| Директория | Назначение | Ключевые файлы |
|------------|------------|----------------|
| [`agents/`](agents/) | 33 определения агентов (4 координационных + 29 специалистов) | [`orchestrator.md`](agents/orchestrator.md), [`start.md`](agents/start.md), [`code.md`](agents/code.md) |
| [`rules/`](rules/) | 4 файла `.mdc`, применяемые всегда — глобальные ограничения | [`orchestrator.mdc`](rules/orchestrator.mdc), [`specialists.mdc`](rules/specialists.mdc) |
| [`skills/`](skills/) | 32 сценария рабочего процесса (`SKILL.md`) | [`orchestrator/SKILL.md`](skills/orchestrator/SKILL.md), [`start-workflow/SKILL.md`](skills/start-workflow/SKILL.md) |
| [`docs/`](docs/) | 37 markdown файлов документации | [`delegation-chain.md`](docs/delegation-chain.md), [`MAINTENANCE_RUNBOOK.md`](docs/MAINTENANCE_RUNBOOK.md) |
| [`scripts/`](scripts/) | 8 скриптов × 3 платформы (`.py`/`.sh`/`.ps1`) | [`run-full-repo-benchmark.py`](scripts/run-full-repo-benchmark.py), [`check-policy-encoding.py`](scripts/check-policy-encoding.py) |
| [`benchmarks/`](benchmarks/) | Контракты поведения + транскрипты-примеры (пройденные/не пройденные) | [`behavior-contracts.json`](benchmarks/behavior-contracts.json), [`transcript-cases.json`](benchmarks/transcript-cases.json) |
| [`profiles/`](profiles/) | Расширения, специфичные для проекта (изолированные от ядра) | [`msnmp/`](profiles/msnmp/) — конвейер пентеста |
| [`reports/`](reports/) | Отчеты аудита (архитектура, безопасность, документация, DevOps) | [`architecture-review-comprehensive.md`](reports/architecture-review-comprehensive.md) |
| [`.github/workflows/`](.github/workflows/) | CI валидация при push/PR | [`repo-validation.yml`](.github/workflows/repo-validation.yml) |

---

## Быстрая установка Геркулеса

### Linux, macOS, WSL2, Termux

```bash
curl -fsSL https://raw.githubusercontent.com/NousResearch/hermes-agent/main/scripts/install.sh | bash
```

### Windows (нативная, PowerShell) — Ранняя бета

> **Внимание:** Нативная поддержка Windows находится в **ранней бета-версии**. Она устанавливается и работает, но не была так широко протестирована, как наши пути для Linux/macOS/WSL2. Пожалуйста, [сообщайте об ошибках](https://github.com/NousResearch/hermes-agent/issues), когда столкнетесь с проблемами. Для наиболее проверенной настройки Windows сегодня запустите однострочник для Linux выше внутри **WSL2**.

Выполните это в PowerShell:

```powershell
iex (irm https://raw.githubusercontent.com/NousResearch/hermes-agent/main/scripts/install.ps1)
```

Установщик обрабатывает все: uv, Python 3.11, Node.js, ripgrep, ffmpeg, **и портативный Git Bash** (MinGit, распакованный в `%LOCALAPPDATA%\hermes\git` — не требует прав администратора, полностью изолирован от любой системной установки Git). Hermes использует этот встроенный Git Bash для выполнения команд оболочки.

Если у вас уже установлен Git, установщик обнаружит его и использует вместо этого. В противном случае загрузка MinGit размером ~45 МБ — это все, что вам нужно — он не будет касаться или мешать какому-либо системному Git.

> **Android / Termux:** Проверенный ручной путь документирован в [руководстве Termux](https://hermes-agent.nousresearch.com/docs/getting-started/termux). В Termux Hermes устанавливает кураторский экстра `.[termux]`, потому что полный экстра `.[all]` в настоящее время включает несовместимые с Android голосовые зависимости.
>
> **Windows:** Нативная поддержка Windows поддерживается как **ранняя бета** — однострочник PowerShell выше устанавливает все, но ожидайте шероховатостей и, пожалуйста, сообщайте об ошибках, когда столкнетесь с ними. Если вы предпочитаете использовать WSL2 (наш наиболее проверенный путь для Windows), команда для Linux также работает там. Нативная установка Windows находится в `%LOCALAPPDATA%\hermes`; установки WSL2 находятся в `~/.hermes`, как и в Linux. Единственная функция Hermes, которая в настоящее время требует именно WSL2, — это панель чата в браузере (она использует POSIX PTY — классический CLI и шлюз работают нативно).

После установки:

```bash
source ~/.bashrc    # перезагрузить оболочку (или: source ~/.zshrc)
hermes              # начать чат!
```

---

## Начало работы

```bash
hermes              # Интерактивный CLI — начать разговор
hermes model        # Выбрать ваш LLM-провайдер и модель
hermes tools        # Настроить, какие инструменты включены
hermes config set   # Установить отдельные значения конфигурации
hermes gateway      # Запустить шлюз обмена сообщениями (Telegram, Discord и т.д.)
hermes setup        # Запустить полный мастер настройки (конфигурирует все сразу)
hermes claw migrate # Мигрировать из OpenClaw (если вы переходите из OpenClaw)
hermes update       # Обновить до последней версии
hermes doctor       # Диагностировать любые проблемы
```

📖 **[Полная документация →](https://hermes-agent.nousresearch.com/docs/)**

## CLI vs Сообщения Краткое руководство

Hermes имеет две точки входа: запустите терминальный интерфейс с помощью `hermes`, или запустите шлюз и общайтесь с ним из Telegram, Discord, Slack, WhatsApp, Signal или Email. Как только вы окажетесь в разговоре, многие команды слеша будут общими для обоих интерфейсов.

| Действие | CLI | Платформы сообщений |
|---------|-----|---------------------|
| Начать чат | `hermes` | Запустите `hermes gateway setup` + `hermes gateway start`, затем отправьте боту сообщение |
| Начать новый разговор | `/new` или `/reset` | `/new` или `/reset` |
| Изменить модель | `/model [провайдер:модель]` | `/model [провайдер:модель]` |
| Установить личность | `/personality [имя]` | `/personality [имя]` |
| Повторить или отменить последний ход | `/retry`, `/undo` | `/retry`, `/undo` |
| Сжать контекст / проверить использование | `/compress`, `/usage`, `/insights [--дни N]` | `/compress`, `/usage`, `/insights [дни]` |
| Просмотреть навыки | `/skills` или `/<имя-навыка>` | `/<имя-навыка>` |
| Прервать текущую работу | `Ctrl+C` или отправить новое сообщение | `/stop` или отправить новое сообщение |
| Статус, специфичный для платформы | `/platforms` | `/status`, `/sethome` |

Полные списки команд см. в [руководстве CLI](https://hermes-agent.nousresearch.com/docs/user-guide/cli) и [руководстве шлюза сообщений](https://hermes-agent.nousresearch.com/docs/user-guide/messaging).

---

## Документация

Вся документация находится по адресу **[hermes-agent.nousresearch.com/docs](https://hermes-agent.nousresearch.com/docs/)**:

| Раздел | Что охватывается |
|---------|---------------|
| [Быстрый старт](https://hermes-agent.nousresearch.com/docs/getting-started/quickstart) | Установка → настройка → первый разговор за 2 минуты |
| [Использование CLI](https://hermes-agent.nousresearch.com/docs/user-guide/cli) | Команды, привязки клавиш, личности, сессии |
| [Конфигурация](https://hermes-agent.nousresearch.com/docs/user-guide/configuration) | Файл конфигурации, провайдеры, модели, все опции |
| [Шлюз сообщений](https://hermes-agent.nousresearch.com/docs/user-guide/messaging) | Telegram, Discord, Slack, WhatsApp, Signal, Home Assistant |
| [Безопасность](https://hermes-agent.nousresearch.com/docs/user-guide/security) | Одобрение команд, сопряжение DM, изоляция контейнеров |
| [Инструменты и наборы инструментов](https://hermes-agent.nousresearch.com/docs/user-guide/features/tools) | 40+ инструментов, система наборов инструментов, бэкенды терминалов |
| [Система навыков](https://hermes-agent.nousresearch.com/docs/user-guide/features/skills) | Процедурная память, Skills Hub, создание навыков |
| [Память](https://hermes-agent.nousresearch.com/docs/user-guide/features/memory) | Постоянная память, профили пользователей, лучшие практики |
| [Интеграция MCP](https://hermes-agent.nousresearch.com/docs/user-guide/features/mcp) | Подключение любого сервера MCP для расширенных возможностей |
| [Планирование Cron](https://hermes-agent.nousresearch.com/docs/user-guide/features/cron) | Запланированные задачи с доставкой на платформу |
| [Файлы контекста](https://hermes-agent.nousresearch.com/docs/user-guide/features/context-files) | Контекст проекта, который формирует каждый разговор |
| [Архитектура](https://hermes-agent.nousresearch.com/docs/developer-guide/architecture) | Структура проекта, цикл агента, ключевые классы |
| [Участие](https://hermes-agent.nousresearch.com/docs/developer-guide/contributing) | Настройка разработки, стиль кода, процесс PR |
| [Справочник CLI](https://hermes-agent.nousresearch.com/docs/reference/cli-commands) | Все команды и флаги |
| [Переменные окружения](https://hermes-agent.nousresearch.com/docs/reference/environment-variables) | Полный справочник переменных окружения |

---

## Миграция из OpenClaw

Если вы переходите из OpenClaw, Hermes может автоматически импортировать ваши настройки, память, навыки и ключи API.

**Во время первой настройки:** Мастер настройки (`hermes setup`) автоматически обнаруживает `~/.openclaw` и предлагает выполнить миграцию перед началом настройки.

**В любое время после установки:**

```bash
hermes claw migrate              # Интерактивная миграция (полный пресет)
hermes claw migrate --dry-run    # Предварительный просмотр того, что будет мигрировано
hermes claw migrate --preset user-data   # Миграция без секретов
hermes claw migrate --overwrite  # Перезапись существующих конфликтов
```

Что импортируется:
- **SOUL.md** — файл персоны
- **Память** — записи MEMORY.md и USER.md
- **Навыки** — пользовательские навыки → `~/.hermes/skills/openclaw-imports/`
- **Список разрешенных команд** — шаблоны одобрения
- **Настройки сообщений** — конфигурации платформ, разрешенные пользователи, рабочая директория
- **Ключи API** — разрешенные секреты (Telegram, OpenRouter, OpenAI, Anthropic, ElevenLabs)
- **TTS ресурсы** — рабочие файлы аудио
- **Инструкции для рабочей среды** — AGENTS.md (с `--workspace-target`)

См. `hermes claw migrate --help` для всех опций или используйте навык `openclaw-migration` для интерактивной миграции под руководством агента с предварительным просмотром.

---

## Участие

Мы приветствуем ваш вклад! См. [Руководство по участию](https://hermes-agent.nousresearch.com/docs/developer-guide/contributing) для настройки разработки, стиля кода и процесса PR.

Краткое руководство для участников — клонируйте и запускайте с помощью `setup-hermes.sh`:

```bash
git clone https://github.com/NousResearch/hermes-agent.git
cd hermes-agent
./setup-hermes.sh     # устанавливает uv, создает venv, устанавливает .[all], создает символическую ссылку ~/.local/bin/hermes
./hermes              # автоматически определяет venv, не нужно `source` заранее
```

Ручной путь (эквивалент вышеизложенного):

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
uv venv .venv --python 3.11
source .venv/bin/activate
uv pip install -e ".[all,dev]"
scripts/run_tests.sh
```

---

## Сообщество

- 💬 [Discord](https://discord.gg/NousResearch)
- 📚 [Skills Hub](https://agentskills.io)
- 🐛 [Issues](https://github.com/NousResearch/hermes-agent/issues)
- 🔌 [computer-use-linux](https://github.com/avifenesh/computer-use-linux) — MCP сервер управления рабочим столом Linux для Hermes и других хостов MCP, с деревьями доступности AT-SPI, вводом Wayland/X11, скриншотами и таргетингом окон композитора.
- 🔌 [HermesClaw](https://github.com/AaronWong1999/hermesclaw) — Мост WeChat от сообщества: Запустите Hermes Agent и OpenClaw на одном аккаунте WeChat.

---

## Лицензия

MIT — см. [LICENSE](LICENSE).

Разработано [Nous Research](https://nousresearch.com).

---

## Архитектура Геркулеса

```text
Пользователь
  ↓
/start (start)
  ↓ Task(orchestrator)
Orchestrator
  ↓↓↓
Специалисты / субагенты
  ↓
Синтез → start → пользователь
```

**Архитектурные инварианты:**

1. **Цепочка:** `user → /start → Task(orchestrator) → Task(specialists)`
2. **Нет Task tool → `MULTI_AGENT_PIPELINE_BLOCKED`** (HARD FAIL, не silent fallback)
3. **L1 writer fan-out > 6** → реструктуризация через суб-оркестраторы
4. **Reader-ветки** без лимита, **writer-ветки:** 3+ → escalate

---

## Компоненты Геркулеса

| Директория | Назначение | Ключевые файлы |
|------------|------------|----------------|
| [`agents/`](agents/) | 33 определения агентов (4 координационных + 29 специалистов) | [`orchestrator.md`](agents/orchestrator.md), [`start.md`](agents/start.md), [`code.md`](agents/code.md) |
| [`rules/`](rules/) | 4 файла `.mdc`, применяемые всегда — глобальные ограничения | [`orchestrator.mdc`](rules/orchestrator.mdc), [`specialists.mdc`](rules/specialists.mdc) |
| [`skills/`](skills/) | 32 сценария рабочего процесса (`SKILL.md`) | [`orchestrator/SKILL.md`](skills/orchestrator/SKILL.md), [`start-workflow/SKILL.md`](skills/start-workflow/SKILL.md) |
| [`docs/`](docs/) | 37 markdown файлов документации | [`delegation-chain.md`](docs/delegation-chain.md), [`MAINTENANCE_RUNBOOK.md`](docs/MAINTENANCE_RUNBOOK.md) |
| [`scripts/`](scripts/) | 8 скриптов × 3 платформы (`.py`/`.sh`/`.ps1`) | [`run-full-repo-benchmark.py`](scripts/run-full-repo-benchmark.py), [`check-policy-encoding.py`](scripts/check-policy-encoding.py) |
| [`benchmarks/`](benchmarks/) | Контракты поведения + транскрипты-примеры (пройденные/не пройденные) | [`behavior-contracts.json`](benchmarks/behavior-contracts.json), [`transcript-cases.json`](benchmarks/transcript-cases.json) |
| [`profiles/`](profiles/) | Расширения, специфичные для проекта (изолированные от ядра) | [`msnmp/`](profiles/msnmp/) — конвейер пентеста |
| [`reports/`](reports/) | Отчеты аудита (архитектура, безопасность, документация, DevOps) | [`architecture-review-comprehensive.md`](reports/architecture-review-comprehensive.md) |
| [`.github/workflows/`](.github/workflows/) | CI валидация при push/PR | [`repo-validation.yml`](.github/workflows/repo-validation.yml) |

---

## Быстрая установка Геркулеса

### Linux, macOS, WSL2, Termux

```bash
curl -fsSL https://raw.githubusercontent.com/NousResearch/hermes-agent/main/scripts/install.sh | bash
```

### Windows (нативная, PowerShell) — Ранняя бета

> **Внимание:** Нативная поддержка Windows находится в **ранней бета-версии**. Она устанавливается и работает, но не была так широко протестирована, как наши пути для Linux/macOS/WSL2. Пожалуйста, [сообщайте об ошибках](https://github.com/NousResearch/hermes-agent/issues), когда столкнетесь с проблемами. Для наиболее проверенной настройки Windows сегодня запустите однострочник для Linux выше внутри **WSL2**.

Выполните это в PowerShell:

```powershell
iex (irm https://raw.githubusercontent.com/NousResearch/hermes-agent/main/scripts/install.ps1)
```

Установщик обрабатывает все: uv, Python 3.11, Node.js, ripgrep, ffmpeg, **и портативный Git Bash** (MinGit, распакованный в `%LOCALAPPDATA%\hermes\git` — не требует прав администратора, полностью изолирован от любой системной установки Git). Hermes использует этот встроенный Git Bash для выполнения команд оболочки.

Если у вас уже установлен Git, установщик обнаружит его и использует вместо этого. В противном случае загрузка MinGit размером ~45 МБ — это все, что вам нужно — он не будет касаться или мешать какому-либо системному Git.

> **Android / Termux:** Проверенный ручной путь документирован в [руководстве Termux](https://hermes-agent.nousresearch.com/docs/getting-started/termux). В Termux Hermes устанавливает кураторский экстра `.[termux]`, потому что полный экстра `.[all]` в настоящее время включает несовместимые с Android голосовые зависимости.
>
> **Windows:** Нативная поддержка Windows поддерживается как **ранняя бета** — однострочник PowerShell выше устанавливает все, но ожидайте шероховатостей и, пожалуйста, сообщайте об ошибках, когда столкнетесь с ними. Если вы предпочитаете использовать WSL2 (наш наиболее проверенный путь для Windows), команда для Linux также работает там. Нативная установка Windows находится в `%LOCALAPPDATA%\hermes`; установки WSL2 находятся в `~/.hermes`, как и в Linux. Единственная функция Hermes, которая в настоящее время требует именно WSL2, — это панель чата в браузере (она использует POSIX PTY — классический CLI и шлюз работают нативно).

После установки:

```bash
source ~/.bashrc    # перезагрузить оболочку (или: source ~/.zshrc)
hermes              # начать чат!
```

---

## Начало работы

```bash
hermes              # Интерактивный CLI — начать разговор
hermes model        # Выбрать ваш LLM-провайдер и модель
hermes tools        # Настроить, какие инструменты включены
hermes config set   # Установить отдельные значения конфигурации
hermes gateway      # Запустить шлюз обмена сообщениями (Telegram, Discord и т.д.)
hermes setup        # Запустить полный мастер настройки (конфигурирует все сразу)
hermes claw migrate # Мигрировать из OpenClaw (если вы переходите из OpenClaw)
hermes update       # Обновить до последней версии
hermes doctor       # Диагностировать любые проблемы
```

📖 **[Полная документация →](https://hermes-agent.nousresearch.com/docs/)**

## CLI vs Сообщения Краткое руководство

Hermes имеет две точки входа: запустите терминальный интерфейс с помощью `hermes`, или запустите шлюз и общайтесь с ним из Telegram, Discord, Slack, WhatsApp, Signal или Email. Как только вы окажетесь в разговоре, многие команды слеша будут общими для обоих интерфейсов.

| Действие | CLI | Платформы сообщений |
|---------|-----|---------------------|
| Начать чат | `hermes` | Запустите `hermes gateway setup` + `hermes gateway start`, затем отправьте боту сообщение |
| Начать новый разговор | `/new` или `/reset` | `/new` или `/reset` |
| Изменить модель | `/model [провайдер:модель]` | `/model [провайдер:модель]` |
| Установить личность | `/personality [имя]` | `/personality [имя]` |
| Повторить или отменить последний ход | `/retry`, `/undo` | `/retry`, `/undo` |
| Сжать контекст / проверить использование | `/compress`, `/usage`, `/insights [--дни N]` | `/compress`, `/usage`, `/insights [дни]` |
| Просмотреть навыки | `/skills` или `/<имя-навыка>` | `/<имя-навыка>` |
| Прервать текущую работу | `Ctrl+C` или отправить новое сообщение | `/stop` или отправить новое сообщение |
| Статус, специфичный для платформы | `/platforms` | `/status`, `/sethome` |

Полные списки команд см. в [руководстве CLI](https://hermes-agent.nousresearch.com/docs/user-guide/cli) и [руководстве шлюза сообщений](https://hermes-agent.nousresearch.com/docs/user-guide/messaging).

---

## Документация

Вся документация находится по адресу **[hermes-agent.nousresearch.com/docs](https://hermes-agent.nousresearch.com/docs/)**:

| Раздел | Что охватывается |
|---------|---------------|
| [Быстрый старт](https://hermes-agent.nousresearch.com/docs/getting-started/quickstart) | Установка → настройка → первый разговор за 2 минуты |
| [Использование CLI](https://hermes-agent.nousresearch.com/docs/user-guide/cli) | Команды, привязки клавиш, личности, сессии |
| [Конфигурация](https://hermes-agent.nousresearch.com/docs/user-guide/configuration) | Файл конфигурации, провайдеры, модели, все опции |
| [Шлюз сообщений](https://hermes-agent.nousresearch.com/docs/user-guide/messaging) | Telegram, Discord, Slack, WhatsApp, Signal, Home Assistant |
| [Безопасность](https://hermes-agent.nousresearch.com/docs/user-guide/security) | Одобрение команд, сопряжение DM, изоляция контейнеров |
| [Инструменты и наборы инструментов](https://hermes-agent.nousresearch.com/docs/user-guide/features/tools) | 40+ инструментов, система наборов инструментов, бэкенды терминалов |
| [Система навыков](https://hermes-agent.nousresearch.com/docs/user-guide/features/skills) | Процедурная память, Skills Hub, создание навыков |
| [Память](https://hermes-agent.nousresearch.com/docs/user-guide/features/memory) | Постоянная память, профили пользователей, лучшие практики |
| [Интеграция MCP](https://hermes-agent.nousresearch.com/docs/user-guide/features/mcp) | Подключение любого сервера MCP для расширенных возможностей |
| [Планирование Cron](https://hermes-agent.nousresearch.com/docs/user-guide/features/cron) | Запланированные задачи с доставкой на платформу |
| [Файлы контекста](https://hermes-agent.nousresearch.com/docs/user-guide/features/context-files) | Контекст проекта, который формирует каждый разговор |
| [Архитектура](https://hermes-agent.nousresearch.com/docs/developer-guide/architecture) | Структура проекта, цикл агента, ключевые классы |
| [Участие](https://hermes-agent.nousresearch.com/docs/developer-guide/contributing) | Настройка разработки, стиль кода, процесс PR |
| [Справочник CLI](https://hermes-agent.nousresearch.com/docs/reference/cli-commands) | Все команды и флаги |
| [Переменные окружения](https://hermes-agent.nousresearch.com/docs/reference/environment-variables) | Полный справочник переменных окружения |

---

## Миграция из OpenClaw

Если вы переходите из OpenClaw, Hermes может автоматически импортировать ваши настройки, память, навыки и ключи API.

**Во время первой настройки:** Мастер настройки (`hermes setup`) автоматически обнаруживает `~/.openclaw` и предлагает выполнить миграцию перед началом настройки.

**В любое время после установки:**

```bash
hermes claw migrate              # Интерактивная миграция (полный пресет)
hermes claw migrate --dry-run    # Предварительный просмотр того, что будет мигрировано
hermes claw migrate --preset user-data   # Миграция без секретов
hermes claw migrate --overwrite  # Перезапись существующих конфликтов
```

Что импортируется:
- **SOUL.md** — файл персоны
- **Память** — записи MEMORY.md и USER.md
- **Навыки** — пользовательские навыки → `~/.hermes/skills/openclaw-imports/`
- **Список разрешенных команд** — шаблоны одобрения
- **Настройки сообщений** — конфигурации платформ, разрешенные пользователи, рабочая директория
- **Ключи API** — разрешенные секреты (Telegram, OpenRouter, OpenAI, Anthropic, ElevenLabs)
- **TTS ресурсы** — рабочие файлы аудио
- **Инструкции для рабочей среды** — AGENTS.md (с `--workspace-target`)

См. `hermes claw migrate --help` для всех опций или используйте навык `openclaw-migration` для интерактивной миграции под руководством агента с предварительным просмотром.

---

## Участие

Мы приветствуем ваш вклад! См. [Руководство по участию](https://hermes-agent.nousresearch.com/docs/developer-guide/contributing) для настройки разработки, стиля кода и процесса PR.

Краткое руководство для участников — клонируйте и запускайте с помощью `setup-hermes.sh`:

```bash
git clone https://github.com/NousResearch/hermes-agent.git
cd hermes-agent
./setup-hermes.sh     # устанавливает uv, создает venv, устанавливает .[all], создает символическую ссылку ~/.local/bin/hermes
./hermes              # автоматически определяет venv, не нужно `source` заранее
```

Ручной путь (эквивалент вышеизложенного):

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
uv venv .venv --python 3.11
source .venv/bin/activate
uv pip install -e ".[all,dev]"
scripts/run_tests.sh
```

---

## Сообщество

- 💬 [Discord](https://discord.gg/NousResearch)
- 📚 [Skills Hub](https://agentskills.io)
- 🐛 [Issues](https://github.com/NousResearch/hermes-agent/issues)
- 🔌 [computer-use-linux](https://github.com/avifenesh/computer-use-linux) — MCP сервер управления рабочим столом Linux для Hermes и других хостов MCP, с деревьями доступности AT-SPI, вводом Wayland/X11, скриншотами и таргетингом окон композитора.
- 🔌 [HermesClaw](https://github.com/AaronWong1999/hermesclaw) — Мост WeChat от сообщества: Запустите Hermes Agent и OpenClaw на одном аккаунте WeChat.

---

## Лицензия

MIT — см. [LICENSE](LICENSE).

Разработано [Nous Research](https://nousresearch.com).

---

## Архитектура Геркулеса

```text
Пользователь
  ↓
/start (start)
  ↓ Task(orchestrator)
Orchestrator
  ↓↓↓
Специалисты / субагенты
  ↓
Синтез → start → пользователь
```

**Архитектурные инварианты:**

1. **Цепочка:** `user → /start → Task(orchestrator) → Task(specialists)`
2. **Нет Task tool → `MULTI_AGENT_PIPELINE_BLOCKED`** (HARD FAIL, не silent fallback)
3. **L1 writer fan-out > 6** → реструктуризация через суб-оркестраторы
4. **Reader-ветки** без лимита, **writer-ветки:** 3+ → escalate

---

## Компоненты Геркулеса

| Директория | Назначение | Ключевые файлы |
|------------|------------|----------------|
| [`agents/`](agents/) | 33 определения агентов (4 координационных + 29 специалистов) | [`orchestrator.md`](agents/orchestrator.md), [`start.md`](agents/start.md), [`code.md`](agents/code.md) |
| [`rules/`](rules/) | 4 файла `.mdc`, применяемые всегда — глобальные ограничения | [`orchestrator.mdc`](rules/orchestrator.mdc), [`specialists.mdc`](rules/specialists.mdc) |
| [`skills/`](skills/) | 32 сценария рабочего процесса (`SKILL.md`) | [`orchestrator/SKILL.md`](skills/orchestrator/SKILL.md), [`start-workflow/SKILL.md`](skills/start-workflow/SKILL.md) |
| [`docs/`](docs/) | 37 markdown файлов документации | [`delegation-chain.md`](docs/delegation-chain.md), [`MAINTENANCE_RUNBOOK.md`](docs/MAINTENANCE_RUNBOOK.md) |
| [`scripts/`](scripts/) | 8 скриптов × 3 платформы (`.py`/`.sh`/`.ps1`) | [`run-full-repo-benchmark.py`](scripts/run-full-repo-benchmark.py), [`check-policy-encoding.py`](scripts/check-policy-encoding.py) |
| [`benchmarks/`](benchmarks/) | Контракты поведения + транскрипты-примеры (пройденные/не пройденные) | [`behavior-contracts.json`](benchmarks/behavior-contracts.json), [`transcript-cases.json`](benchmarks/transcript-cases.json) |
| [`profiles/`](profiles/) | Расширения, специфичные для проекта (изолированные от ядра) | [`msnmp/`](profiles/msnmp/) — конвейер пентеста |
| [`reports/`](reports/) | Отчеты аудита (архитектура, безопасность, документация, DevOps) | [`architecture-review-comprehensive.md`](reports/architecture-review-comprehensive.md) |
| [`.github/workflows/`](.github/workflows/) | CI валидация при push/PR | [`repo-validation.yml`](.github/workflows/repo-validation.yml) |

---

## Быстрая установка Геркулеса

### Linux, macOS, WSL2, Termux

```bash
curl -fsSL https://raw.githubusercontent.com/NousResearch/hermes-agent/main/scripts/install.sh | bash
```

### Windows (нативная, PowerShell) — Ранняя бета

> **Внимание:** Нативная поддержка Windows находится в **ранней бета-версии**. Она устанавливается и работает, но не была так широко протестирована, как наши пути для Linux/macOS/WSL2. Пожалуйста, [сообщайте об ошибках](https://github.com/NousResearch/hermes-agent/issues), когда столкнетесь с проблемами. Для наиболее проверенной настройки Windows сегодня запустите однострочник для Linux выше внутри **WSL2**.

Выполните это в PowerShell:

```powershell
iex (irm https://raw.githubusercontent.com/NousResearch/hermes-agent/main/scripts/install.ps1)
```

Установщик обрабатывает все: uv, Python 3.11, Node.js, ripgrep, ffmpeg, **и портативный Git Bash** (MinGit, распакованный в `%LOCALAPPDATA%\hermes\git` — не требует прав администратора, полностью изолирован от любой системной установки Git). Hermes использует этот встроенный Git Bash для выполнения команд оболочки.

Если у вас уже установлен Git, установщик обнаружит его и использует вместо этого. В противном случае загрузка MinGit размером ~45 МБ — это все, что вам нужно — он не будет касаться или мешать какому-либо системному Git.

> **Android / Termux:** Проверенный ручной путь документирован в [руководстве Termux](https://hermes-agent.nousresearch.com/docs/getting-started/termux). В Termux Hermes устанавливает кураторский экстра `.[termux]`, потому что полный экстра `.[all]` в настоящее время включает несовместимые с Android голосовые зависимости.
>
> **Windows:** Нативная поддержка Windows поддерживается как **ранняя бета** — однострочник PowerShell выше устанавливает все, но ожидайте шероховатостей и, пожалуйста, сообщайте об ошибках, когда столкнетесь с ними. Если вы предпочитаете использовать WSL2 (наш наиболее проверенный путь для Windows), команда для Linux также работает там. Нативная установка Windows находится в `%LOCALAPPDATA%\hermes`; установки WSL2 находятся в `~/.hermes`, как и в Linux. Единственная функция Hermes, которая в настоящее время требует именно WSL2, — это панель чата в браузере (она использует POSIX PTY — классический CLI и шлюз работают нативно).

После установки:

```bash
source ~/.bashrc    # перезагрузить оболочку (или: source ~/.zshrc)
hermes              # начать чат!
```

---

## Начало работы

```bash
hermes              # Интерактивный CLI — начать разговор
hermes model        # Выбрать ваш LLM-провайдер и модель
hermes tools        # Настроить, какие инструменты включены
hermes config set   # Установить отдельные значения конфигурации
hermes gateway      # Запустить шлюз обмена сообщениями (Telegram, Discord и т.д.)
hermes setup        # Запустить полный мастер настройки (конфигурирует все сразу)
hermes claw migrate # Мигрировать из OpenClaw (если вы переходите из OpenClaw)
hermes update       # Обновить до последней версии
hermes doctor       # Диагностировать любые проблемы
```

📖 **[Полная документация →](https://hermes-agent.nousresearch.com/docs/)**

## CLI vs Сообщения Краткое руководство

Hermes имеет две точки входа: запустите терминальный интерфейс с помощью `hermes`, или запустите шлюз и общайтесь с ним из Telegram, Discord, Slack, WhatsApp, Signal или Email. Как только вы окажетесь в разговоре, многие команды слеша будут общими для обоих интерфейсов.

| Действие | CLI | Платформы сообщений |
|---------|-----|---------------------|
| Начать чат | `hermes` | Запустите `hermes gateway setup` + `hermes gateway start`, затем отправьте боту сообщение |
| Начать новый разговор | `/new` или `/reset` | `/new` или `/reset` |
| Изменить модель | `/model [провайдер:модель]` | `/model [провайдер:модель]` |
| Установить личность | `/personality [имя]` | `/personality [имя]` |
| Повторить или отменить последний ход | `/retry`, `/undo` | `/retry`, `/undo` |
| Сжать контекст / проверить использование | `/compress`, `/usage`, `/insights [--дни N]` | `/compress`, `/usage`, `/insights [дни]` |
| Просмотреть навыки | `/skills` или `/<имя-навыка>` | `/<имя-навыка>` |
| Прервать текущую работу | `Ctrl+C` или отправить новое сообщение | `/stop` или отправить новое сообщение |
| Статус, специфичный для платформы | `/platforms` | `/status`, `/sethome` |

Полные списки команд см. в [руководстве CLI](https://hermes-agent.nousresearch.com/docs/user-guide/cli) и [руководстве шлюза сообщений](https://hermes-agent.nousresearch.com/docs/user-guide/messaging).

---

## Документация

Вся документация находится по адресу **[hermes-agent.nousresearch.com/docs](https://hermes-agent.nousresearch.com/docs/)**:

| Раздел | Что охватывается |
|---------|---------------|
| [Быстрый старт](https://hermes-agent.nousresearch.com/docs/getting-started/quickstart) | Установка → настройка → первый разговор за 2 минуты |
| [Использование CLI](https://hermes-agent.nousresearch.com/docs/user-guide/cli) | Команды, привязки клавиш, личности, сессии |
| [Конфигурация](https://hermes-agent.nousresearch.com/docs/user-guide/configuration) | Файл конфигурации, провайдеры, модели, все опции |
| [Шлюз сообщений](https://hermes-agent.nousresearch.com/docs/user-guide/messaging) | Telegram, Discord, Slack, WhatsApp, Signal, Home Assistant |
| [Безопасность](https://hermes-agent.nousresearch.com/docs/user-guide/security) | Одобрение команд, сопряжение DM, изоляция контейнеров |
| [Инструменты и наборы инструментов](https://hermes-agent.nousresearch.com/docs/user-guide/features/tools) | 40+ инструментов, система наборов инструментов, бэкенды терминалов |
| [Система навыков](https://hermes-agent.nousresearch.com/docs/user-guide/features/skills) | Процедурная память, Skills Hub, создание навыков |
| [Память](https://hermes-agent.nousresearch.com/docs/user-guide/features/memory) | Постоянная память, профили пользователей, лучшие практики |
| [Интеграция MCP](https://hermes-agent.nousresearch.com/docs/user-guide/features/mcp) | Подключение любого сервера MCP для расширенных возможностей |
| [Планирование Cron](https://hermes-agent.nousresearch.com/docs/user-guide/features/cron) | Запланированные задачи с доставкой на платформу |
| [Файлы контекста](https://hermes-agent.nousresearch.com/docs/user-guide/features/context-files) | Контекст проекта, который формирует каждый разговор |
| [Архитектура](https://hermes-agent.nousresearch.com/docs/developer-guide/architecture) | Структура проекта, цикл агента, ключевые классы |
| [Участие](https://hermes-agent.nousresearch.com/docs/developer-guide/contributing) | Настройка разработки, стиль кода, процесс PR |
| [Справочник CLI](https://hermes-agent.nousresearch.com/docs/reference/cli-commands) | Все команды и флаги |
| [Переменные окружения](https://hermes-agent.nousresearch.com/docs/reference/environment-variables) | Полный справочник переменных окружения |

---

## Миграция из OpenClaw

Если вы переходите из OpenClaw, Hermes может автоматически импортировать ваши настройки, память, навыки и ключи API.

**Во время первой настройки:** Мастер настройки (`hermes setup`) автоматически обнаруживает `~/.openclaw` и предлагает выполнить миграцию перед началом настройки.

**В любое время после установки:**

```bash
hermes claw migrate              # Интерактивная миграция (полный пресет)
hermes claw migrate --dry-run    # Предварительный просмотр того, что будет мигрировано
hermes claw migrate --preset user-data   # Миграция без секретов
hermes claw migrate --overwrite  # Перезапись существующих конфликтов
```

Что импортируется:
- **SOUL.md** — файл персоны
- **Память** — записи MEMORY.md и USER.md
- **Навыки** — пользовательские навыки → `~/.hermes/skills/openclaw-imports/`
- **Список разрешенных команд** — шаблоны одобрения
- **Настройки сообщений** — конфигурации платформ, разрешенные пользователи, рабочая директория
- **Ключи API** — разрешенные секреты (Telegram, OpenRouter, OpenAI, Anthropic, ElevenLabs)
- **TTS ресурсы** — рабочие файлы аудио
- **Инструкции для рабочей среды** — AGENTS.md (с `--workspace-target`)

См. `hermes claw migrate --help` для всех опций или используйте навык `openclaw-migration` для интерактивной миграции под руководством агента с предварительным просмотром.

---

## Участие

Мы приветствуем ваш вклад! См. [Руководство по участию](https://hermes-agent.nousresearch.com/docs/developer-guide/contributing) для настройки разработки, стиля кода и процесса PR.

Краткое руководство для участников — клонируйте и запускайте с помощью `setup-hermes.sh`:

```bash
git clone https://github.com/NousResearch/hermes-agent.git
cd hermes-agent
./setup-hermes.sh     # устанавливает uv, создает venv, устанавливает .[all], создает символическую ссылку ~/.local/bin/hermes
./hermes              # автоматически определяет venv, не нужно `source` заранее
```

Ручной путь (эквивалент вышеизложенного):

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
uv venv .venv --python 3.11
source .venv/bin/activate
uv pip install -e ".[all,dev]"
scripts/run_tests.sh
```

---

## Сообщество

- 💬 [Discord](https://discord.gg/NousResearch)
- 📚 [Skills Hub](https://agentskills.io)
- 🐛 [Issues](https://github.com/NousResearch/hermes-agent/issues)
- 🔌 [computer-use-linux](https://github.com/avifenesh/computer-use-linux) — MCP сервер управления рабочим столом Linux для Hermes и других хостов MCP, с деревьями доступности AT-SPI, вводом Wayland/X11, скриншотами и таргетингом окон композитора.
- 🔌 [HermesClaw](https://github.com/AaronWong1999/hermesclaw) — Мост WeChat от сообщества: Запустите Hermes Agent и OpenClaw на одном аккаунте WeChat.

---

## Лицензия

MIT — см. [LICENSE](LICENSE).

Разработано [Nous Research](https://nousresearch.com).

---

## Архитектура Геркулеса

```text
Пользователь
  ↓
/start (start)
  ↓ Task(orchestrator)
Orchestrator
  ↓↓↓
Специалисты / субагенты
  ↓
Синтез → start → пользователь
```

**Архитектурные инварианты:**

1. **Цепочка:** `user → /start → Task(orchestrator) → Task(specialists)`
2. **Нет Task tool → `MULTI_AGENT_PIPELINE_BLOCKED`** (HARD FAIL, не silent fallback)
3. **L1 writer fan-out > 6** → реструктуризация через суб-оркестраторы
4. **Reader-ветки** без лимита, **writer-ветки:** 3+ → escalate

---

## Компоненты Геркулеса

| Директория | Назначение | Ключевые файлы |
|------------|------------|----------------|
| [`agents/`](agents/) | 33 определения агентов (4 координационных + 29 специалистов) | [`orchestrator.md`](agents/orchestrator.md), [`start.md`](agents/start.md), [`code.md`](agents/code.md) |
| [`rules/`](rules/) | 4 файла `.mdc`, применяемые всегда — глобальные ограничения | [`orchestrator.mdc`](rules/orchestrator.mdc), [`specialists.mdc`](rules/specialists.mdc) |
| [`skills/`](skills/) | 32 сценария рабочего процесса (`SKILL.md`) | [`orchestrator/SKILL.md`](skills/orchestrator/SKILL.md), [`start-workflow/SKILL.md`](skills/start-workflow/SKILL.md) |
| [`docs/`](docs/) | 37 markdown файлов документации | [`delegation-chain.md`](docs/delegation-chain.md), [`MAINTENANCE_RUNBOOK.md`](docs/MAINTENANCE_RUNBOOK.md) |
| [`scripts/`](scripts/) | 8 скриптов × 3 платформы (`.py`/`.sh`/`.ps1`) | [`run-full-repo-benchmark.py`](scripts/run-full-repo-benchmark.py), [`check-policy-encoding.py`](scripts/check-policy-encoding.py) |
| [`benchmarks/`](benchmarks/) | Контракты поведения + транскрипты-примеры (пройденные/не пройденные) | [`behavior-contracts.json`](benchmarks/behavior-contracts.json), [`transcript-cases.json`](benchmarks/transcript-cases.json) |
| [`profiles/`](profiles/) | Расширения, специфичные для проекта (изолированные от ядра) | [`msnmp/`](profiles/msnmp/) — конвейер пентеста |
| [`reports/`](reports/) | Отчеты аудита (архитектура, безопасность, документация, DevOps) | [`architecture-review-comprehensive.md`](reports/architecture-review-comprehensive.md) |
| [`.github/workflows/`](.github/workflows/) | CI валидация при push/PR | [`repo-validation.yml`](.github/workflows/repo-validation.yml) |

---

## Быстрая установка Геркулеса

### Linux, macOS, WSL2, Termux

```bash
curl -fsSL https://raw.githubusercontent.com/NousResearch/hermes-agent/main/scripts/install.sh | bash
```

### Windows (нативная, PowerShell) — Ранняя бета

> **Внимание:** Нативная поддержка Windows находится в **ранней бета-версии**. Она устанавливается и работает, но не была так широко протестирована, как наши пути для Linux/macOS/WSL2. Пожалуйста, [сообщайте об ошибках](https://github.com/NousResearch/hermes-agent/issues), когда столкнетесь с проблемами. Для наиболее проверенной настройки Windows сегодня запустите однострочник для Linux выше внутри **WSL2**.

Выполните это в PowerShell:

```powershell
iex (irm https://raw.githubusercontent.com/NousResearch/hermes-agent/main/scripts/install.ps1)
```

Установщик обрабатывает все: uv, Python 3.11, Node.js, ripgrep, ffmpeg, **и портативный Git Bash** (MinGit, распакованный в `%LOCALAPPDATA%\hermes\git` — не требует прав администратора, полностью изолирован от любой системной установки Git). Hermes использует этот встроенный Git Bash для выполнения команд оболочки.

Если у вас уже установлен Git, установщик обнаружит его и использует вместо этого. В противном случае загрузка MinGit размером ~45 МБ — это все, что вам нужно — он не будет касаться или мешать какому-либо системному Git.

> **Android / Termux:** Проверенный ручной путь документирован в [руководстве Termux](https://hermes-agent.nousresearch.com/docs/getting-started/termux). В Termux Hermes устанавливает кураторский экстра `.[termux]`, потому что полный экстра `.[all]` в настоящее время включает несовместимые с Android голосовые зависимости.
>
> **Windows:** Нативная поддержка Windows поддерживается как **ранняя бета** — однострочник PowerShell выше устанавливает все, но ожидайте шероховатостей и, пожалуйста, сообщайте об ошибках, когда столкнетесь с ними. Если вы предпочитаете использовать WSL2 (наш наиболее проверенный путь для Windows), команда для Linux также работает там. Нативная установка Windows находится в `%LOCALAPPDATA%\hermes`; установки WSL2 находятся в `~/.hermes`, как и в Linux. Единственная функция Hermes, которая в настоящее время требует именно WSL2, — это панель чата в браузере (она использует POSIX PTY — классический CLI и шлюз работают нативно).

После установки:

```bash
source ~/.bashrc    # перезагрузить оболочку (или: source ~/.zshrc)
hermes              # начать чат!
```

---

## Начало работы

```bash
hermes              # Интерактивный CLI — начать разговор
hermes model        # Выбрать ваш LLM-провайдер и модель
hermes tools        # Настроить, какие инструменты включены
hermes config set   # Установить отдельные значения конфигурации
hermes gateway      # Запустить шлюз обмена сообщениями (Telegram, Discord и т.д.)
hermes setup        # Запустить полный мастер настройки (конфигурирует все сразу)
hermes claw migrate # Мигрировать из OpenClaw (если вы переходите из OpenClaw)
hermes update       # Обновить до последней версии
hermes doctor       # Диагностировать любые проблемы
```

📖 **[Полная документация →](https://hermes-agent.nousresearch.com/docs/)**

## CLI vs Сообщения Краткое руководство

Hermes имеет две точки входа: запустите терминальный интерфейс с помощью `hermes`, или запустите шлюз и общайтесь с ним из Telegram, Discord, Slack, WhatsApp, Signal или Email. Как только вы окажетесь в разговоре, многие команды слеша будут общими для обоих интерфейсов.

| Действие | CLI | Платформы сообщений |
|---------|-----|---------------------|
| Начать чат | `hermes` | Запустите `hermes gateway setup` + `hermes gateway start`, затем отправьте боту сообщение |
| Начать новый разговор | `/new` или `/reset` | `/new` или `/reset` |
| Изменить модель | `/model [провайдер:модель]` | `/model [провайдер:модель]` |
| Установить личность | `/personality [имя]` | `/personality [имя]` |
| Повторить или отменить последний ход | `/retry`, `/undo` | `/retry`, `/undo` |
| Сжать контекст / проверить использование | `/compress`, `/usage`, `/insights [--дни N]` | `/compress`, `/usage`, `/insights [дни]` |
| Просмотреть навыки | `/skills` или `/<имя-навыка>` | `/<имя-навыка>` |
| Прервать текущую работу | `Ctrl+C` или отправить новое сообщение | `/stop` или отправить новое сообщение |
| Статус, специфичный для платформы | `/platforms` | `/status`, `/sethome` |

Полные списки команд см. в [руководстве CLI](https://hermes-agent.nousresearch.com/docs/user-guide/cli) и [руководстве шлюза сообщений](https://hermes-agent.nousresearch.com/docs/user-guide/messaging).

---

## Документация

Вся документация находится по адресу **[hermes-agent.nousresearch.com/docs](https://hermes-agent.nousresearch.com/docs/)**:

| Раздел | Что охватывается |
|---------|---------------|
| [Быстрый старт](https://hermes-agent.nousresearch.com/docs/getting-started/quickstart) | Установка → настройка → первый разговор за 2 минуты |
| [Использование CLI](https://hermes-agent.nousresearch.com/docs/user-guide/cli) | Команды, привязки клавиш, личности, сессии |
| [Конфигурация](https://hermes-agent.nousresearch.com/docs/user-guide/configuration) | Файл конфигурации, провайдеры, модели, все опции |
| [Шлюз сообщений](https://hermes-agent.nousresearch.com/docs/user-guide/messaging) | Telegram, Discord, Slack, WhatsApp, Signal, Home Assistant |
| [Безопасность](https://hermes-agent.nousresearch.com/docs/user-guide/security) | Одобрение команд, сопряжение DM, изоляция контейнеров |
| [Инструменты и наборы инструментов](https://hermes-agent.nousresearch.com/docs/user-guide/features/tools) | 40+ инструментов, система наборов инструментов, бэкенды терминалов |
| [Система навыков](https://hermes-agent.nousresearch.com/docs/user-guide/features/skills) | Процедурная память, Skills Hub, создание навыков |
| [Память](https://hermes-agent.nousresearch.com/docs/user-guide/features/memory) | Постоянная память, профили пользователей, лучшие практики |
| [Интеграция MCP](https://hermes-agent.nousresearch.com/docs/user-guide/features/mcp) | Подключение любого сервера MCP для расширенных возможностей |
| [Планирование Cron](https://hermes-agent.nousresearch.com/docs/user-guide/features/cron) | Запланированные задачи с доставкой на платформу |
| [Файлы контекста](https://hermes-agent.nousresearch.com/docs/user-guide/features/context-files) | Контекст проекта, который формирует каждый разговор |
| [Архитектура](https://hermes-agent.nousresearch.com/docs/developer-guide/architecture) | Структура проекта, цикл агента, ключевые классы |
| [Участие](https://hermes-agent.nousresearch.com/docs/developer-guide/contributing) | Настройка разработки, стиль кода, процесс PR |
| [Справочник CLI](https://hermes-agent.nousresearch.com/docs/reference/cli-commands) | Все команды и флаги |
| [Переменные окружения](https://hermes-agent.nousresearch.com/docs/reference/environment-variables) | Полный справочник переменных окружения |

---

## Миграция из OpenClaw

Если вы переходите из OpenClaw, Hermes может автоматически импортировать ваши настройки, память, навыки и ключи API.

**Во время первой настройки:** Мастер настройки (`hermes setup`) автоматически обнаруживает `~/.openclaw` и предлагает выполнить миграцию перед началом настройки.

**В любое время после установки:**

```bash
hermes claw migrate              # Интерактивная миграция (полный пресет)
hermes claw migrate --dry-run    # Предварительный просмотр того, что будет мигрировано
hermes claw migrate --preset user-data   # Миграция без секретов
hermes claw migrate --overwrite  # Перезапись существующих конфликтов
```

Что импортируется:
- **SOUL.md** — файл персоны
- **Память** — записи MEMORY.md и USER.md
- **Навыки** — пользовательские навыки → `~/.hermes/skills/openclaw-imports/`
- **Список разрешенных команд** — шаблоны одобрения
- **Настройки сообщений** — конфигурации платформ, разрешенные пользователи, рабочая директория
- **Ключи API** — разрешенные секреты (Telegram, OpenRouter, OpenAI, Anthropic, ElevenLabs)
- **TTS ресурсы** — рабочие файлы аудио
- **Инструкции для рабочей среды** — AGENTS.md (с `--workspace-target`)

См. `hermes claw migrate --help` для всех опций или используйте навык `openclaw-migration` для интерактивной миграции под руководством агента с предварительным просмотром.

---

## Участие

Мы приветствуем ваш вклад! См. [Руководство по участию](https://hermes-agent.nousresearch.com/docs/developer-guide/contributing) для настройки разработки, стиля кода и процесса PR.

Краткое руководство для участников — клонируйте и запускайте с помощью `setup-hermes.sh`:

```bash
git clone https://github.com/NousResearch/hermes-agent.git
cd hermes-agent
./setup-hermes.sh     # устанавливает uv, создает venv, устанавливает .[all], создает символическую ссылку ~/.local/bin/hermes
./hermes              # автоматически определяет venv, не нужно `source` заранее
```

Ручной путь (эквивалент вышеизложенного):

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
uv venv .venv --python 3.11
source .venv/bin/activate
uv pip install -e ".[all,dev]"
scripts/run_tests.sh
```

---

## Сообщество

- 💬 [Discord](https://discord.gg/NousResearch)
- 📚 [Skills Hub](https://agentskills.io)
- 🐛 [Issues](https://github.com/NousResearch/hermes-agent/issues)
- 🔌 [computer-use-linux](https://github.com/avifenesh/computer-use-linux) — MCP сервер управления рабочим столом Linux для Hermes и других хостов MCP, с деревьями доступности AT-SPI, вводом Wayland/X11, скриншотами и таргетингом окон композитора.
- 🔌 [HermesClaw](https://github.com/AaronWong1999/hermesclaw) — Мост WeChat от сообщества: Запустите Hermes Agent и OpenClaw на одном аккаунте WeChat.

---

## Лицензия

MIT — см. [LICENSE](LICENSE).

Разработано [Nous Research](https://nousresearch.com).

---

## Архитектура Геркулеса

```text
Пользователь
  ↓
/start (start)
  ↓ Task(orchestrator)
Orchestrator
  ↓↓↓
Специалисты / субагенты
  ↓
Синтез → start → пользователь
```

**Архитектурные инварианты:**

1. **Цепочка:** `user → /start → Task(orchestrator) → Task(specialists)`
2. **Нет Task tool → `MULTI_AGENT_PIPELINE_BLOCKED`** (HARD FAIL, не silent fallback)
3. **L1 writer fan-out > 6** → реструктуризация через суб-оркестраторы
4. **Reader-ветки** без лимита, **writer-ветки:** 3+ → escalate

---

## Компоненты Геркулеса

| Директория | Назначение | Ключевые файлы |
|------------|------------|----------------|
| [`agents/`](agents/) | 33 определения агентов (4 координационных + 29 специалистов) | [`orchestrator.md`](agents/orchestrator.md), [`start.md`](agents/start.md), [`code.md`](agents/code.md) |
| [`rules/`](rules/) | 4 файла `.mdc`, применяемые всегда — глобальные ограничения | [`orchestrator.mdc`](rules/orchestrator.mdc), [`specialists.mdc`](rules/specialists.mdc) |
| [`skills/`](skills/) | 32 сценария рабочего процесса (`SKILL.md`) | [`orchestrator/SKILL.md`](skills/orchestrator/SKILL.md), [`start-workflow/SKILL.md`](skills/start-workflow/SKILL.md) |
| [`docs/`](docs/) | 37 markdown файлов документации | [`delegation-chain.md`](docs/delegation-chain.md), [`MAINTENANCE_RUNBOOK.md`](docs/MAINTENANCE_RUNBOOK.md) |
| [`scripts/`](scripts/) | 8 скриптов × 3 платформы (`.py`/`.sh`/`.ps1`) | [`run-full-repo-benchmark.py`](scripts/run-full-repo-benchmark.py), [`check-policy-encoding.py`](scripts/check-policy-encoding.py) |
| [`benchmarks/`](benchmarks/) | Контракты поведения + транскрипты-примеры (пройденные/не пройденные) | [`behavior-contracts.json`](benchmarks/behavior-contracts.json), [`transcript-cases.json`](benchmarks/transcript-cases.json) |
| [`profiles/`](profiles/) | Расширения, специфичные для проекта (изолированные от ядра) | [`msnmp/`](profiles/msnmp/) — конвейер пентеста |
| [`reports/`](reports/) | Отчеты аудита (архитектура, безопасность, документация, DevOps) | [`architecture-review-comprehensive.md`](reports/architecture-review-comprehensive.md) |
| [`.github/workflows/`](.github/workflows/) | CI валидация при push/PR | [`repo-validation.yml`](.github/workflows/repo-validation.yml) |

---

## Быстрая установка Геркулеса

### Linux, macOS, WSL2, Termux

```bash
curl -fsSL https://raw.githubusercontent.com/NousResearch/hermes-agent/main/scripts/install.sh | bash
```

### Windows (нативная, PowerShell) — Ранняя бета

> **Внимание:** Нативная поддержка Windows находится в **ранней бета-версии**. Она устанавливается и работает, но не была так широко протестирована, как наши пути для Linux/macOS/WSL2. Пожалуйста, [сообщайте об ошибках](https://github.com/NousResearch/hermes-agent/issues), когда столкнетесь с проблемами. Для наиболее проверенной настройки Windows сегодня запустите однострочник для Linux выше внутри **WSL2**.

Выполните это в PowerShell:

```powershell
iex (irm https://raw.githubusercontent.com/NousResearch/hermes-agent/main/scripts/install.ps1)
```

Установщик обрабатывает все: uv, Python 3.11, Node.js, ripgrep, ffmpeg, **и портативный Git Bash** (MinGit, распакованный в `%LOCALAPPDATA%\hermes\git` — не требует прав администратора, полностью изолирован от любой системной установки Git). Hermes использует этот встроенный Git Bash для выполнения команд оболочки.

Если у вас уже установлен Git, установщик обнаружит его и использует вместо этого. В противном случае загрузка MinGit размером ~45 МБ — это все, что вам нужно — он не будет касаться или мешать какому-либо системному Git.

> **Android / Termux:** Проверенный ручной путь документирован в [руководстве Termux](https://hermes-agent.nousresearch.com/docs/getting-started/termux). В Termux Hermes устанавливает кураторский экстра `.[termux]`, потому что полный экстра `.[all]` в настоящее время включает несовместимые с Android голосовые зависимости.
>
> **Windows:** Нативная поддержка Windows поддерживается как **ранняя бета** — однострочник PowerShell выше устанавливает все, но ожидайте шероховатостей и, пожалуйста, сообщайте об ошибках, когда столкнетесь с ними. Если вы предпочитаете использовать WSL2 (наш наиболее проверенный путь для Windows), команда для Linux также работает там. Нативная установка Windows находится в `%LOCALAPPDATA%\hermes`; установки WSL2 находятся в `~/.hermes`, как и в Linux. Единственная функция Hermes, которая в настоящее время требует именно WSL2, — это панель чата в браузере (она использует POSIX PTY — классический CLI и шлюз работают нативно).

После установки:

```bash
source ~/.bashrc    # перезагрузить оболочку (или: source ~/.zshrc)
hermes              # начать чат!
```

---

## Начало работы

```bash
hermes              # Интерактивный CLI — начать разговор
hermes model        # Выбрать ваш LLM-провайдер и модель
hermes tools        # Настроить, какие инструменты включены
hermes config set   # Установить отдельные значения конфигурации
hermes gateway      # Запустить шлюз обмена сообщениями (Telegram, Discord и т.д.)
hermes setup        # Запустить полный мастер настройки (конфигурирует все сразу)
hermes claw migrate # Мигрировать из OpenClaw (если вы переходите из OpenClaw)
hermes update       # Обновить до последней версии
hermes doctor       # Диагностировать любые проблемы
```

📖 **[Полная документация →](https://hermes-agent.nousresearch.com/docs/)**

## CLI vs Сообщения Краткое руководство

Hermes имеет две точки входа: запустите терминальный интерфейс с помощью `hermes`, или запустите шлюз и общайтесь с ним из Telegram, Discord, Slack, WhatsApp, Signal или Email. Как только вы окажетесь в разговоре, многие команды слеша будут общими для обоих интерфейсов.

| Действие | CLI | Платформы сообщений |
|---------|-----|---------------------|
| Начать чат | `hermes` | Запустите `hermes gateway setup` + `hermes gateway start`, затем отправьте боту сообщение |
| Начать новый разговор | `/new` или `/reset` | `/new` или `/reset` |
| Изменить модель | `/model [провайдер:модель]` | `/model [провайдер:модель]` |
| Установить личность | `/personality [имя]` | `/personality [имя]` |
| Повторить или отменить последний ход | `/retry`, `/undo` | `/retry`, `/undo` |
| Сжать контекст / проверить использование | `/compress`, `/usage`, `/insights [--дни N]` | `/compress`, `/usage`, `/insights [дни]` |
| Просмотреть навыки | `/skills` или `/<имя-навыка>` | `/<имя-навыка>` |
| Прервать текущую работу | `Ctrl+C` или отправить новое сообщение | `/stop` или отправить новое сообщение |
| Статус, специфичный для платформы | `/platforms` | `/status`, `/sethome` |

Полные списки команд см. в [руководстве CLI](https://hermes-agent.nousresearch.com/docs/user-guide/cli) и [руководстве шлюза сообщений](https://hermes-agent.nousresearch.com/docs/user-guide/messaging).

---

## Документация

Вся документация находится по адресу **[hermes-agent.nousresearch.com/docs](https://hermes-agent.nousresearch.com/docs/)**:

| Раздел | Что охватывается |
|---------|---------------|
| [Быстрый старт](https://hermes-agent.nousresearch.com/docs/getting-started/quickstart) | Установка → настройка → первый разговор за 2 минуты |
| [Использование CLI](https://hermes-agent.nousresearch.com/docs/user-guide/cli) | Команды, привязки клавиш, личности, сессии |
| [Конфигурация](https://hermes-agent.nousresearch.com/docs/user-guide/configuration) | Файл конфигурации, провайдеры, модели, все опции |
| [Шлюз сообщений](https://hermes-agent.nousresearch.com/docs/user-guide/messaging) | Telegram, Discord, Slack, WhatsApp, Signal, Home Assistant |
| [Безопасность](https://hermes-agent.nousresearch.com/docs/user-guide/security) | Одобрение команд, сопряжение DM, изоляция контейнеров |
| [Инструменты и наборы инструментов](https://hermes-agent.nousresearch.com/docs/user-guide/features/tools) | 40+ инструментов, система наборов инструментов, бэкенды терминалов |
| [Система навыков](https://hermes-agent.nousresearch.com/docs/user-guide/features/skills) | Процедурная память, Skills Hub, создание навыков |
| [Память](https://hermes-agent.nousresearch.com/docs/user-guide/features/memory) | Постоянная память, профили пользователей, лучшие практики |
| [Интеграция MCP](https://hermes-agent.nousresearch.com/docs/user-guide/features/mcp) | Подключение любого сервера MCP для расширенных возможностей |
| [Планирование Cron](https://hermes-agent.nousresearch.com/docs/user-guide/features/cron) | Запланированные задачи с доставкой на платформу |
| [Файлы контекста](https://hermes-agent.nousresearch.com/docs/user-guide/features/context-files) | Контекст проекта, который формирует каждый разговор |
| [Архитектура](https://hermes-agent.nousresearch.com/docs/developer-guide/architecture) | Структура проекта, цикл агента, ключевые классы |
| [Участие](https://hermes-agent.nousresearch.com/docs/developer-guide/contributing) | Настройка разработки, стиль кода, процесс PR |
| [Справочник CLI](https://hermes-agent.nousresearch.com/docs/reference/cli-commands) | Все команды и флаги |
| [Переменные окружения](https://hermes-agent.nousresearch.com/docs/reference/environment-variables) | Полный справочник переменных окружения |

---

## Миграция из OpenClaw

Если вы переходите из OpenClaw, Hermes может автоматически импортировать ваши настройки, память, навыки и ключи API.

**Во время первой настройки:** Мастер настройки (`hermes setup`) автоматически обнаруживает `~/.openclaw` и предлагает выполнить миграцию перед началом настройки.

**В любое время после установки:**

```bash
hermes claw migrate              # Интерактивная миграция (полный пресет)
hermes claw migrate --dry-run    # Предварительный просмотр того, что будет мигрировано
hermes claw migrate --preset user-data   # Миграция без секретов
hermes claw migrate --overwrite  # Перезапись существующих конфликтов
```

Что импортируется:
- **SOUL.md** — файл персоны
- **Память** — записи MEMORY.md и USER.md
- **Навыки** — пользовательские навыки → `~/.hermes/skills/openclaw-imports/`
- **Список разрешенных команд** — шаблоны одобрения
- **Настройки сообщений** — конфигурации платформ, разрешенные пользователи, рабочая директория
- **Ключи API** — разрешенные секреты (Telegram, OpenRouter, OpenAI, Anthropic, ElevenLabs)
- **TTS ресурсы** — рабочие файлы аудио
- **Инструкции для рабочей среды** — AGENTS.md (с `--workspace-target`)

См. `hermes claw migrate --help` для всех опций или используйте навык `openclaw-migration` для интерактивной миграции под руководством агента с предварительным просмотром.

---

## Участие

Мы приветствуем ваш вклад! См. [Руководство по участию](https://hermes-agent.nousresearch.com/docs/developer-guide/contributing) для настройки разработки, стиля кода и процесса PR.

Краткое руководство для участников — клонируйте и запускайте с помощью `setup-hermes.sh`:

```bash
git clone https://github.com/NousResearch/hermes-agent.git
cd hermes-agent
./setup-hermes.sh     # устанавливает uv, создает venv, устанавливает .[all], создает символическую ссылку ~/.local/bin/hermes
./hermes              # автоматически определяет venv, не нужно `source` заранее
```

Ручной путь (эквивалент вышеизложенного):

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
uv venv .venv --python 3.11
source .venv/bin/activate
uv pip install -e ".[all,dev]"
scripts/run_tests.sh
```

---

## Сообщество

- 💬 [Discord](https://discord.gg/NousResearch)
- 📚 [Skills Hub](https://agentskills.io)
- 🐛 [Issues](https://github.com/NousResearch/hermes-agent/issues)
- 🔌 [computer-use-linux](https://github.com/avifenesh/computer-use-linux) — MCP сервер управления рабочим столом Linux для Hermes и других хостов MCP, с деревьями доступности AT-SPI, вводом Wayland/X11, скриншотами и таргетингом окон композитора.
- 🔌 [HermesClaw](https://github.com/AaronWong1999/hermesclaw) — Мост WeChat от сообщества: Запустите Hermes Agent и OpenClaw на одном аккаунте WeChat.

---

## Лицензия

MIT — см. [LICENSE](LICENSE).

Разработано [Nous Research](https://nousresearch.com).

---

## Архитектура Геркулеса

```text
Пользователь
  ↓
/start (start)
  ↓ Task(orchestrator)
Orchestrator
  ↓↓↓
Специалисты / субагенты
  ↓
Синтез → start → пользователь
```

**Архитектурные инварианты:**

1. **Цепочка:** `user → /start → Task(orchestrator) → Task(specialists)`
2. **Нет Task tool → `MULTI_AGENT_PIPELINE_BLOCKED`** (HARD FAIL, не silent fallback)
3. **L1 writer fan-out > 6** → реструктуризация через суб-оркестраторы
4. **Reader-ветки** без лимита, **writer-ветки:** 3+ → escalate

---

## Компоненты Геркулеса

| Директория | Назначение | Ключевые файлы |
|------------|------------|----------------|
| [`agents/`](agents/) | 33 определения агентов (4 координационных + 29 специалистов) | [`orchestrator.md`](agents/orchestrator.md), [`start.md`](agents/start.md), [`code.md`](agents/code.md) |
| [`rules/`](rules/) | 4 файла `.mdc`, применяемые всегда — глобальные ограничения | [`orchestrator.mdc`](rules/orchestrator.mdc), [`specialists.mdc`](rules/specialists.mdc) |
| [`skills/`](skills/) | 32 сценария рабочего процесса (`SKILL.md`) | [`orchestrator/SKILL.md`](skills/orchestrator/SKILL.md), [`start-workflow/SKILL.md`](skills/start-workflow/SKILL.md) |
| [`docs/`](docs/) | 37 markdown файлов документации | [`delegation-chain.md`](docs/delegation-chain.md), [`MAINTENANCE_RUNBOOK.md`](docs/MAINTENANCE_RUNBOOK.md) |
| [`scripts/`](scripts/) | 8 скриптов × 3 платформы (`.py`/`.sh`/`.ps1`) | [`run-full-repo-benchmark.py`](scripts/run-full-repo-benchmark.py), [`check-policy-encoding.py`](scripts/check-policy-encoding.py) |
| [`benchmarks/`](benchmarks/) | Контракты поведения + транскрипты-примеры (пройденные/не пройденные) | [`behavior-contracts.json`](benchmarks/behavior-contracts.json), [`transcript-cases.json`](benchmarks/transcript-cases.json) |
| [`profiles/`](profiles/) | Расширения, специфичные для проекта (изолированные от ядра) | [`msnmp/`](profiles/msnmp/) — конвейер пентеста |
| [`reports/`](reports/) | Отчеты аудита (архитектура, безопасность, документация, DevOps) | [`architecture-review-comprehensive.md`](reports/architecture-review-comprehensive.md) |
| [`.github/workflows/`](.github/workflows/) | CI валидация при push/PR | [`repo-validation.yml`](.github/workflows/repo-validation.yml) |

---

## Быстрая установка Геркулеса

### Linux, macOS, WSL2, Termux

```bash
curl -fsSL https://raw.githubusercontent.com/NousResearch/hermes-agent/main/scripts/install.sh | bash
```

### Windows (нативная, PowerShell) — Ранняя бета

> **Внимание:** Нативная поддержка Windows находится в **ранней бета-версии**. Она устанавливается и работает, но не была так широко протестирована, как наши пути для Linux/macOS/WSL2. Пожалуйста, [сообщайте об ошибках](https://github.com/NousResearch/hermes-agent/issues), когда столкнетесь с проблемами. Для наиболее проверенной настройки Windows сегодня запустите однострочник для Linux выше внутри **WSL2**.

Выполните это в PowerShell:

```powershell
iex (irm https://raw.githubusercontent.com/NousResearch/hermes-agent/main/scripts/install.ps1)
```

Установщик обрабатывает все: uv, Python 3.11, Node.js, ripgrep, ffmpeg, **и портативный Git Bash** (MinGit, распакованный в `%LOCALAPPDATA%\hermes\git` — не требует прав администратора, полностью изолирован от любой системной установки Git). Hermes использует этот встроенный Git Bash для выполнения команд оболочки.

Если у вас уже установлен Git, установщик обнаружит его и использует вместо этого. В противном случае загрузка MinGit размером ~45 МБ — это все, что вам нужно — он не будет касаться или мешать какому-либо системному Git.

> **Android / Termux:** Проверенный ручной путь документирован в [руководстве Termux](https://hermes-agent.nousresearch.com/docs/getting-started/termux). В Termux Hermes устанавливает кураторский экстра `.[termux]`, потому что полный экстра `.[all]` в настоящее время включает несовместимые с Android голосовые зависимости.
>
> **Windows:** Нативная поддержка Windows поддерживается как **ранняя бета** — однострочник PowerShell выше устанавливает все, но ожидайте шероховатостей и, пожалуйста, сообщайте об ошибках, когда столкнетесь с ними. Если вы предпочитаете использовать WSL2 (наш наиболее проверенный путь для Windows), команда для Linux также работает там. Нативная установка Windows находится в `%LOCALAPPDATA%\hermes`; установки WSL2 находятся в `~/.hermes`, как и в Linux. Единственная функция Hermes, которая в настоящее время требует именно WSL2, — это панель чата в браузере (она использует POSIX PTY — классический CLI и шлюз работают нативно).

После установки:

```bash
source ~/.bashrc    # перезагрузить оболочку (или: source ~/.zshrc)
hermes              # начать чат!
```

---

## Начало работы

```bash
hermes              # Интерактивный CLI — начать разговор
hermes model        # Выбрать ваш LLM-провайдер и модель
hermes tools        # Настроить, какие инструменты включены
hermes config set   # Установить отдельные значения конфигурации
hermes gateway      # Запустить шлюз обмена сообщениями (Telegram, Discord и т.д.)
hermes setup        # Запустить полный мастер настройки (конфигурирует все сразу)
hermes claw migrate # Мигрировать из OpenClaw (если вы переходите из OpenClaw)
hermes update       # Обновить до последней версии
hermes doctor       # Диагностировать любые проблемы
```

📖 **[Полная документация →](https://hermes-agent.nousresearch.com/docs/)**

## CLI vs Сообщения Краткое руководство

Hermes имеет две точки входа: запустите терминальный интерфейс с помощью `hermes`, или запустите шлюз и общайтесь с ним из Telegram, Discord, Slack, WhatsApp, Signal или Email. Как только вы окажетесь в разговоре, многие команды слеша будут общими для обоих интерфейсов.

| Действие | CLI | Платформы сообщений |
|---------|-----|---------------------|
| Начать чат | `hermes` | Запустите `hermes gateway setup` + `hermes gateway start`, затем отправьте боту сообщение |
| Начать новый разговор | `/new` или `/reset` | `/new` или `/reset` |
| Изменить модель | `/model [провайдер:модель]` | `/model [провайдер:модель]` |
| Установить личность | `/personality [имя]` | `/personality [имя]` |
| Повторить или отменить последний ход | `/retry`, `/undo` | `/retry`, `/undo` |
| Сжать контекст / проверить использование | `/compress`, `/usage`, `/insights [--дни N]` | `/compress`, `/usage`, `/insights [дни]` |
| Просмотреть навыки | `/skills` или `/<имя-навыка>` | `/<имя-навыка>` |
| Прервать текущую работу | `Ctrl+C` или отправить новое сообщение | `/stop` или отправить новое сообщение |
| Статус, специфичный для платформы | `/platforms` | `/status`, `/sethome` |

Полные списки команд см. в [руководстве CLI](https://hermes-agent.nousresearch.com/docs/user-guide/cli) и [руководстве шлюза сообщений](https://hermes-agent.nousresearch.com/docs/user-guide/messaging).

---

## Документация

Вся документация находится по адресу **[hermes-agent.nousresearch.com/docs](https://hermes-agent.nousresearch.com/docs/)**:

| Раздел | Что охватывается |
|---------|---------------|
| [Быстрый старт](https://hermes-agent.nousresearch.com/docs/getting-started/quickstart) | Установка → настройка → первый разговор за 2 минуты |
| [Использование CLI](https://hermes-agent.nousresearch.com/docs/user-guide/cli) | Команды, привязки клавиш, личности, сессии |
| [Конфигурация](https://hermes-agent.nousresearch.com/docs/user-guide/configuration) | Файл конфигурации, провайдеры, модели, все опции |
| [Шлюз сообщений](https://hermes-agent.nousresearch.com/docs/user-guide/messaging) | Telegram, Discord, Slack, WhatsApp, Signal, Home Assistant |
| [Безопасность](https://hermes-agent.nousresearch.com/docs/user-guide/security) | Одобрение команд, сопряжение DM, изоляция контейнеров |
| [Инструменты и наборы инструментов](https://hermes-agent.nousresearch.com/docs/user-guide/features/tools) | 40+ инструментов, система наборов инструментов, бэкенды терминалов |
| [Система навыков](https://hermes-agent.nousresearch.com/docs/user-guide/features/skills) | Процедурная память, Skills Hub, создание навыков |
| [Память](https://hermes-agent.nousresearch.com/docs/user-guide/features/memory) | Постоянная память, профили пользователей, лучшие практики |
| [Интеграция MCP](https://hermes-agent.nousresearch.com/docs/user-guide/features/mcp) | Подключение любого сервера MCP для расширенных возможностей |
| [Планирование Cron](https://hermes-agent.nousresearch.com/docs/user-guide/features/cron) | Запланированные задачи с доставкой на платформу |
| [Файлы контекста](https://hermes-agent.nousresearch.com/docs/user-guide/features/context-files) | Контекст проекта, который формирует каждый разговор |
| [Архитектура](https://hermes-agent.nousresearch.com/docs/developer-guide/architecture) | Структура проекта, цикл агента, ключевые классы |
| [Участие](https://hermes-agent.nousresearch.com/docs/developer-guide/contributing) | Настройка разработки, стиль кода, процесс PR |
| [Справочник CLI](https://hermes-agent.nousresearch.com/docs/reference/cli-commands) | Все команды и флаги |
| [Переменные окружения](https://hermes-agent.nousresearch.com/docs/reference/environment-variables) | Полный справочник переменных окружения |

---

## Миграция из OpenClaw

Если вы переходите из OpenClaw, Hermes может автоматически импортировать ваши настройки, память, навыки и ключи API.

**Во время первой настройки:** Мастер настройки (`hermes setup`) автоматически обнаруживает `~/.openclaw` и предлагает выполнить миграцию перед началом настройки.

**В любое время после установки:**

```bash
hermes claw migrate              # Интерактивная миграция (полный пресет)
hermes claw migrate --dry-run    # Предварительный просмотр того, что будет мигрировано
hermes claw migrate --preset user-data   # Миграция без секретов
hermes claw migrate --overwrite  # Перезапись существующих конфликтов
```

Что импортируется:
- **SOUL.md** — файл персоны
- **Память** — записи MEMORY.md и USER.md
- **Навыки** — пользовательские навыки → `~/.hermes/skills/openclaw-imports/`
- **Список разрешенных команд** — шаблоны одобрения
- **Настройки сообщений** — конфигурации платформ, разрешенные пользователи, рабочая директория
- **Ключи API** — разрешенные секреты (Telegram, OpenRouter, OpenAI, Anthropic, ElevenLabs)
- **TTS ресурсы** — рабочие файлы аудио
- **Инструкции для рабочей среды** — AGENTS.md (с `--workspace-target`)

См. `hermes claw migrate --help` для всех опций или используйте навык `openclaw-migration` для интерактивной миграции под руководством агента с предварительным просмотром.

---

## Участие

Мы приветствуем ваш вклад! См. [Руководство по участию](https://hermes-agent.nousresearch.com/docs/developer-guide/contributing) для настройки разработки, стиля кода и процесса PR.

Краткое руководство для участников — клонируйте и запускайте с помощью `setup-hermes.sh`:

```bash
git clone https://github.com/NousResearch/hermes-agent.git
cd hermes-agent
./setup-hermes.sh     # устанавливает uv, создает venv, устанавливает .[all], создает символическую ссылку ~/.local/bin/hermes
./hermes              # автоматически определяет venv, не нужно `source` заранее
```

Ручной путь (эквивалент вышеизложенного):

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
uv venv .venv --python 3.11
source .venv/bin/activate
uv pip install -e ".[all,dev]"
scripts/run_tests.sh
```

---

## Сообщество

- 💬 [Discord](https://discord.gg/NousResearch)
- 📚 [Skills Hub](https://agentskills.io)
- 🐛 [Issues](https://github.com/NousResearch/hermes-agent/issues)
- 🔌 [computer-use-linux](https://github.com/avifenesh/computer-use-linux) — MCP сервер управления рабочим столом Linux для Hermes и других хостов MCP, с деревьями доступности AT-SPI, вводом Wayland/X11, скриншотами и таргетингом окон композитора.
- 🔌 [HermesClaw](https://github.com/AaronWong1999/hermesclaw) — Мост WeChat от сообщества: Запустите Hermes Agent и OpenClaw на одном аккаунте WeChat.

---

## Лицензия

MIT — см. [LICENSE](LICENSE).

Разработано [Nous Research](https://nousresearch.com).

---

## Архитектура Геркулеса

```text
Пользователь
  ↓
/start (start)
  ↓ Task(orchestrator)
Orchestrator
  ↓↓↓
Специалисты / субагенты
  ↓
Синтез → start → пользователь
```

**Архитектурные инварианты:**

1. **Цепочка:** `user → /start → Task(orchestrator) → Task(specialists)`
2. **Нет Task tool → `MULTI_AGENT_PIPELINE_BLOCKED`** (HARD FAIL, не silent fallback)
3. **L1 writer fan-out > 6** → реструктуризация через суб-оркестраторы
4. **Reader-ветки** без лимита, **writer-ветки:** 3+ → escalate

---

## Компоненты Геркулеса

| Директория | Назначение | Ключевые файлы |
|------------|------------|----------------|
| [`agents/`](agents/) | 33 определения агентов (4 координационных + 29 специалистов) | [`orchestrator.md`](agents/orchestrator.md), [`start.md`](agents/start.md), [`code.md`](agents/code.md) |
| [`rules/`](rules/) | 4 файла `.mdc`, применяемые всегда — глобальные ограничения | [`orchestrator.mdc`](rules/orchestrator.mdc), [`specialists.mdc`](rules/specialists.mdc) |
| [`skills/`](skills/) | 32 сценария рабочего процесса (`SKILL.md`) | [`orchestrator/SKILL.md`](skills/orchestrator/SKILL.md), [`start-workflow/SKILL.md`](skills/start-workflow/SKILL.md) |
| [`docs/`](docs/) | 37 markdown файлов документации | [`delegation-chain.md`](docs/delegation-chain.md), [`MAINTENANCE_RUNBOOK.md`](docs/MAINTENANCE_RUNBOOK.md) |
| [`scripts/`](scripts/) | 8 скриптов × 3 платформы (`.py`/`.sh`/`.ps1`) | [`run-full-repo-benchmark.py`](scripts/run-full-repo-benchmark.py), [`check-policy-encoding.py`](scripts/check-policy-encoding.py) |
| [`benchmarks/`](benchmarks/) | Контракты поведения + транскрипты-примеры (пройденные/не пройденные) | [`behavior-contracts.json`](benchmarks/behavior-contracts.json), [`transcript-cases.json`](benchmarks/transcript-cases.json) |
| [`profiles/`](profiles/) | Расширения, специфичные для проекта (изолированные от ядра) | [`msnmp/`](profiles/msnmp/) — конвейер пентеста |
| [`reports/`](reports/) | Отчеты аудита (архитектура, безопасность, документация, DevOps) | [`architecture-review-comprehensive.md`](reports/architecture-review-comprehensive.md) |
| [`.github/workflows/`](.github/workflows/) | CI валидация при push/PR | [`repo-validation.yml`](.github/workflows/repo-validation.yml) |

---

## Быстрая установка Геркулеса

### Linux, macOS, WSL2, Termux

```bash
curl -fsSL https://raw.githubusercontent.com/NousResearch/hermes-agent/main/scripts/install.sh | bash
```

### Windows (нативная, PowerShell) — Ранняя бета

> **Внимание:** Нативная поддержка Windows находится в **ранней бета-версии**. Она устанавливается и работает, но не была так широко протестирована, как наши пути для Linux/macOS/WSL2. Пожалуйста, [сообщайте об ошибках](https://github.com/NousResearch/hermes-agent/issues), когда столкнетесь с проблемами. Для наиболее проверенной настройки Windows сегодня запустите однострочник для Linux выше внутри **WSL2**.

Выполните это в PowerShell:

```powershell
iex (irm https://raw.githubusercontent.com/NousResearch/hermes-agent/main/scripts/install.ps1)
```

Установщик обрабатывает все: uv, Python 3.11, Node.js, ripgrep, ffmpeg, **и портативный Git Bash** (MinGit, распакованный в `%LOCALAPPDATA%\hermes\git` — не требует прав администратора, полностью изолирован от любой системной установки Git). Hermes использует этот встроенный Git Bash для выполнения команд оболочки.

Если у вас уже установлен Git, установщик обнаружит его и использует вместо этого. В противном случае загрузка MinGit размером ~45 МБ — это все, что вам нужно — он не будет касаться или мешать какому-либо системному Git.

> **Android / Termux:** Проверенный ручной путь документирован в [руководстве Termux](https://hermes-agent.nousresearch.com/docs/getting-started/termux). В Termux Hermes устанавливает кураторский экстра `.[termux]`, потому что полный экстра `.[all]` в настоящее время включает несовместимые с Android голосовые зависимости.
>
> **Windows:** Нативная поддержка Windows поддерживается как **ранняя бета** — однострочник PowerShell выше устанавливает все, но ожидайте шероховатостей и, пожалуйста, сообщайте об ошибках, когда столкнетесь с ними. Если вы предпочитаете использовать WSL2 (наш наиболее проверенный путь для Windows), команда для Linux также работает там. Нативная установка Windows находится в `%LOCALAPPDATA%\hermes`; установки WSL2 находятся в `~/.hermes`, как и в Linux. Единственная функция Hermes, которая в настоящее время требует именно WSL2, — это панель чата в браузере (она использует POSIX PTY — классический CLI и шлюз работают нативно).

После установки:

```bash
source ~/.bashrc    # перезагрузить оболочку (или: source ~/.zshrc)
hermes              # начать чат!
```

---

## Начало работы

```bash
hermes              # Интерактивный CLI — начать разговор
hermes model        # Выбрать ваш LLM-провайдер и модель
hermes tools        # Настроить, какие инструменты включены
hermes config set   # Установить отдельные значения конфигурации
hermes gateway      # Запустить шлюз обмена сообщениями (Telegram, Discord и т.д.)
hermes setup        # Запустить полный мастер настройки (конфигурирует все сразу)
hermes claw migrate # Мигрировать из OpenClaw (если вы переходите из OpenClaw)
hermes update       # Обновить до последней версии
hermes doctor       # Диагностировать любые проблемы
```

📖 **[Полная документация →](https://hermes-agent.nousresearch.com/docs/)**

## CLI vs Сообщения Краткое руководство

Hermes имеет две точки входа: запустите терминальный интерфейс с помощью `hermes`, или запустите шлюз и общайтесь с ним из Telegram, Discord, Slack, WhatsApp, Signal или Email. Как только вы окажетесь в разговоре, многие команды слеша будут общими для обоих интерфейсов.

| Действие | CLI | Платформы сообщений |
|---------|-----|---------------------|
| Начать чат | `hermes` | Запустите `hermes gateway setup` + `hermes gateway start`, затем отправьте боту сообщение |
| Начать новый разговор | `/new` или `/reset` | `/new` или `/reset` |
| Изменить модель | `/model [провайдер:модель]` | `/model [провайдер:модель]` |
| Установить личность | `/personality [имя]` | `/personality [имя]` |
| Повторить или отменить последний ход | `/retry`, `/undo` | `/retry`, `/undo` |
| Сжать контекст / проверить использование | `/compress`, `/usage`, `/insights [--дни N]` | `/compress`, `/usage`, `/insights [дни]` |
| Просмотреть навыки | `/skills` или `/<имя-навыка>` | `/<имя-навыка>` |
| Прервать текущую работу | `Ctrl+C` или отправить новое сообщение | `/stop` или отправить новое сообщение |
| Статус, специфичный для платформы | `/platforms` | `/status`, `/sethome` |

Полные списки команд см. в [руководстве CLI](https://hermes-agent.nousresearch.com/docs/user-guide/cli) и [руководстве шлюза сообщений](https://hermes-agent.nousresearch.com/docs/user-guide/messaging).

---

## Документация

Вся документация находится по адресу **[hermes-agent.nousresearch.com/docs](https://hermes-agent.nousresearch.com/docs/)**:

| Раздел | Что охватывается |
|---------|---------------|
| [Быстрый старт](https://hermes-agent.nousresearch.com/docs/getting-started/quickstart) | Установка → настройка → первый разговор за 2 минуты |
| [Использование CLI](https://hermes-agent.nousresearch.com/docs/user-guide/cli) | Команды, привязки клавиш, личности, сессии |
| [Конфигурация](https://hermes-agent.nousresearch.com/docs/user-guide/configuration) | Файл конфигурации, провайдеры, модели, все опции |
| [Шлюз сообщений](https://hermes-agent.nousresearch.com/docs/user-guide/messaging) | Telegram, Discord, Slack, WhatsApp, Signal, Home Assistant |
| [Безопасность](https://hermes-agent.nousresearch.com/docs/user-guide/security) | Одобрение команд, сопряжение DM, изоляция контейнеров |
| [Инструменты и наборы инструментов](https://hermes-agent.nousresearch.com/docs/user-guide/features/tools) | 40+ инструментов, система наборов инструментов, бэкенды терминалов |
| [Система навыков](https://hermes-agent.nousresearch.com/docs/user-guide/features/skills) | Процедурная память, Skills Hub, создание навыков |
| [Память](https://hermes-agent.nousresearch.com/docs/user-guide/features/memory) | Постоянная память, профили пользователей, лучшие практики |
| [Интеграция MCP](https://hermes-agent.nousresearch.com/docs/user-guide/features/mcp) | Подключение любого сервера MCP для расширенных возможностей |
| [Планирование Cron](https://hermes-agent.nousresearch.com/docs/user-guide/features/cron) | Запланированные задачи с доставкой на платформу |
| [Файлы контекста](https://hermes-agent.nousresearch.com/docs/user-guide/features/context-files) | Контекст проекта, который формирует каждый разговор |
| [Архитектура](https://hermes-agent.nousresearch.com/docs/developer-guide/architecture) | Структура проекта, цикл агента, ключевые классы |
| [Участие](https://hermes-agent.nousresearch.com/docs/developer-guide/contributing) | Настройка разработки, стиль кода, процесс PR |
| [Справочник CLI](https://hermes-agent.nousresearch.com/docs/reference/cli-commands) | Все команды и флаги |
| [Переменные окружения](https://hermes-agent.nousresearch.com/docs/reference/environment-variables) | Полный справочник переменных окружения |

---

## Миграция из OpenClaw

Если вы переходите из OpenClaw, Hermes может автоматически импортировать ваши настройки, память, навыки и ключи API.

**Во время первой настройки:** Мастер настройки (`hermes setup`) автоматически обнаруживает `~/.openclaw` и предлагает выполнить миграцию перед началом настройки.

**В любое время после установки:**

```bash
hermes claw migrate              # Интерактивная миграция (полный пресет)
hermes claw migrate --dry-run    # Предварительный просмотр того, что будет мигрировано
hermes claw migrate --preset user-data   # Миграция без секретов
hermes claw migrate --overwrite  # Перезапись существующих конфликтов
```

Что импортируется:
- **SOUL.md** — файл персоны
- **Память** — записи MEMORY.md и USER.md
- **Навыки** — пользовательские навыки → `~/.hermes/skills/openclaw-imports/`
- **Список разрешенных команд** — шаблоны одобрения
- **Настройки сообщений** — конфигурации платформ, разрешенные пользователи, рабочая директория
- **Ключи API** — разрешенные секреты (Telegram, OpenRouter, OpenAI, Anthropic, ElevenLabs)
- **TTS ресурсы** — рабочие файлы аудио
- **Инструкции для рабочей среды** — AGENTS.md (с `--workspace-target`)

См. `hermes claw migrate --help` для всех опций или используйте навык `openclaw-migration` для интерактивной миграции под руководством агента с предварительным просмотром.

---

## Участие

Мы приветствуем ваш вклад! См. [Руководство по участию](https://hermes-agent.nousresearch.com/docs/developer-guide/contributing) для настройки разработки, стиля кода и процесса PR.

Краткое руководство для участников — клонируйте и запускайте с помощью `setup-hermes.sh`:

```bash
git clone https://github.com/NousResearch/hermes-agent.git
cd hermes-agent
./setup-hermes.sh     # устанавливает uv, создает venv, устанавливает .[all], создает символическую ссылку ~/.local/bin/hermes
./hermes              # автоматически определяет venv, не нужно `source` заранее
```

Ручной путь (эквивалент вышеизложенного):

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
uv venv .venv --python 3.11
source .venv/bin/activate
uv pip install -e ".[all,dev]"
scripts/run_tests.sh
```

---

## Сообщество

- 💬 [Discord](https://discord.gg/NousResearch)
- 📚 [Skills Hub](https://agentskills.io)
- 🐛 [Issues](https://github.com/NousResearch/hermes-agent/issues)
- 🔌 [computer-use-linux](https://github.com/avifenesh/computer-use-linux) — MCP сервер управления рабочим столом Linux для Hermes и других хостов MCP, с деревьями доступности AT-SPI, вводом Wayland/X11, скриншотами и таргетингом окон композитора.
- 🔌 [HermesClaw](https://github.com/AaronWong1999/hermesclaw) — Мост WeChat от сообщества: Запустите Hermes Agent и OpenClaw на одном аккаунте WeChat.

---

## Лицензия

MIT — см. [LICENSE](LICENSE).

Разработано [Nous Research](https://nousresearch.com).

---

## Архитектура Геркулеса

```text
Пользователь
  ↓
/start (start)
  ↓ Task(orchestrator)
Orchestrator
  ↓↓↓
Специалисты / субагенты
  ↓
Синтез → start → пользователь
```

**Архитектурные инварианты:**

1. **Цепочка:** `user → /start → Task(orchestrator) → Task(specialists)`
2. **Нет Task tool → `MULTI_AGENT_PIPELINE_BLOCKED`** (HARD FAIL, не silent fallback)
3. **L1 writer fan-out > 6** → реструктуризация через суб-оркестраторы
4. **Reader-ветки** без лимита, **writer-ветки:** 3+ → escalate

---

## Компоненты Геркулеса

| Директория | Назначение | Ключевые файлы |
|------------|------------|----------------|
| [`agents/`](agents/) | 33 определения агентов (4 координационных + 29 специалистов) | [`orchestrator.md`](agents/orchestrator.md), [`start.md`](agents/start.md), [`code.md`](agents/code.md) |
| [`rules/`](rules/) | 4 файла `.mdc`, применяемые всегда — глобальные ограничения | [`orchestrator.mdc`](rules/orchestrator.mdc), [`specialists.mdc`](rules/specialists.mdc) |
| [`skills/`](skills/) | 32 сценария рабочего процесса (`SKILL.md`) | [`orchestrator/SKILL.md`](skills/orchestrator/SKILL.md), [`start-workflow/SKILL.md`](skills/start-workflow/SKILL.md) |
| [`docs/`](docs/) | 37 markdown файлов документации | [`delegation-chain.md`](docs/delegation-chain.md), [`MAINTENANCE_RUNBOOK.md`](docs/MAINTENANCE_RUNBOOK.md) |
| [`scripts/`](scripts/) | 8 скриптов × 3 платформы (`.py`/`.sh`/`.ps1`) | [`run-full-repo-benchmark.py`](scripts/run-full-repo-benchmark.py), [`check-policy-encoding.py`](scripts/check-policy-encoding.py) |
| [`benchmarks/`](benchmarks/) | Контракты поведения + транскрипты-примеры (пройденные/не пройденные) | [`behavior-contracts.json`](benchmarks/behavior-contracts.json), [`transcript-cases.json`](benchmarks/transcript-cases.json) |
| [`profiles/`](profiles/) | Расширения, специфичные для проекта (изолированные от ядра) | [`msnmp/`](profiles/msnmp/) — конвейер пентеста |
| [`reports/`](reports/) | Отчеты аудита (архитектура, безопасность, документация, DevOps) | [`architecture-review-comprehensive.md`](reports/architecture-review-comprehensive.md) |
| [`.github/workflows/`](.github/workflows/) | CI валидация при push/PR | [`repo-validation.yml`](.github/workflows/repo-validation.yml) |

---

## Быстрая установка Геркулеса

### Linux, macOS, WSL2, Termux

```bash
curl -fsSL https://raw.githubusercontent.com/NousResearch/hermes-agent/main/scripts/install.sh | bash
```

### Windows (нативная, PowerShell) — Ранняя бета

> **Внимание:** Нативная поддержка Windows находится в **ранней бета-версии**. Она устанавливается и работает, но не была так широко протестирована, как наши пути для Linux/macOS/WSL2. Пожалуйста, [сообщайте об ошибках](https://github.com/NousResearch/hermes-agent/issues), когда столкнетесь с проблемами. Для наиболее проверенной настройки Windows сегодня запустите однострочник для Linux выше внутри **WSL2**.

Выполните это в PowerShell:

```powershell
iex (irm https://raw.githubusercontent.com/NousResearch/hermes-agent/main/scripts/install.ps1)
```

Установщик обрабатывает все: uv, Python 3.11, Node.js, ripgrep, ffmpeg, **и портативный Git Bash** (MinGit, распакованный в `%LOCALAPPDATA%\hermes\git` — не требует прав администратора, полностью изолирован от любой системной установки Git). Hermes использует этот встроенный Git Bash для выполнения команд оболочки.

Если у вас уже установлен Git, установщик обнаружит его и использует вместо этого. В противном случае загрузка MinGit размером ~45 МБ — это все, что вам нужно — он не будет касаться или мешать какому-либо системному Git.

> **Android / Termux:** Проверенный ручной путь документирован в [руководстве Termux](https://hermes-agent.nousresearch.com/docs/getting-started/termux). В Termux Hermes устанавливает кураторский экстра `.[termux]`, потому что полный экстра `.[all]` в настоящее время включает несовместимые с Android голосовые зависимости.
>
> **Windows:** Нативная поддержка Windows поддерживается как **ранняя бета** — однострочник PowerShell выше устанавливает все, но ожидайте шероховатостей и, пожалуйста, сообщайте об ошибках, когда столкнетесь с ними. Если вы предпочитаете использовать WSL2 (наш наиболее проверенный путь для Windows), команда для Linux также работает там. Нативная установка Windows находится в `%LOCALAPPDATA%\hermes`; установки WSL2 находятся в `~/.hermes`, как и в Linux. Единственная функция Hermes, которая в настоящее время требует именно WSL2, — это панель чата в браузере (она использует POSIX PTY — классический CLI и шлюз работают нативно).

После установки:

```bash
source ~/.bashrc    # перезагрузить оболочку (или: source ~/.zshrc)
hermes              # начать чат!
```

---

## Начало работы

```bash
hermes              # Интерактивный CLI — начать разговор
hermes model        # Выбрать ваш LLM-провайдер и модель
hermes tools        # Настроить, какие инструменты включены
hermes config set   # Установить отдельные значения конфигурации
hermes gateway      # Запустить шлюз обмена сообщениями (Telegram, Discord и т.д.)
hermes setup        # Запустить полный мастер настройки (конфигурирует все сразу)
hermes claw migrate # Мигрировать из OpenClaw (если вы переходите из OpenClaw)
hermes update       # Обновить до последней версии
hermes doctor       # Диагностировать любые проблемы
```

📖 **[Полная документация →](https://hermes-agent.nousresearch.com/docs/)**

## CLI vs Сообщения Краткое руководство

Hermes имеет две точки входа: запустите терминальный интерфейс с помощью `hermes`, или запустите шлюз и общайтесь с ним из Telegram, Discord, Slack, WhatsApp, Signal или Email. Как только вы окажетесь в разговоре, многие команды слеша будут общими для обоих интерфейсов.

| Действие | CLI | Платформы сообщений |
|---------|-----|---------------------|
| Начать чат | `hermes` | Запустите `hermes gateway setup` + `hermes gateway start`, затем отправьте боту сообщение |
| Начать новый разговор | `/new` или `/reset` | `/new` или `/reset` |
| Изменить модель | `/model [провайдер:модель]` | `/model [провайдер:модель]` |
| Установить личность | `/personality [имя]` | `/personality [имя]` |
| Повторить или отменить последний ход | `/retry`, `/undo` | `/retry`, `/undo` |
| Сжать контекст / проверить использование | `/compress`, `/usage`, `/insights [--дни N]` | `/compress`, `/usage`, `/insights [дни]` |
| Просмотреть навыки | `/skills` или `/<имя-навыка>` | `/<имя-навыка>` |
| Прервать текущую работу | `Ctrl+C` или отправить новое сообщение | `/stop` или отправить новое сообщение |
| Статус, специфичный для платформы | `/platforms` | `/status`, `/sethome` |

Полные списки команд см. в [руководстве CLI](https://hermes-agent.nousresearch.com/docs/user-guide/cli) и [руководстве шлюза сообщений](https://hermes-agent.nousresearch.com/docs/user-guide/messaging).

---

## Документация

Вся документация находится по адресу **[hermes-agent.nousresearch.com/docs](https://hermes-agent.nousresearch.com/docs/)**:

| Раздел | Что охватывается |
|---------|---------------|
| [Быстрый старт](https://hermes-agent.nousresearch.com/docs/getting-started/quickstart) | Установка → настройка → первый разговор за 2 минуты |
| [Использование CLI](https://hermes-agent.nousresearch.com/docs/user-guide/cli) | Команды, привязки клавиш, личности, сессии |
| [Конфигурация](https://hermes-agent.nousresearch.com/docs/user-guide/configuration) | Файл конфигурации, провайдеры, модели, все опции |
| [Шлюз сообщений](https://hermes-agent.nousresearch.com/docs/user-guide/messaging) | Telegram, Discord, Slack, WhatsApp, Signal, Home Assistant |
| [Безопасность](https://hermes-agent.nousresearch.com/docs/user-guide/security) | Одобрение команд, сопряжение DM, изоляция контейнеров |
| [Инструменты и наборы инструментов](https://hermes-agent.nousresearch.com/docs/user-guide/features/tools) | 40+ инструментов, система наборов инструментов, бэкенды терминалов |
| [Система навыков](https://hermes-agent.nousresearch.com/docs/user-guide/features/skills) | Процедурная память, Skills Hub, создание навыков |
| [Память](https://hermes-agent.nousresearch.com/docs/user-guide/features/memory) | Постоянная память, профили пользователей, лучшие практики |
| [Интеграция MCP](https://hermes-agent.nousresearch.com/docs/user-guide/features/mcp) | Подключение любого сервера MCP для расширенных возможностей |
| [Планирование Cron](https://hermes-agent.nousresearch.com/docs/user-guide/features/cron) | Запланированные задачи с доставкой на платформу |
| [Файлы контекста](https://hermes-agent.nousresearch.com/docs/user-guide/features/context-files) | Контекст проекта, который формирует каждый разговор |
| [Архитектура](https://hermes-agent.nousresearch.com/docs/developer-guide/architecture) | Структура проекта, цикл агента, ключевые классы |
| [Участие](https://hermes-agent.nousresearch.com/docs/developer-guide/contributing) | Настройка разработки, стиль кода, процесс PR |
| [Справочник CLI](https://hermes-agent.nousresearch.com/docs/reference/cli-commands) | Все команды и флаги |
| [Переменные окружения](https://hermes-agent.nousresearch.com/docs/reference/environment-variables) | Полный справочник переменных окружения |

---

## Миграция из OpenClaw

Если вы переходите из OpenClaw, Hermes может автоматически импортировать ваши настройки, память, навыки и ключи API.

**Во время первой настройки:** Мастер настройки (`hermes setup`) автоматически обнаруживает `~/.openclaw` и предлагает выполнить миграцию перед началом настройки.

**В любое время после установки:**

```bash
hermes claw migrate              # Интерактивная миграция (полный пресет)
hermes claw migrate --dry-run    # Предварительный просмотр того, что будет мигрировано
hermes claw migrate --preset user-data   # Миграция без секретов
hermes claw migrate --overwrite  # Перезапись существующих конфликтов
```

Что импортируется:
- **SOUL.md** — файл персоны
- **Память** — записи MEMORY.md и USER.md
- **Навыки** — пользовательские навыки → `~/.hermes/skills/openclaw-imports/`
- **Список разрешенных команд** — шаблоны одобрения
- **Настройки сообщений** — конфигурации платформ, разрешенные пользователи, рабочая директория
- **Ключи API** — разрешенные секреты (Telegram, OpenRouter, OpenAI, Anthropic, ElevenLabs)
- **TTS ресурсы** — рабочие файлы аудио
- **Инструкции для рабочей среды** — AGENTS.md (с `--workspace-target`)

См. `hermes claw migrate --help` для всех опций или используйте навык `openclaw-migration` для интерактивной миграции под руководством агента с предварительным просмотром.

---

## Участие

Мы приветствуем ваш вклад! См. [Руководство по участию](https://hermes-agent.nousresearch.com/docs/developer-guide/contributing) для настройки разработки, стиля кода и процесса PR.

Краткое руководство для участников — клонируйте и запускайте с помощью `setup-hermes.sh`:

```bash
git clone https://github.com/NousResearch/hermes-agent.git
cd hermes-agent
./setup-hermes.sh     # устанавливает uv, создает venv, устанавливает .[all], создает символическую ссылку ~/.local/bin/hermes
./hermes              # автоматически определяет venv, не нужно `source` заранее
```

Ручной путь (эквивалент вышеизложенного):

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
uv venv .venv --python 3.11
source .venv/bin/activate
uv pip install -e ".[all,dev]"
scripts/run_tests.sh
```

---

## Сообщество

- 💬 [Discord](https://discord.gg/NousResearch)
- 📚 [Skills Hub](https://agentskills.io)
- 🐛 [Issues](https://github.com/NousResearch/hermes-agent/issues)
- 🔌 [computer-use-linux](https://github.com/avifenesh/computer-use-linux) — MCP сервер управления рабочим столом Linux для Hermes и других хостов MCP, с деревьями доступности AT-SPI, вводом Wayland/X11, скриншотами и таргетингом окон композитора.
- 🔌 [HermesClaw](https://github.com/AaronWong1999/hermesclaw) — Мост WeChat от сообщества: Запустите Hermes Agent и OpenClaw на одном аккаунте WeChat.

---

## Лицензия

MIT — см. [LICENSE](LICENSE).

Разработано [Nous Research](https://nousresearch.com).

---

## Архитектура Геркулеса

```text
Пользователь
  ↓
/start (start)
  ↓ Task(orchestrator)
Orchestrator
  ↓↓↓
Специалисты / субагенты
  ↓
Синтез → start → пользователь
```

**Архитектурные инварианты:**

1. **Цепочка:** `user → /start → Task(orchestrator) → Task(specialists)`
2. **Нет Task tool → `MULTI_AGENT_PIPELINE_BLOCKED`** (HARD FAIL, не silent fallback)
3. **L1 writer fan-out > 6** → реструктуризация через суб-оркестраторы
4. **Reader-ветки** без лимита, **writer-ветки:** 3+ → escalate

---

## Компоненты Геркулеса

| Директория | Назначение | Ключевые файлы |
|------------|------------|----------------|
| [`agents/`](agents/) | 33 определения агентов (4 координационных + 29 специалистов) | [`orchestrator.md`](agents/orchestrator.md), [`start.md`](agents/start.md), [`code.md`](agents/code.md) |
| [`rules/`](rules/) | 4 файла `.mdc`, применяемые всегда — глобальные ограничения | [`orchestrator.mdc`](rules/orchestrator.mdc), [`specialists.mdc`](rules/specialists.mdc) |
| [`skills/`](skills/) | 32 сценария рабочего процесса (`SKILL.md`) | [`orchestrator/SKILL.md`](skills/orchestrator/SKILL.md), [`start-workflow/SKILL.md`](skills/start-workflow/SKILL.md) |
| [`docs/`](docs/) | 37 markdown файлов документации | [`delegation-chain.md`](docs/delegation-chain.md), [`MAINTENANCE_RUNBOOK.md`](docs/MAINTENANCE_RUNBOOK.md) |
| [`scripts/`](scripts/) | 8 скриптов × 3 платформы (`.py`/`.sh`/`.ps1`) | [`run-full-repo-benchmark.py`](scripts/run-full-repo-benchmark.py), [`check-policy-encoding.py`](scripts/check-policy-encoding.py) |
| [`benchmarks/`](benchmarks/) | Контракты поведения + транскрипты-примеры (пройденные/не пройденные) | [`behavior-contracts.json`](benchmarks/behavior-contracts.json), [`transcript-cases.json`](benchmarks/transcript-cases.json) |
| [`profiles/`](profiles/) | Расширения, специфичные для проекта (изолированные от ядра) | [`msnmp/`](profiles/msnmp/) — конвейер пентеста |
| [`reports/`](reports/) | Отчеты аудита (архитектура, безопасность, документация, DevOps) | [`architecture-review-comprehensive.md`](reports/architecture-review-comprehensive.md) |
| [`.github/workflows/`](.github/workflows/) | CI валидация при push/PR | [`repo-validation.yml`](.github/workflows/repo-validation.yml) |

---

## Быстрая установка Геркулеса

### Linux, macOS, WSL2, Termux

```bash
curl -fsSL https://raw.githubusercontent.com/NousResearch/hermes-agent/main/scripts/install.sh | bash
```

### Windows (нативная, PowerShell) — Ранняя бета

> **Внимание:** Нативная поддержка Windows находится в **ранней бета-версии**. Она устанавливается и работает, но не была так широко протестирована, как наши пути для Linux/macOS/WSL2. Пожалуйста, [сообщайте об ошибках](https://github.com/NousResearch/hermes-agent/issues), когда столкнетесь с проблемами. Для наиболее проверенной настройки Windows сегодня запустите однострочник для Linux выше внутри **WSL2**.

Выполните это в PowerShell:

```powershell
iex (irm https://raw.githubusercontent.com/NousResearch/hermes-agent/main/scripts/install.ps1)
```

Установщик обрабатывает все: uv, Python 3.11, Node.js, ripgrep, ffmpeg, **и портативный Git Bash** (MinGit, распакованный в `%LOCALAPPDATA%\hermes\git` — не требует прав администратора, полностью изолирован от любой системной установки Git). Hermes использует этот встроенный Git Bash для выполнения команд оболочки.

Если у вас уже установлен Git, установщик обнаружит его и использует вместо этого. В противном случае загрузка MinGit размером ~45 МБ — это все, что вам нужно — он не будет касаться или мешать какому-либо системному Git.

> **Android / Termux:** Проверенный ручной путь документирован в [руководстве Termux](https://hermes-agent.nousresearch.com/docs/getting-started/termux). В Termux Hermes устанавливает кураторский экстра `.[termux]`, потому что полный экстра `.[all]` в настоящее время включает несовместимые с Android голосовые зависимости.
>
> **Windows:** Нативная поддержка Windows поддерживается как **ранняя бета** — однострочник PowerShell выше устанавливает все, но ожидайте шероховатостей и, пожалуйста, сообщайте об ошибках, когда столкнетесь с ними. Если вы предпочитаете использовать WSL2 (наш наиболее проверенный путь для Windows), команда для Linux также работает там. Нативная установка Windows находится в `%LOCALAPPDATA%\hermes`; установки WSL2 находятся в `~/.hermes`, как и в Linux. Единственная функция Hermes, которая в настоящее время требует именно WSL2, — это панель чата в браузере (она использует POSIX PTY — классический CLI и шлюз работают нативно).

После установки:

```bash
source ~/.bashrc    # перезагрузить оболочку (или: source ~/.zshrc)
hermes              # начать чат!
```

---

## Начало работы

```bash
hermes              # Интерактивный CLI — начать разговор
hermes model        # Выбрать ваш LLM-провайдер и модель
hermes tools        # Настроить, какие инструменты включены
hermes config set   # Установить отдельные значения конфигурации
hermes gateway      # Запустить шлюз обмена сообщениями (Telegram, Discord и т.д.)
hermes setup        # Запустить полный мастер настройки (конфигурирует все сразу)
hermes claw migrate # Мигрировать из OpenClaw (если вы переходите из OpenClaw)
hermes update       # Обновить до последней версии
hermes doctor       # Диагностировать любые проблемы
```

📖 **[Полная документация →](https://hermes-agent.nousresearch.com/docs/)**

## CLI vs Сообщения Краткое руководство

Hermes имеет две точки входа: запустите терминальный интерфейс с помощью `hermes`, или запустите шлюз и общайтесь с ним из Telegram, Discord, Slack, WhatsApp, Signal или Email. Как только вы окажетесь в разговоре, многие команды слеша будут общими для обоих интерфейсов.

| Действие | CLI | Платформы сообщений |
|---------|-----|---------------------|
| Начать чат | `hermes` | Запустите `hermes gateway setup` + `hermes gateway start`, затем отправьте боту сообщение |
| Начать новый разговор | `/new` или `/reset` | `/new` или `/reset` |
| Изменить модель | `/model [провайдер:модель]` | `/model [провайдер:модель]` |
| Установить личность | `/personality [имя]` | `/personality [имя]` |
| Повторить или отменить последний ход | `/retry`, `/undo` | `/retry`, `/undo` |
| Сжать контекст / проверить использование | `/compress`, `/usage`, `/insights [--дни N]` | `/compress`, `/usage`, `/insights [дни]` |
| Просмотреть навыки | `/skills` или `/<имя-навыка>` | `/<имя-навыка>` |
| Прервать текущую работу | `Ctrl+C` или отправить новое сообщение | `/stop` или отправить новое сообщение |
| Статус, специфичный для платформы | `/platforms` | `/status`, `/sethome` |

Полные списки команд см. в [руководстве CLI](https://hermes-agent.nousresearch.com/docs/user-guide/cli) и [руководстве шлюза сообщений](https://hermes-agent.nousresearch.com/docs/user-guide/messaging).

---

## Документация

Вся документация находится по адресу **[hermes-agent.nousresearch.com/docs](https://hermes-agent.nousresearch.com/docs/)**:

| Раздел | Что охватывается |
|---------|---------------|
| [Быстрый старт](https://hermes-agent.nousresearch.com/docs/getting-started/quickstart) | Установка → настройка → первый разговор за 2 минуты |
| [Использование CLI](https://hermes-agent.nousresearch.com/docs/user-guide/cli) | Команды, привязки клавиш, личности, сессии |
| [Конфигурация](https://hermes-agent.nousresearch.com/docs/user-guide/configuration) | Файл конфигурации, провайдеры, модели, все опции |
| [Шлюз сообщений](https://hermes-agent.nousresearch.com/docs/user-guide/messaging) | Telegram, Discord, Slack, WhatsApp, Signal, Home Assistant |
| [Безопасность](https://hermes-agent.nousresearch.com/docs/user-guide/security) | Одобрение команд, сопряжение DM, изоляция контейнеров |
| [Инструменты и наборы инструментов](https://hermes-agent.nousresearch.com/docs/user-guide/features/tools) | 40+ инструментов, система наборов инструментов, бэкенды терминалов |
| [Система навыков](https://hermes-agent.nousresearch.com/docs/user-guide/features/skills) | Процедурная память, Skills Hub, создание навыков |
| [Память](https://hermes-agent.nousresearch.com/docs/user-guide/features/memory) | Постоянная память, профили пользователей, лучшие практики |
| [Интеграция MCP](https://hermes-agent.nousresearch.com/docs/user-guide/features/mcp) | Подключение любого сервера MCP для расширенных возможностей |
| [Планирование Cron](https://hermes-agent.nousresearch.com/docs/user-guide/features/cron) | Запланированные задачи с доставкой на платформу |
| [Файлы контекста](https://hermes-agent.nousresearch.com/docs/user-guide/features/context-files) | Контекст проекта, который формирует каждый разговор |
| [Архитектура](https://hermes-agent.nousresearch.com/docs/developer-guide/architecture) | Структура проекта, цикл агента, ключевые классы |
| [Участие](https://hermes-agent.nousresearch.com/docs/developer-guide/contributing) | Настройка разработки, стиль кода, процесс PR |
| [Справочник CLI](https://hermes-agent.nousresearch.com/docs/reference/cli-commands) | Все команды и флаги |
| [Переменные окружения](https://hermes-agent.nousresearch.com/docs/reference/environment-variables) | Полный справочник переменных окружения |

---

## Миграция из OpenClaw

Если вы переходите из OpenClaw, Hermes может автоматически импортировать ваши настройки, память, навыки и ключи API.

**Во время первой настройки:** Мастер настройки (`hermes setup`) автоматически обнаруживает `~/.openclaw` и предлагает выполнить миграцию перед началом настройки.

**В любое время после установки:**

```bash
hermes claw migrate              # Интерактивная миграция (полный пресет)
hermes claw migrate --dry-run    # Предварительный просмотр того, что будет мигрировано
hermes claw migrate --preset user-data   # Миграция без секретов
hermes claw migrate --overwrite  # Перезапись существующих конфликтов
```

Что импортируется:
- **SOUL.md** — файл персоны
- **Память** — записи MEMORY.md и USER.md
- **Навыки** — пользовательские навыки → `~/.hermes/skills/openclaw-imports/`
- **Список разрешенных команд** — шаблоны одобрения
- **Настройки сообщений** — конфигурации платформ, разрешенные пользователи, рабочая директория
- **Ключи API** — разрешенные секреты (Telegram, OpenRouter, OpenAI, Anthropic, ElevenLabs)
- **TTS ресурсы** — рабочие файлы аудио
- **Инструкции для рабочей среды** — AGENTS.md (с `--workspace-target`)

См. `hermes claw migrate --help` для всех опций или используйте навык `openclaw-migration` для интерактивной миграции под руководством агента с предварительным просмотром.

---

## Участие

Мы приветствуем ваш вклад! См. [Руководство по участию](https://hermes-agent.nousresearch.com/docs/developer-guide/contributing) для настройки разработки, стиля кода и процесса PR.

Краткое руководство для участников — клонируйте и запускайте с помощью `setup-hermes.sh`:

```bash
git clone https://github.com/NousResearch/hermes-agent.git
cd hermes-agent
./setup-hermes.sh     # устанавливает uv, создает venv, устанавливает .[all], создает символическую ссылку ~/.local/bin/hermes
./hermes              # автоматически определяет venv, не нужно `source` заранее
```

Ручной путь (эквивалент вышеизложенного):

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
uv venv .venv --python 3.11
source .venv/bin/activate
uv pip install -e ".[all,dev]"
scripts/run_tests.sh
```

---

## Сообщество

- 💬 [Discord](https://discord.gg/NousResearch)
- 📚 [Skills Hub](https://agentskills.io)
- 🐛 [Issues](https://github.com/NousResearch/hermes-agent/issues)
- 🔌 [computer-use-linux](https://github.com/avifenesh/computer-use-linux) — MCP сервер управления рабочим столом Linux для Hermes и других хостов MCP, с деревьями доступности AT-SPI, вводом Wayland/X11, скриншотами и таргетингом окон композитора.
- 🔌 [HermesClaw](https://github.com/AaronWong1999/hermesclaw) — Мост WeChat от сообщества: Запустите Hermes Agent и OpenClaw на одном аккаунте WeChat.

---

## Лицензия

MIT — см. [LICENSE](LICENSE).

Разработано [Nous Research](https://nousresearch.com).

---

## Архитектура Геркулеса

```text
Пользователь
  ↓
/start (start)
  ↓ Task(orchestrator)
Orchestrator
  ↓↓↓
Специалисты / субагенты
  ↓
Синтез → start → пользователь
```

**Архитектурные инварианты:**

1. **Цепочка:** `user → /start → Task(orchestrator) → Task(specialists)`
2. **Нет Task tool → `MULTI_AGENT_PIPELINE_BLOCKED`** (HARD FAIL, не silent fallback)
3. **L1 writer fan-out > 6** → реструктуризация через суб-оркестраторы
4. **Reader-ветки** без лимита, **writer-ветки:** 3+ → escalate

---

## Компоненты Геркулеса

| Директория | Назначение | Ключевые файлы |
|------------|------------|----------------|
| [`agents/`](agents/) | 33 определения агентов (4 координационных + 29 специалистов) | [`orchestrator.md`](agents/orchestrator.md), [`start.md`](agents/start.md), [`code.md`](agents/code.md) |
| [`rules/`](rules/) | 4 файла `.mdc`, применяемые всегда — глобальные ограничения | [`orchestrator.mdc`](rules/orchestrator.mdc), [`specialists.mdc`](rules/specialists.mdc) |
| [`skills/`](skills/) | 32 сценария рабочего процесса (`SKILL.md`) | [`orchestrator/SKILL.md`](skills/orchestrator/SKILL.md), [`start-workflow/SKILL.md`](skills/start-workflow/SKILL.md) |
| [`docs/`](docs/) | 37 markdown файлов документации | [`delegation-chain.md`](docs/delegation-chain.md), [`MAINTENANCE_RUNBOOK.md`](docs/MAINTENANCE_RUNBOOK.md) |
| [`scripts/`](scripts/) | 8 скриптов × 3 платформы (`.py`/`.sh`/`.ps1`) | [`run-full-repo-benchmark.py`](scripts/run-full-repo-benchmark.py), [`check-policy-encoding.py`](scripts/check-policy-encoding.py) |
| [`benchmarks/`](benchmarks/) | Контракты поведения + транскрипты-примеры (пройденные/не пройденные) | [`behavior-contracts.json`](benchmarks/behavior-contracts.json), [`transcript-cases.json`](benchmarks/transcript-cases.json) |
| [`profiles/`](profiles/) | Расширения, специфичные для проекта (изолированные от ядра) | [`msnmp/`](profiles/msnmp/) — конвейер пентеста |
| [`reports/`](reports/) | Отчеты аудита (архитектура, безопасность, документация, DevOps) | [`architecture-review-comprehensive.md`](reports/architecture-review-comprehensive.md) |
| [`.github/workflows/`](.github/workflows/) | CI валидация при push/PR | [`repo-validation.yml`](.github/workflows/repo-validation.yml) |

---

## Быстрая установка Геркулеса

### Linux, macOS, WSL2, Termux

```bash
curl -fsSL https://raw.githubusercontent.com/NousResearch/hermes-agent/main/scripts/install.sh | bash
```

### Windows (нативная, PowerShell) — Ранняя бета

> **Внимание:** Нативная поддержка Windows находится в **ранней бета-версии**. Она устанавливается и работает, но не была так широко протестирована, как наши пути для Linux/macOS/WSL2. Пожалуйста, [сообщайте об ошибках](https://github.com/NousResearch/hermes-agent/issues), когда столкнетесь с проблемами. Для наиболее проверенной настройки Windows сегодня запустите однострочник для Linux выше внутри **WSL2**.

Выполните это в PowerShell:

```powershell
iex (irm https://raw.githubusercontent.com/NousResearch/hermes-agent/main/scripts/install.ps1)
```

Установщик обрабатывает все: uv, Python 3.11, Node.js, ripgrep, ffmpeg, **и портативный Git Bash** (MinGit, распакованный в `%LOCALAPPDATA%\hermes\git` — не требует прав администратора, полностью изолирован от любой системной установки Git). Hermes использует этот встроенный Git Bash для выполнения команд оболочки.

Если у вас уже установлен Git, установщик обнаружит его и использует вместо этого. В противном случае загрузка MinGit размером ~45 МБ — это все, что вам нужно — он не будет касаться или мешать какому-либо системному Git.

> **Android / Termux:** Проверенный ручной путь документирован в [руководстве Termux](https://hermes-agent.nousresearch.com/docs/getting-started/termux). В Termux Hermes устанавливает кураторский экстра `.[termux]`, потому что полный экстра `.[all]` в настоящее время включает несовместимые с Android голосовые зависимости.
>
> **Windows:** Нативная поддержка Windows поддерживается как **ранняя бета** — однострочник PowerShell выше устанавливает все, но ожидайте шероховатостей и, пожалуйста, сообщайте об ошибках, когда столкнетесь с ними. Если вы предпочитаете использовать WSL2 (наш наиболее проверенный путь для Windows), команда для Linux также работает там. Нативная установка Windows находится в `%LOCALAPPDATA%\hermes`; установки WSL2 находятся в `~/.hermes`, как и в Linux. Единственная функция Hermes, которая в настоящее время требует именно WSL2, — это панель чата в браузере (она использует POSIX PTY — классический CLI и шлюз работают нативно).

После установки:

```bash
source ~/.bashrc    # перезагрузить оболочку (или: source ~/.zshrc)
hermes              # начать чат!
```

---

## Начало работы

```bash
hermes              # Интерактивный CLI — начать разговор
hermes model        # Выбрать ваш LLM-провайдер и модель
hermes tools        # Настроить, какие инструменты включены
hermes config set   # Установить отдельные значения конфигурации
hermes gateway      # Запустить шлюз обмена сообщениями (Telegram, Discord и т.д.)
hermes setup        # Запустить полный мастер настройки (конфигурирует все сразу)
hermes claw migrate # Мигрировать из OpenClaw (если вы переходите из OpenClaw)
hermes update       # Обновить до последней версии
hermes doctor       # Диагностировать любые проблемы
```

📖 **[Полная документация →](https://hermes-agent.nousresearch.com/docs/)**

## CLI vs Сообщения Краткое руководство

Hermes имеет две точки входа: запустите терминальный интерфейс с помощью `hermes`, или запустите шлюз и общайтесь с ним из Telegram, Discord, Slack, WhatsApp, Signal или Email. Как только вы окажетесь в разговоре, многие команды слеша будут общими для обоих интерфейсов.

| Действие | CLI | Платформы сообщений |
|---------|-----|---------------------|
| Начать чат | `hermes` | Запустите `hermes gateway setup` + `hermes gateway start`, затем отправьте боту сообщение |
| Начать новый разговор | `/new` или `/reset` | `/new` или `/reset` |
| Изменить модель | `/model [провайдер:модель]` | `/model [провайдер:модель]` |
| Установить личность | `/personality [имя]` | `/personality [имя]` |
| Повторить или отменить последний ход | `/retry`, `/undo` | `/retry`, `/undo` |
| Сжать контекст / проверить использование | `/compress`, `/usage`, `/insights [--дни N]` | `/compress`, `/usage`, `/insights [дни]` |
| Просмотреть навыки | `/skills` или `/<имя-навыка>` | `/<имя-навыка>` |
| Прервать текущую работу | `Ctrl+C` или отправить новое сообщение | `/stop` или отправить новое сообщение |
| Статус, специфичный для платформы | `/platforms` | `/status`, `/sethome` |

Полные списки команд см. в [руководстве CLI](https://hermes-agent.nousresearch.com/docs/user-guide/cli) и [руководстве шлюза сообщений](https://hermes-agent.nousresearch.com/docs/user-guide/messaging).

---

## Документация

Вся документация находится по адресу **[hermes-agent.nousresearch.com/docs](https://hermes-agent.nousresearch.com/docs/)**:

| Раздел | Что охватывается |
|---------|---------------|
| [Быстрый старт](https://hermes-agent.nousresearch.com/docs/getting-started/quickstart) | Установка → настройка → первый разговор за 2 минуты |
| [Использование CLI](https://hermes-agent.nousresearch.com/docs/user-guide/cli) | Команды, привязки клавиш, личности, сессии |
| [Конфигурация](https://hermes-agent.nousresearch.com/docs/user-guide/configuration) | Файл конфигурации, провайдеры, модели, все опции |
| [Шлюз сообщений](https://hermes-agent.nousresearch.com/docs/user-guide/messaging) | Telegram, Discord, Slack, WhatsApp, Signal, Home Assistant |
| [Безопасность](https://hermes-agent.nousresearch.com/docs/user-guide/security) | Одобрение команд, сопряжение DM, изоляция контейнеров |
| [Инструменты и наборы инструментов](https://hermes-agent.nousresearch.com/docs/user-guide/features/tools) | 40+ инструментов, система наборов инструментов, бэкенды терминалов |
| [Система навыков](https://hermes-agent.nousresearch.com/docs/user-guide/features/skills) | Процедурная память, Skills Hub, создание навыков |
| [Память](https://hermes-agent.nousresearch.com/docs/user-guide/features/memory) | Постоянная память, профили пользователей, лучшие практики |
| [Интеграция MCP](https://hermes-agent.nousresearch.com/docs/user-guide/features/mcp) | Подключение любого сервера MCP для расширенных возможностей |
| [Планирование Cron](https://hermes-agent.nousresearch.com/docs/user-guide/features/cron) | Запланированные задачи с доставкой на платформу |
| [Файлы контекста](https://hermes-agent.nousresearch.com/docs/user-guide/features/context-files) | Контекст проекта, который формирует каждый разговор |
| [Архитектура](https://hermes-agent.nousresearch.com/docs/developer-guide/architecture) | Структура проекта, цикл агента, ключевые классы |
| [Участие](https://hermes-agent.nousresearch.com/docs/developer-guide/contributing) | Настройка разработки, стиль кода, процесс PR |
| [Справочник CLI](https://hermes-agent.nousresearch.com/docs/reference/cli-commands) | Все команды и флаги |
| [Переменные окружения](https://hermes-agent.nousresearch.com/docs/reference/environment-variables) | Полный справочник переменных окружения |

---

## Миграция из OpenClaw

Если вы переходите из OpenClaw, Hermes может автоматически импортировать ваши настройки, память, навыки и ключи API.

**Во время первой настройки:** Мастер настройки (`hermes setup`) автоматически обнаруживает `~/.openclaw` и предлагает выполнить миграцию перед началом настройки.

**В любое время после установки:**

```bash
hermes claw migrate              # Интерактивная миграция (полный пресет)
hermes claw migrate --dry-run    # Предварительный просмотр того, что будет мигрировано
hermes claw migrate --preset user-data   # Миграция без секретов
hermes claw migrate --overwrite  # Перезапись существующих конфликтов
```

Что импортируется:
- **SOUL.md** — файл персоны
- **Память** — записи MEMORY.md и USER.md
- **Навыки** — пользовательские навыки → `~/.hermes/skills/openclaw-imports/`
- **Список разрешенных команд** — шаблоны одобрения
- **Настройки сообщений** — конфигурации платформ, разрешенные пользователи, рабочая директория
- **Ключи API** — разрешенные секреты (Telegram, OpenRouter, OpenAI, Anthropic, ElevenLabs)
- **TTS ресурсы** — рабочие файлы аудио
- **Инструкции для рабочей среды** — AGENTS.md (с `--workspace-target`)

См. `hermes claw migrate --help` для всех опций или используйте навык `openclaw-migration` для интерактивной миграции под руководством агента с предварительным просмотром.

---

## Участие

Мы приветствуем ваш вклад! См. [Руководство по участию](https://hermes-agent.nousresearch.com/docs/developer-guide/contributing) для настройки разработки, стиля кода и процесса PR.

Краткое руководство для участников — клонируйте и запускайте с помощью `setup-hermes.sh`:

```bash
git clone https://github.com/NousResearch/hermes-agent.git
cd hermes-agent
./setup-hermes.sh     # устанавливает uv, создает venv, устанавливает .[all], создает символическую ссылку ~/.local/bin/hermes
./hermes              # автоматически определяет venv, не нужно `source` заранее
```

Ручной путь (эквивалент вышеизложенного):

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
uv venv .venv --python 3.11
source .venv/bin/activate
uv pip install -e ".[all,dev]"
scripts/run_tests.sh
```

---

## Сообщество

- 💬 [Discord](https://discord.gg/NousResearch)
- 📚 [Skills Hub](https://agentskills.io)
- 🐛 [Issues](https://github.com/NousResearch/hermes-agent/issues)
- 🔌 [computer-use-linux](https://github.com/avifenesh/computer-use-linux) — MCP сервер управления рабочим столом Linux для Hermes и других хостов MCP, с деревьями доступности AT-SPI, вводом Wayland/X11, скриншотами и таргетингом окон композитора.
- 🔌 [HermesClaw](https://github.com/AaronWong1999/hermesclaw) — Мост WeChat от сообщества: Запустите Hermes Agent и OpenClaw на одном аккаунте WeChat.

---

## Лицензия

MIT — см. [LICENSE](LICENSE).

Разработано [Nous Research](https://nousresearch.com).

---

## Архитектура Геркулеса

```text
Пользователь
  ↓
/start (start)
  ↓ Task(orchestrator)
Orchestrator
  ↓↓↓
Специалисты / субагенты
  ↓
Синтез → start → пользователь
```

**Архитектурные инварианты:**

1. **Цепочка:** `user → /start → Task(orchestrator) → Task(specialists)`
2. **Нет Task tool → `MULTI_AGENT_PIPELINE_BLOCKED`** (HARD FAIL, не silent fallback)
3. **L1 writer fan-out > 6** → реструктуризация через суб-оркестраторы
4. **Reader-ветки** без лимита, **writer-ветки:** 3+ → escalate

---

## Компоненты Геркулеса

| Директория | Назначение | Ключевые файлы |
|------------|------------|----------------|
| [`agents/`](agents/) | 33 определения агентов (4 координационных + 29 специалистов) | [`orchestrator.md`](agents/orchestrator.md), [`start.md`](agents/start.md), [`code.md`](agents/code.md) |
| [`rules/`](rules/) | 4 файла `.mdc`, применяемые всегда — глобальные ограничения | [`orchestrator.mdc`](rules/orchestrator.mdc), [`specialists.mdc`](rules/specialists.mdc) |
| [`skills/`](skills/) | 32 сценария рабочего процесса (`SKILL.md`) | [`orchestrator/SKILL.md`](skills/orchestrator/SKILL.md), [`start-workflow/SKILL.md`](skills/start-workflow/SKILL.md) |
| [`docs/`](docs/) | 37 markdown файлов документации | [`delegation-chain.md`](docs/delegation-chain.md), [`MAINTENANCE_RUNBOOK.md`](docs/MAINTENANCE_RUNBOOK.md) |
| [`scripts/`](scripts/) | 8 скриптов × 3 платформы (`.py`/`.sh`/`.ps1`) | [`run-full-repo-benchmark.py`](scripts/run-full-repo-benchmark.py), [`check-policy-encoding.py`](scripts/check-policy-encoding.py) |
| [`benchmarks/`](benchmarks/) | Контракты поведения + транскрипты-примеры (пройденные/не пройденные) | [`behavior-contracts.json`](benchmarks/behavior-contracts.json), [`transcript-cases.json`](benchmarks/transcript-cases.json) |
| [`profiles/`](profiles/) | Расширения, специфичные для проекта (изолированные от ядра) | [`msnmp/`](profiles/msnmp/) — конвейер пентеста |
| [`reports/`](reports/) | Отчеты аудита (архитектура, безопасность, документация, DevOps) | [`architecture-review-comprehensive.md`](reports/architecture-review-comprehensive.md) |
| [`.github/workflows/`](.github/workflows/) | CI валидация при push/PR | [`repo-validation.yml`](.github/workflows/repo-validation.yml) |

---

## Быстрая установка Геркулеса

### Linux, macOS, WSL2, Termux

```bash
curl -fsSL https://raw.githubusercontent.com/NousResearch/hermes-agent/main/scripts/install.sh | bash
```

### Windows (нативная, PowerShell) — Ранняя бета

> **Внимание:** Нативная поддержка Windows находится в **ранней бета-версии**. Она устанавливается и работает, но не была так широко протестирована, как наши пути для Linux/macOS/WSL2. Пожалуйста, [сообщайте об ошибках](https://github.com/NousResearch/hermes-agent/issues), когда столкнетесь с проблемами. Для наиболее проверенной настройки Windows сегодня запустите однострочник для Linux выше внутри **WSL2**.

Выполните это в PowerShell:

```powershell
iex (irm https://raw.githubusercontent.com/NousResearch/hermes-agent/main/scripts/install.ps1)
```

Установщик обрабатывает все: uv, Python 3.11, Node.js, ripgrep, ffmpeg, **и портативный Git Bash** (MinGit, распакованный в `%LOCALAPPDATA%\hermes\git` — не требует прав администратора, полностью изолирован от любой системной установки Git). Hermes использует этот встроенный Git Bash для выполнения команд оболочки.

Если у вас уже установлен Git, установщик обнаружит его и использует вместо этого. В противном случае загрузка MinGit размером ~45 МБ — это все, что вам нужно — он не будет касаться или мешать какому-либо системному Git.

> **Android / Termux:** Проверенный ручной путь документирован в [руководстве Termux](https://hermes-agent.nousresearch.com/docs/getting-started/termux). В Termux Hermes устанавливает кураторский экстра `.[termux]`, потому что полный экстра `.[all]` в настоящее время включает несовместимые с Android голосовые зависимости.
>
> **Windows:** Нативная поддержка Windows поддерживается как **ранняя бета** — однострочник PowerShell выше устанавливает все, но ожидайте шероховатостей и, пожалуйста, сообщайте об ошибках, когда столкнетесь с ними. Если вы предпочитаете использовать WSL2 (наш наиболее проверенный путь для Windows), команда для Linux также работает там. Нативная установка Windows находится в `%LOCALAPPDATA%\hermes`; установки WSL2 находятся в `~/.hermes`, как и в Linux. Единственная функция Hermes, которая в настоящее время требует именно WSL2, — это панель чата в браузере (она использует POSIX PTY — классический CLI и шлюз работают нативно).

После установки:

```bash
source ~/.bashrc    # перезагрузить оболочку (или: source ~/.zshrc)
hermes              # начать чат!
```

---

## Начало работы

```bash
hermes              # Интерактивный CLI — начать разговор
hermes model        # Выбрать ваш LLM-провайдер и модель
hermes tools        # Настроить, какие инструменты включены
hermes config set   # Установить отдельные значения конфигурации
hermes gateway      # Запустить шлюз обмена сообщениями (Telegram, Discord и т.д.)
hermes setup        # Запустить полный мастер настройки (конфигурирует все сразу)
hermes claw migrate # Мигрировать из OpenClaw (если вы переходите из OpenClaw)
hermes update       # Обновить до последней версии
hermes doctor       # Диагностировать любые проблемы
```

📖 **[Полная документация →](https://hermes-agent.nousresearch.com/docs/)**

## CLI vs Сообщения Краткое руководство

Hermes имеет две точки входа: запустите терминальный интерфейс с помощью `hermes`, или запустите шлюз и общайтесь с ним из Telegram, Discord, Slack, WhatsApp, Signal или Email. Как только вы окажетесь в разговоре, многие команды слеша будут общими для обоих интерфейсов.

| Действие | CLI | Платформы сообщений |
|---------|-----|---------------------|
| Начать чат | `hermes` | Запустите `hermes gateway setup` + `hermes gateway start`, затем отправьте боту сообщение |
| Начать новый разговор | `/new` или `/reset` | `/new` или `/reset` |
| Изменить модель | `/model [провайдер:модель]` | `/model [провайдер:модель]` |
| Установить личность | `/personality [имя]` | `/personality [имя]` |
| Повторить или отменить последний ход | `/retry`, `/undo` | `/retry`, `/undo` |
| Сжать контекст / проверить использование | `/compress`, `/usage`, `/insights [--дни N]` | `/compress`, `/usage`, `/insights [дни]` |
| Просмотреть навыки | `/skills` или `/<имя-навыка>` | `/<имя-навыка>` |
| Прервать текущую работу | `Ctrl+C` или отправить новое сообщение | `/stop` или отправить новое сообщение |
| Статус, специфичный для платформы | `/platforms` | `/status`, `/sethome` |

Полные списки команд см. в [руководстве CLI](https://hermes-agent.nousresearch.com/docs/user-guide/cli) и [руководстве шлюза сообщений](https://hermes-agent.nousresearch.com/docs/user-guide/messaging).

---

## Документация

Вся документация находится по адресу **[hermes-agent.nousresearch.com/docs](https://hermes-agent.nousresearch.com/docs/)**:

| Раздел | Что охватывается |
|---------|---------------|
| [Быстрый старт](https://hermes-agent.nousresearch.com/docs/getting-started/quickstart) | Установка → настройка → первый разговор за 2 минуты |
| [Использование CLI](https://hermes-agent.nousresearch.com/docs/user-guide/cli) | Команды, привязки клавиш, личности, сессии |
| [Конфигурация](https://hermes-agent.nousresearch.com/docs/user-guide/configuration) | Файл конфигурации, провайдеры, модели, все опции |
| [Шлюз сообщений](https://hermes-agent.nousresearch.com/docs/user-guide/messaging) | Telegram, Discord, Slack, WhatsApp, Signal, Home Assistant |
| [Безопасность](https://hermes-agent.nousresearch.com/docs/user-guide/security) | Одобрение команд, сопряжение DM, изоляция контейнеров |
| [Инструменты и наборы инструментов](https://hermes-agent.nousresearch.com/docs/user-guide/features/tools) | 40+ инструментов, система наборов инструментов, бэкенды терминалов |
| [Система навыков](https://hermes-agent.nousresearch.com/docs/user-guide/features/skills) | Процедурная память, Skills Hub, создание навыков |
| [Память](https://hermes-agent.nousresearch.com/docs/user-guide/features/memory) | Постоянная память, профили пользователей, лучшие практики |
| [Интеграция MCP](https://hermes-agent.nousresearch.com/docs/user-guide/features/mcp) | Подключение любого сервера MCP для расширенных возможностей |
| [Планирование Cron](https://hermes-agent.nousresearch.com/docs/user-guide/features/cron) | Запланированные задачи с доставкой на платформу |
| [Файлы контекста](https://hermes-agent.nousresearch.com/docs/user-guide/features/context-files) | Контекст проекта, который формирует каждый разговор |
| [Архитектура](https://hermes-agent.nousresearch.com/docs/developer-guide/architecture) | Структура проекта, цикл агента, ключевые классы |
| [Участие](https://hermes-agent.nousresearch.com/docs/developer-guide/contributing) | Настройка разработки, стиль кода, процесс PR |
| [Справочник CLI](https://hermes-agent.nousresearch.com/docs/reference/cli-commands) | Все команды и флаги |
| [Переменные окружения](https://hermes-agent.nousresearch.com/docs/reference/environment-variables) | Полный справочник переменных окружения |

---

## Миграция из OpenClaw

Если вы переходите из OpenClaw, Hermes может автоматически импортировать ваши настройки, память, навыки и ключи API.

**Во время первой настройки:** Мастер настройки (`hermes setup`) автоматически обнаруживает `~/.openclaw` и предлагает выполнить миграцию перед началом настройки.

**В любое время после установки:**

```bash
hermes claw migrate              # Интерактивная миграция (полный пресет)
hermes claw migrate --dry-run    # Предварительный просмотр того, что будет мигрировано
hermes claw migrate --preset user-data   # Миграция без секретов
hermes claw migrate --overwrite  # Перезапись существующих конфликтов
```

Что импортируется:
- **SOUL.md** — файл персоны
- **Память** — записи MEMORY.md и USER.md
- **Навыки** — пользовательские навыки → `~/.hermes/skills/openclaw-imports/`
- **Список разрешенных команд** — шаблоны одобрения
- **Настройки сообщений** — конфигурации платформ, разрешенные пользователи, рабочая директория
- **Ключи API** — разрешенные секреты (Telegram, OpenRouter, OpenAI, Anthropic, ElevenLabs)
- **TTS ресурсы** — рабочие файлы аудио
- **Инструкции для рабочей среды** — AGENTS.md (с `--workspace-target`)

См. `hermes claw migrate --help` для всех опций или используйте навык `openclaw-migration` для интерактивной миграции под руководством агента с предварительным просмотром.

---

## Участие

Мы приветствуем ваш вклад! См. [Руководство по участию](https://hermes-agent.nousresearch.com/docs/developer-guide/contributing) для настройки разработки, стиля кода и процесса PR.

Краткое руководство для участников — клонируйте и запускайте с помощью `setup-hermes.sh`:

```bash
git clone https://github.com/NousResearch/hermes-agent.git
cd hermes-agent
./setup-hermes.sh     # устанавливает uv, создает venv, устанавливает .[all], создает символическую ссылку ~/.local/bin/hermes
./hermes              # автоматически определяет venv, не нужно `source` заранее
```

Ручной путь (эквивалент вышеизложенного):

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
uv venv .venv --python 3.11
source .venv/bin/activate
uv pip install -e ".[all,dev]"
scripts/run_tests.sh
```

---

## Сообщество

- 💬 [Discord](https://discord.gg/NousResearch)
- 📚 [Skills Hub](https://agentskills.io)
- 🐛 [Issues](https://github.com/NousResearch/hermes-agent/issues)
- 🔌 [computer-use-linux](https://github.com/avifenesh/computer-use-linux) — MCP сервер управления рабочим столом Linux для Hermes и других хостов MCP, с деревьями доступности AT-SPI, вводом Wayland/X11, скриншотами и таргетингом окон композитора.
- 🔌 [HermesClaw](https://github.com/AaronWong1999/hermesclaw) — Мост WeChat от сообщества: Запустите Hermes Agent и OpenClaw на одном аккаунте WeChat.

---

## Лицензия

MIT — см. [LICENSE](LICENSE).

Разработано [Nous Research](https://nousresearch.com).

---

## Архитектура Геркулеса

```text
Пользователь
  ↓
/start (start)
  ↓ Task(orchestrator)
Orchestrator
  ↓↓↓
Специалисты / субагенты
  ↓
Синтез → start → пользователь
```

**Архитектурные инварианты:**

1. **Цепочка:** `user → /start → Task(orchestrator) → Task(specialists)`
2. **Нет Task tool → `MULTI_AGENT_PIPELINE_BLOCKED`** (HARD FAIL, не silent fallback)
3. **L1 writer fan-out > 6** → реструктуризация через суб-оркестраторы
4. **Reader-ветки** без лимита, **writer-ветки:** 3+ → escalate

---

## Компоненты Геркулеса

| Директория | Назначение | Ключевые файлы |
|------------|------------|----------------|
| [`agents/`](agents/) | 33 определения агентов (4 координационных + 29 специалистов) | [`orchestrator.md`](agents/orchestrator.md), [`start.md`](agents/start.md), [`code.md`](agents/code.md) |
| [`rules/`](rules/) | 4 файла `.mdc`, применяемые всегда — глобальные ограничения | [`orchestrator.mdc`](rules/orchestrator.mdc), [`specialists.mdc`](rules/specialists.mdc) |
| [`skills/`](skills/) | 32 сценария рабочего процесса (`SKILL.md`) | [`orchestrator/SKILL.md`](skills/orchestrator/SKILL.md), [`start-workflow/SKILL.md`](skills/start-workflow/SKILL.md) |
| [`docs/`](docs/) | 37 markdown файлов документации | [`delegation-chain.md`](docs/delegation-chain.md), [`MAINTENANCE_RUNBOOK.md`](docs/MAINTENANCE_RUNBOOK.md) |
| [`scripts/`](scripts/) | 8 скриптов × 3 платформы (`.py`/`.sh`/`.ps1`) | [`run-full-repo-benchmark.py`](scripts/run-full-repo-benchmark.py), [`check-policy-encoding.py`](scripts/check-policy-encoding.py) |
| [`benchmarks/`](benchmarks/) | Контракты поведения + транскрипты-примеры (пройденные/не пройденные) | [`behavior-contracts.json`](benchmarks/behavior-contracts.json), [`transcript-cases.json`](benchmarks/transcript-cases.json) |
| [`profiles/`](profiles/) | Расширения, специфичные для проекта (изолированные от ядра) | [`msnmp/`](profiles/msnmp/) — конвейер пентеста |
| [`reports/`](reports/) | Отчеты аудита (архитектура, безопасность, документация, DevOps) | [`architecture-review-comprehensive.md`](reports/architecture-review-comprehensive.md) |
| [`.github/workflows/`](.github/workflows/) | CI валидация при push/PR | [`repo-validation.yml`](.github/workflows/repo-validation.yml) |

---

## Быстрая установка Геркулеса

### Linux, macOS, WSL2, Termux

```bash
curl -fsSL https://raw.githubusercontent.com/NousResearch/hermes-agent/main/scripts/install.sh | bash
```

### Windows (нативная, PowerShell) — Ранняя бета

> **Внимание:** Нативная поддержка Windows находится в **ранней бета-версии**. Она устанавливается и работает, но не была так широко протестирована, как наши пути для Linux/macOS/WSL2. Пожалуйста, [сообщайте об ошибках](https://github.com/NousResearch/hermes-agent/issues), когда столкнетесь с проблемами. Для наиболее проверенной настройки Windows сегодня запустите однострочник для Linux выше внутри **WSL2**.

Выполните это в PowerShell:

```powershell
iex (irm https://raw.githubusercontent.com/NousResearch/hermes-agent/main/scripts/install.ps1)
```

Установщик обрабатывает все: uv, Python 3.11, Node.js, ripgrep, ffmpeg, **и портативный Git Bash** (MinGit, распакованный в `%LOCALAPPDATA%\hermes\git` — не требует прав администратора, полностью изолирован от любой системной установки Git). Hermes использует этот встроенный Git Bash для выполнения команд оболочки.

Если у вас уже установлен Git, установщик обнаружит его и использует вместо этого. В противном случае загрузка MinGit размером ~45 МБ — это все, что вам нужно — он не будет касаться или мешать какому-либо системному Git.

> **Android / Termux:** Проверенный ручной путь документирован в [руководстве Termux](https://hermes-agent.nousresearch.com/docs/getting-started/termux). В Termux Hermes устанавливает кураторский экстра `.[termux]`, потому что полный экстра `.[all]` в настоящее время включает несовместимые с Android голосовые зависимости.
>
> **Windows:** Нативная поддержка Windows поддерживается как **ранняя бета** — однострочник PowerShell выше устанавливает все, но ожидайте шероховатостей и, пожалуйста, сообщайте об ошибках, когда столкнетесь с ними. Если вы предпочитаете использовать WSL2 (наш наиболее проверенный путь для Windows), команда для Linux также работает там. Нативная установка Windows находится в `%LOCALAPPDATA%\hermes`; установки WSL2 находятся в `~/.hermes`, как и в Linux. Единственная функция Hermes, которая в настоящее время требует именно WSL2, — это панель чата в браузере (она использует POSIX PTY — классический CLI и шлюз работают нативно).

После установки:

```bash
source ~/.bashrc    # перезагрузить оболочку (или: source ~/.zshrc)
hermes              # начать чат!
```

---

## Начало работы

```bash
hermes              # Интерактивный CLI — начать разговор
hermes model        # Выбрать ваш LLM-провайдер и модель
hermes tools        # Настроить, какие инструменты включены
hermes config set   # Установить отдельные значения конфигурации
hermes gateway      # Запустить шлюз обмена сообщениями (Telegram, Discord и т.д.)
hermes setup        # Запустить полный мастер настройки (конфигурирует все сразу)
hermes claw migrate # Мигрировать из OpenClaw (если вы переходите из OpenClaw)
hermes update       # Обновить до последней версии
hermes doctor       # Диагностировать любые проблемы
```

📖 **[Полная документация →](https://hermes-agent.nousresearch.com/docs/)**

## CLI vs Сообщения Краткое руководство

Hermes имеет две точки входа: запустите терминальный интерфейс с помощью `hermes`, или запустите шлюз и общайтесь с ним из Telegram, Discord, Slack, WhatsApp, Signal или Email. Как только вы окажетесь в разговоре, многие команды слеша будут общими для обоих интерфейсов.

| Действие | CLI | Платформы сообщений |
|---------|-----|---------------------|
| Начать чат | `hermes` | Запустите `hermes gateway setup` + `hermes gateway start`, затем отправьте боту сообщение |
| Начать новый разговор | `/new` или `/reset` | `/new` или `/reset` |
| Изменить модель | `/model [провайдер:модель]` | `/model [провайдер:модель]` |
| Установить личность | `/personality [имя]` | `/personality [имя]` |
| Повторить или отменить последний ход | `/retry`, `/undo` | `/retry`, `/undo` |
| Сжать контекст / проверить использование | `/compress`, `/usage`, `/insights [--дни N]` | `/compress`, `/usage`, `/insights [дни]` |
| Просмотреть навыки | `/skills` или `/<имя-навыка>` | `/<имя-навыка>` |
| Прервать текущую работу | `Ctrl+C` или отправить новое сообщение | `/stop` или отправить новое сообщение |
| Статус, специфичный для платформы | `/platforms` | `/status`, `/sethome` |

Полные списки команд см. в [руководстве CLI](https://hermes-agent.nousresearch.com/docs/user-guide/cli) и [руководстве шлюза сообщений](https://hermes-agent.nousresearch.com/docs/user-guide/messaging).

---

## Документация

Вся документация находится по адресу **[hermes-agent.nousresearch.com/docs](https://hermes-agent.nousresearch.com/docs/)**:

| Раздел | Что охватывается |
|---------|---------------|
| [Быстрый старт](https://hermes-agent.nousresearch.com/docs/getting-started/quickstart) | Установка → настройка → первый разговор за 2 минуты |
| [Использование CLI](https://hermes-agent.nousresearch.com/docs/user-guide/cli) | Команды, привязки клавиш, личности, сессии |
| [Конфигурация](https://hermes-agent.nousresearch.com/docs/user-guide/configuration) | Файл конфигурации, провайдеры, модели, все опции |
| [Шлюз сообщений](https://hermes-agent.nousresearch.com/docs/user-guide/messaging) | Telegram, Discord, Slack, WhatsApp, Signal, Home Assistant |
| [Безопасность](https://hermes-agent.nousresearch.com/docs/user-guide/security) | Одобрение команд, сопряжение DM, изоляция контейнеров |
| [Инструменты и наборы инструментов](https://hermes-agent.nousresearch.com/docs/user-guide/features/tools) | 40+ инструментов, система наборов инструментов, бэкенды терминалов |
| [Система навыков](https://hermes-agent.nousresearch.com/docs/user-guide/features/skills) | Процедурная память, Skills Hub, создание навыков |
| [Память](https://hermes-agent.nousresearch.com/docs/user-guide/features/memory) | Постоянная память, профили пользователей, лучшие практики |
| [Интеграция MCP](https://hermes-agent.nousresearch.com/docs/user-guide/features/mcp) | Подключение любого сервера MCP для расширенных возможностей |
| [Планирование Cron](https://hermes-agent.nousresearch.com/docs/user-guide/features/cron) | Запланированные задачи с доставкой на платформу |
| [Файлы контекста](https://hermes-agent.nousresearch.com/docs/user-guide/features/context-files) | Контекст проекта, который формирует каждый разговор |
| [Архитектура](https://hermes-agent.nousresearch.com/docs/developer-guide/architecture) | Структура проекта, цикл агента, ключевые классы |
| [Участие](https://hermes-agent.nousresearch.com/docs/developer-guide/contributing) | Настройка разработки, стиль кода, процесс PR |
| [Справочник CLI](https://hermes-agent.nousresearch.com/docs/reference/cli-commands) | Все команды и флаги |
| [Переменные окружения](https://hermes-agent.nousresearch.com/docs/reference/environment-variables) | Полный справочник переменных окружения |

---

## Миграция из OpenClaw

Если вы переходите из OpenClaw, Hermes может автоматически импортировать ваши настройки, память, навыки и ключи API.

**Во время первой настройки:** Мастер настройки (`hermes setup`) автоматически обнаруживает `~/.openclaw` и предлагает выполнить миграцию перед началом настройки.

**В любое время после установки:**

```bash
hermes claw migrate              # Интерактивная миграция (полный пресет)
hermes claw migrate --dry-run    # Предварительный просмотр того, что будет мигрировано
hermes claw migrate --preset user-data   # Миграция без секретов
hermes claw migrate --overwrite  # Перезапись существующих конфликтов
```

Что импортируется:
- **SOUL.md** — файл персоны
- **Память** — записи MEMORY.md и USER.md
- **Навыки** — пользовательские навыки → `~/.hermes/skills/openclaw-imports/`
- **Список разрешенных команд** — шаблоны одобрения
- **Настройки сообщений** — конфигурации платформ, разрешенные пользователи, рабочая директория
- **Ключи API** — разрешенные секреты (Telegram, OpenRouter, OpenAI, Anthropic, ElevenLabs)
- **TTS ресурсы** — рабочие файлы аудио
- **Инструкции для рабочей среды** — AGENTS.md (с `--workspace-target`)

См. `hermes claw migrate --help` для всех опций или используйте навык `openclaw-migration` для интерактивной миграции под руководством агента с предварительным просмотром.

---

## Участие

Мы приветствуем ваш вклад! См. [Руководство по участию](https://hermes-agent.nousresearch.com/docs/developer-guide/contributing) для настройки разработки, стиля кода и процесса PR.

Краткое руководство для участников — клонируйте и запускайте с помощью `setup-hermes.sh`:

```bash
git clone https://github.com/NousResearch/hermes-agent.git
cd hermes-agent
./setup-hermes.sh     # устанавливает uv, создает venv, устанавливает .[all], создает символическую ссылку ~/.local/bin/hermes
./hermes              # автоматически определяет venv, не нужно `source` заранее
```

Ручной путь (эквивалент вышеизложенного):

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
uv venv .venv --python 3.11
source .venv/bin/activate
uv pip install -e ".[all,dev]"
scripts/run_tests.sh
```

---

## Сообщество

- 💬 [Discord](https://discord.gg/NousResearch)
- 📚 [Skills Hub](https://agentskills.io)
- 🐛 [Issues](https://github.com/NousResearch/hermes-agent/issues)
- 🔌 [computer-use-linux](https://github.com/avifenesh/computer-use-linux) — MCP сервер управления рабочим столом Linux для Hermes и других хостов MCP, с деревьями доступности AT-SPI, вводом Wayland/X11, скриншотами и таргетингом окон композитора.
- 🔌 [HermesClaw](https://github.com/AaronWong1999/hermesclaw) — Мост WeChat от сообщества: Запустите Hermes Agent и OpenClaw на одном аккаунте WeChat.

---

## Лицензия

MIT — см. [LICENSE](LICENSE).

Разработано [Nous Research](https://nousresearch.com).

---

## Архитектура Геркулеса

```text
Пользователь
  ↓
/start (start)
  ↓ Task(orchestrator)
Orchestrator
  ↓↓↓
Специалисты / субагенты
  ↓
Синтез → start → пользователь
```

**Архитектурные инварианты:**

1. **Цепочка:** `user → /start → Task(orchestrator) → Task(specialists)`
2. **Нет Task tool → `MULTI_AGENT_PIPELINE_BLOCKED`** (HARD FAIL, не silent fallback)
3. **L1 writer fan-out > 6** → реструктуризация через суб-оркестраторы
4. **Reader-ветки** без лимита, **writer-ветки:** 3+ → escalate

---

## Компоненты Геркулеса

| Директория | Назначение | Ключевые файлы |
|------------|------------|----------------|
| [`agents/`](agents/) | 33 определения агентов (4 координационных + 29 специалистов) | [`orchestrator.md`](agents/orchestrator.md), [`start.md`](agents/start.md), [`code.md`](agents/code.md) |
| [`rules/`](rules/) | 4 файла `.mdc`, применяемые всегда — глобальные ограничения | [`orchestrator.mdc`](rules/orchestrator.mdc), [`specialists.mdc`](rules/specialists.mdc) |
| [`skills/`](skills/) | 32 сценария рабочего процесса (`SKILL.md`) | [`orchestrator/SKILL.md`](skills/orchestrator/SKILL.md), [`start-workflow/SKILL.md`](skills/start-workflow/SKILL.md) |
| [`docs/`](docs/) | 37 markdown файлов документации | [`delegation-chain.md`](docs/delegation-chain.md), [`MAINTENANCE_RUNBOOK.md`](docs/MAINTENANCE_RUNBOOK.md)
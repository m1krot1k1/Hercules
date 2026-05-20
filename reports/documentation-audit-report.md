# Documentation Audit Report

**Дата:** 2026-04-04
**Аудитор:** Docs Agent
**Репозиторий:** `c:/Users/ndppd/Desktop/.cursor`

---

## Executive Summary

Репозиторий содержит **высококачественную документацию** с хорошим покрытием основных компонентов. Найдено **34 agent definitions** (фактически), **35 skill directories** (фактически), **37 markdown файлов** в `docs/`. Основные проблемы: расхождения в счётчиках, устаревшие ссылки, отсутствие API-документации для tg_bot, и неполное покрытие skills в реестрах.

---

## 1. Корневой README.md

### 1.1. Счётчик агентов не соответствует действительности

**Файл:** [`README.md`](README.md:5)
**Категория:** Актуальность
**Критичность:** 🔴 Высокая

**Описание:** Строка 5 утверждает `**34 agent definitions** (без `agents/README.md`): 4 coordination + 30 domain specialists`. Фактический подсчёт файлов в `agents/` (исключая `README.md` и подкаталог `agent-manager/`) даёт **34 файла**, но не все из них — domain specialists. Координационные агенты: `start`, `orchestrator`, `meta-agent-architect`, `subagent-factory` = 4. Остальные 30 — это domain specialists + registry-агенты (`benchmark-specialist`, `rules-specialist`, `skills-specialist`, `profile-manager`, `agent-manager`, `tgbot-specialist`). Формула верна, но классификация размыта.

**Рекомендация:** Уточнить классификацию. Registry-агенты (`benchmark-specialist`, `rules-specialist`, `skills-specialist`, `profile-manager`, `agent-manager`, `tgbot-specialist`) — это не domain specialists в классическом смысле. Рассмотреть категорию "platform/registry agents".

---

### 1.2. Отсутствует ссылка на tg_bot в структуре репозитория

**Файл:** [`README.md`](README.md:43-54)
**Категория:** Полнота покрытия
**Критичность:** 🟡 Средняя

**Описание:** В секции "Реальная структура репозитория" перечислены `agents/`, `rules/`, `skills/`, `docs/`, `profiles/`, `benchmarks/`, `agent-tasks/`, `scripts/`, `.github/workflows/`, `.plan/`. **Отсутствует `tg_bot/`** — значимый компонент с собственной документацией.

**Рекомендация:** Добавить строку:
```
tg_bot/          # Telegram control plane для 24/7 оркестрации
```

---

### 1.3. Нет ссылки на reports/ директорию

**Файл:** [`README.md`](README.md:43-54)
**Категория:** Полнота покрытия
**Критичность:** 🟢 Низкая

**Описание:** Директория `reports/` содержит отчёты аудита (`architecture-review-comprehensive.md`, `security-audit-wave1.md`, `review-wave1.md`), но не упомянута в структуре.

**Рекомендация:** Добавить `reports/` в список с описанием "Отчёты аудита и ревью".

---

### 1.4. Отсутствует Troubleshooting секция

**Файл:** [`README.md`](README.md:1-182)
**Категория:** Troubleshooting / Runbooks
**Критичность:** 🟡 Средняя

**Описание:** В корневом README нет секции troubleshooting. Пользователь, столкнувшийся с проблемой (например, "Task недоступен", "зеркало рассинхронизировалось"), не найдёт быстрого решения.

**Рекомендация:** Добавить секцию перед "Smoke Test":
```markdown
## Troubleshooting

| Проблема | Решение |
|----------|---------|
| `Task` инструмент недоступен | См. `docs/delegation-chain.md` — это HARD FAIL, не fallback |
| Зеркало `.cursor/` рассинхронизировано | Запустить `rsync` команды из README или `CHECK_CURSOR_MIRROR=1 python3 scripts/validate-repo-consistency.py` |
| Валидатор падает после добавления агента | Проверить frontmatter, обновить `agents/README.md` и `rules/specialists.mdc` |
| Бот не отвечает | Проверить `tg_bot/.env`, запустить `python3 tg_bot/main.py` |
```

---

### 1.5. Нет информации о версиях / changelog

**Файл:** [`README.md`](README.md:1-182)
**Категория:** Полнота покрытия
**Критичность:** 🟡 Средняя

**Описание:** Отсутствует информация о текущей версии системы, changelog, или истории изменений. Непонятно, какая версия конфигурации развёрнута.

**Рекомендация:** Добавить секцию "Version" в начало или создать `CHANGELOG.md`.

---

## 2. docs/ директория (37 файлов)

### 2.1. docs/README.md — отличная структура, но нет ссылок на новые документы

**Файл:** [`docs/README.md`](docs/README.md:1-49)
**Категория:** Актуальность
**Критичность:** 🟡 Средняя

**Описание:** Таблица содержит 36 строк, но в директории `docs/` фактически **37 markdown файлов**. Не включены в таблицу:
- `docs/delivery/backlog.md`
- `docs/delivery/PBI-002/prd.md`
- `docs/delivery/PBI-006/prd.md`
- `docs/state-map-wave1.md`
- `docs/gap-analysis-wave1.md`
- `docs/improvement-plan-wave1.md`

**Рекомендация:** Добавить недостающие документы в таблицу `docs/README.md` или создать отдельную секцию "Delivery & Planning".

---

### 2.2. docs/skills-index.md — не все skills упомянуты

**Файл:** [`docs/skills-index.md`](docs/skills-index.md:1-45)
**Категория:** Актуальность
**Критичность:** 🔴 Высокая

**Описание:** В таблице `skills-index.md` перечислены **35 skills** (включая "New" секцию). Фактически в `skills/` **35 директорий** с `SKILL.md`. Однако в таблице `skills/README.md` перечислены только **18 skills** (11 основных + 7 "New"). Отсутствуют:
- `agent-council-judge`
- `agent-evals`
- `behavior-benchmarks-transcript`
- `budget-orchestration`
- `caid-ownership-matrix`
- `human-in-the-loop-gates`
- `mcp-governance`
- `progressive-mcp-discovery`
- `session-memory-tiers`
- `structured-agent-logging`
- `structured-policy-yaml`
- `tool-output-sanitization`
- `web-research-fact-pack`

**Рекомендация:** Синхронизировать `skills/README.md` с `docs/skills-index.md`. Либо расширить таблицу, либо добавить ссылку на `docs/skills-index.md` как на master list.

---

### 2.3. docs/GLOSSARY.md — хороший глоссарий

**Файл:** [`docs/GLOSSARY.md`](docs/GLOSSARY.md:1-72)
**Категория:** Полнота покрытия
**Критичность:** ✅ OK

**Описание:** Глоссарий покрывает ключевые термины: agent, DUA, envelope, ENTRY_MODE, B-tree, Task, fan-out, RELAY_MODE и др. Хорошо структурирован по категориям.

**Рекомендация:** Добавить термины, которые встречаются в коде, но отсутствуют в глоссарии:
- `CAID` (упоминается в `caid-ownership-matrix`, `caid-worktrees`)
- `HITL` (human-in-the-loop)
- `MCP` (Model Context Protocol)
- `AC` (Acceptance Criteria)

---

### 2.4. docs/MAINTENANCE_RUNBOOK.md — хороший runbook

**Файл:** [`docs/MAINTENANCE_RUNBOOK.md`](docs/MAINTENANCE_RUNBOOK.md:1-144)
**Категория:** Runbooks
**Критичность:** ✅ OK

**Описание:** Пошаговые инструкции для добавления/переименования/удаления агента, создания skill, обновления правил. Хорошо структурирован.

**Рекомендация:** Добавить секции:
- "Добавление нового скрипта в `scripts/`" (с учётом allowlist в `.gitignore`)
- "Обновление benchmark fixtures"
- "Создание нового профиля"

---

### 2.5. Отсутствует API документация для tg_bot

**Файл:** `docs/` (нет файла)
**Категория:** API документация
**Критичность:** 🔴 Высокая

**Описание:** `tg_bot/` — полноценный компонент с CLI (`ctl.py`), long-polling (`main.py`), bootstrap (`bootstrap.py`). Нет документации по:
- Доступным командам CLI с параметрами
- Формату событий в `runtime/`
- Формату approval-событий
- Структуре `runtime/events/pending/` и `runtime/approvals/resolved/`

**Рекомендация:** Создать `docs/tg-bot-api.md` или расширить `tg_bot/README.md` секцией "API Reference".

---

### 2.6. Delivery документы без контекста

**Файлы:** `docs/delivery/backlog.md`, `docs/delivery/PBI-002/prd.md`, `docs/delivery/PBI-006/prd.md`
**Категория:** Структура и навигация
**Критичность:** 🟡 Средняя

**Описание:** Директория `docs/delivery/` содержит backlog и PRD для PBI-002 и PBI-006, но нет:
- Индекса delivery документов
- Описания конвенции PBI
- Связи с `docs/pbi-task-workflow.md`

**Рекомендация:** Создать `docs/delivery/README.md` с индексом и описанием workflow.

---

## 3. agents/README.md

### 3.1. Таблица агентов не полностью синхронизирована с файловой системой

**Файл:** [`agents/README.md`](agents/README.md:63-122)
**Категория:** Актуальность
**Критичность:** 🟡 Средняя

**Описание:** В таблице перечислены агенты, но некоторые агенты из файловой системы отсутствуют в таблицах:
- `agent-architect.md` — упомянут в строке 70, но в секции "Planning & Architecture"
- `provider-integrator.md` — упомянут в строке 80 ✅
- `rules-specialist.md` — упомянут в строке 117 ✅
- `skills-specialist.md` — упомянут в строке 118 ✅
- `profile-manager.md` — упомянут в строке 119 ✅
- `tgbot-specialist.md` — упомянут в строке 120 ✅

Все агенты из файловой системы присутствуют в таблицах. ✅

---

### 3.2. Счётчик "33 агентов" в specialist-discovery skill

**Файл:** [`agents/README.md`](agents/README.md:2)
**Категория:** Актуальность
**Критичность:** 🟡 Средняя

**Описание:** Строка 2: `*34 agent definitions (4 coordination + 30 domain specialists in core)*`. Однако в `skills/specialist-discovery/SKILL.md` (судя по `skills/README.md` строка 17) упоминается "33 агента". Расхождение в 1 агент.

**Рекомендация:** Унифицировать счётчики во всех документах. Запустить `scripts/validate-agent-registry.sh` для получения точного числа.

---

### 3.3. Отсутствует документация для подкаталога agent-manager/

**Файл:** `agents/agent-manager/` (нет README)
**Категория:** Полнота покрытия
**Критичность:** 🟢 Низкая

**Описание:** В `agents/` есть подкаталог `agent-manager/`, который не описан в документации.

**Рекомендация:** Добавить `agents/agent-manager/README.md` или описать содержимое в основной документации.

---

## 4. skills/README.md

### 4.1. Неполный реестр skills

**Файл:** [`skills/README.md`](skills/README.md:1-62)
**Категория:** Полнота покрытия
**Критичность:** 🔴 Высокая

**Описание:** В таблице перечислены только **18 skills** из **35 фактических**. Отсутствуют 17 skills:
- `agent-council-judge`
- `agent-evals`
- `agent-manager`
- `behavior-benchmarks-transcript`
- `budget-orchestration`
- `caid-ownership-matrix`
- `human-in-the-loop-gates`
- `mcp-governance`
- `progressive-mcp-discovery`
- `session-memory-tiers`
- `structured-agent-logging`
- `structured-policy-yaml`
- `tool-output-sanitization`
- `web-research-fact-pack`

**Рекомендация:** Расширить таблицу или добавить ссылку на `docs/skills-index.md` как на полный master list.

---

### 4.2. Шаблон SKILL.md неполный

**Файл:** [`skills/README.md`](skills/README.md:52-59)
**Категория:** Полнота покрытия
**Критичность:** 🟡 Средняя

**Описание:** Шаблон показывает только YAML frontmatter и разделы `## Purpose`, `## Когда использовать`, `## Шаги`, `## Policy Reference`. Реальные SKILL.md файлы содержат дополнительные секции: `## Examples`, `## Anti-patterns`, `## Related`, response footers.

**Рекомендация:** Расширить шаблон до полного набора рекомендуемых секций.

---

## 5. scripts/README.md

### 5.1. Хорошая документация скриптов

**Файл:** [`scripts/README.md`](scripts/README.md:1-67)
**Категория:** Полнота покрытия
**Критичность:** ✅ OK

**Описание:** Реестр скриптов с описанием, примеры запуска для трёх платформ, коды выхода, требования. Хорошо структурирован.

**Рекомендация:** Добавить секцию "Output format" — что выводит каждый скрипт при успехе/ошибке.

---

### 5.2. Отсутствует документация для check-policy-encoding.py

**Файл:** [`scripts/README.md`](scripts/README.md:16)
**Категория:** Полнота покрытия
**Критичность:** 🟢 Низкая

**Описание:** `check-policy-encoding.py` упомянут в таблице, но для него нет `.sh` и `.ps1` обёрток (в отличие от остальных скриптов). Это не отражено в документации.

**Рекомендация:** Указать, что `check-policy-encoding` доступен только как `.py`.

---

## 6. tg_bot/README.md

### 6.1. Хороший quick start, но нет API reference

**Файл:** [`tg_bot/README.md`](tg_bot/README.md:1-86)
**Категория:** API документация
**Критичность:** 🟡 Средняя

**Описание:** README описывает что умеет бот, структуру, быстрый старт, CLI команды, troubleshooting. Но нет:
- Полного списка команд Telegram бота с параметрами
- Формата файлов в `runtime/`
- Схемы событий (event schema)
- Инструкции по интеграции с оркестратором

**Рекомендация:** Добавить секции "Command Reference" и "Event Schema".

---

### 6.2. Отсутствует описание переменных окружения

**Файл:** [`tg_bot/README.md`](tg_bot/README.md:1-86)
**Категория:** Полнота покрытия
**Критичность:** 🟡 Средняя

**Описание:** Упомянуты `TELEGRAM_BOT_TOKEN` и `TELEGRAM_ADMIN_CHAT_ID`, но нет полной таблицы всех переменных `.env` с описанием, обязательностью, значениями по умолчанию.

**Рекомендация:** Добавить таблицу конфигурации:
```markdown
| Переменная | Обязательна | По умолчанию | Описание |
|------------|-------------|--------------|----------|
| TELEGRAM_BOT_TOKEN | Да | — | Token от @BotFather |
| TELEGRAM_ADMIN_CHAT_ID | Да | — | ID чата для команд |
```

---

## 7. benchmarks/README.md

### 7.1. Хорошее описание behavior contracts

**Файл:** [`benchmarks/README.md`](benchmarks/README.md:1-55)
**Категория:** Полнота покрытия
**Критичность:** ✅ OK

**Описание:** Таблица из 21 behavior contract с ID и описанием. Понятная структура, примеры запуска.

**Рекомендация:** Добавить описание формата `behavior-contracts.json` — какие поля используются, как добавлять новый контракт.

---

### 7.2. Нет описания формата transcript fixtures

**Файл:** [`benchmarks/README.md`](benchmarks/README.md:1-55)
**Категория:** API документация
**Критичность:** 🟡 Средняя

**Описание:** Упомянуты `transcript-fixtures/pass/` и `transcript-fixtures/fail/`, но нет описания формата JSON файлов — какие поля ожидаются, как создавать новые fixtures.

**Рекомендация:** Добавить секцию "Transcript Fixture Format" с примером JSON структуры.

---

## 8. profiles/README.md

### 8.1. Минимальная документация

**Файл:** [`profiles/README.md`](profiles/README.md:1-21)
**Категория:** Полнота покрытия
**Критичность:** 🟡 Средняя

**Описание:** Документ описывает назначение профилей и типовую структуру, но не содержит:
- Примеров реальных профилей (кроме `msnmp`)
- Инструкции по созданию нового профиля
- Best practices для isolation
- Связи с `profile-manager` агентом

**Рекомендация:** Расширить документ, добавить пример создания профиля с нуля.

---

## 9. Перекрёстные ссылки

### 9.1. Хорошая связность основных документов

**Категория:** Перекрёстные ссылки
**Критичность:** ✅ OK

**Описание:** Основные документы (`README.md`, `docs/README.md`, `agents/README.md`, `skills/README.md`, `docs/GLOSSARY.md`, `docs/MAINTENANCE_RUNBOOK.md`) содержат перекрёстные ссылки друг на друга.

---

### 9.2. Отсутствуют обратные ссылки из docs/ в корневой README

**Категория:** Перекрёстные ссылки
**Критичность:** 🟢 Низкая

**Описание:** Некоторые документы в `docs/` не ссылаются обратно на корневой README или `docs/README.md` для навигации.

**Рекомендация:** Добавить footer в каждый документ `docs/`:
```markdown
---
**Навигация:** [Главная](../README.md) | [Оглавление docs](./README.md) | [Глоссарий](./GLOSSARY.md)
```

---

## 10. Сводная таблица проблем

| # | Файл | Строка | Категория | Критичность | Описание |
|---|------|--------|-----------|-------------|----------|
| 1 | `README.md` | 5 | Актуальность | 🔴 Высокая | Классификация агентов размыта (registry agents vs domain specialists) |
| 2 | `README.md` | 43-54 | Полнота | 🟡 Средняя | Отсутствует `tg_bot/` в структуре репозитория |
| 3 | `README.md` | 43-54 | Полнота | 🟢 Низкая | Отсутствует `reports/` в структуре |
| 4 | `README.md` | 1-182 | Troubleshooting | 🟡 Средняя | Нет секции troubleshooting |
| 5 | `README.md` | 1-182 | Полнота | 🟡 Средняя | Нет версии/changelog |
| 6 | `docs/README.md` | 5-36 | Актуальность | 🟡 Средняя | Не все 37 файлов включены в таблицу |
| 7 | `docs/skills-index.md` | 1-45 | Актуальность | 🔴 Высокая | `skills/README.md` перечисляет только 18 из 35 skills |
| 8 | `docs/GLOSSARY.md` | 1-72 | Полнота | 🟢 Низкая | Отсутствуют термины CAID, HITL, MCP, AC |
| 9 | `docs/MAINTENANCE_RUNBOOK.md` | 1-144 | Полнота | 🟢 Низкая | Нет секций для скриптов, benchmarks, profiles |
| 10 | `docs/` | — | API Docs | 🔴 Высокая | Нет API документации для tg_bot |
| 11 | `docs/delivery/` | — | Структура | 🟡 Средняя | Нет `delivery/README.md` |
| 12 | `agents/README.md` | 2 | Актуальность | 🟡 Средняя | Расхождение счётчика "33" vs "34" в разных документах |
| 13 | `agents/agent-manager/` | — | Полнота | 🟢 Низкая | Нет README для подкаталога |
| 14 | `skills/README.md` | 7-32 | Полнота | 🔴 Высокая | 17 из 35 skills не перечислены в таблице |
| 15 | `skills/README.md` | 52-59 | Полнота | 🟡 Средняя | Шаблон SKILL.md неполный |
| 16 | `scripts/README.md` | 16 | Полнота | 🟢 Низкая | `check-policy-encoding` только `.py`, нет обёрток |
| 17 | `tg_bot/README.md` | 1-86 | API Docs | 🟡 Средняя | Нет Command Reference и Event Schema |
| 18 | `tg_bot/README.md` | 1-86 | Полнота | 🟡 Средняя | Нет таблицы переменных окружения |
| 19 | `benchmarks/README.md` | 1-55 | API Docs | 🟡 Средняя | Нет описания формата fixtures |
| 20 | `profiles/README.md` | 1-21 | Полнота | 🟡 Средняя | Минимальная документация, нет примеров |
| 21 | `docs/*.md` | — | Навигация | 🟢 Низкая | Нет footer-навигации в документах |

---

## 11. Рекомендации по приоритетам

### 🔴 Высокий приоритет (немедленно)
1. **Синхронизировать `skills/README.md`** с `docs/skills-index.md` — добавить все 35 skills или ссылку на master list
2. **Создать API документацию для tg_bot** — команды, события, формат файлов
3. **Уточнить классификацию агентов** — добавить категорию "registry/platform agents"

### 🟡 Средний приоритет (в ближайшем спринте)
4. **Добавить Troubleshooting секцию** в корневой README
5. **Обновить `docs/README.md`** — включить все 37 файлов
6. **Создать `docs/delivery/README.md`** — индекс delivery документов
7. **Расширить `profiles/README.md`** — примеры, best practices
8. **Добавить таблицу env vars** в `tg_bot/README.md`
9. **Унифицировать счётчики агентов** во всех документах

### 🟢 Низкий приоритет (бэклог)
10. **Добавить CHANGELOG.md** или секцию версий
11. **Расширить глоссарий** терминами CAID, HITL, MCP, AC
12. **Добавить footer-навигацию** в документы `docs/`
13. **Создать `agents/agent-manager/README.md`**
14. **Добавить описание формата** benchmark fixtures

---

## 12. Оценка покрытия

| Критерий | Оценка | Комментарий |
|----------|--------|-------------|
| Полнота покрытия | 7/10 | Основные компоненты задокументированы, но skills и delivery документы неполны |
| Актуальность | 6/10 | Расхождения в счётчиках, не все файлы включены в индексы |
| Структура и навигация | 8/10 | Хорошая иерархия, но не хватает обратных ссылок |
| Примеры использования | 8/10 | Хорошие примеры в agents/README.md и scripts/README.md |
| Quick start guides | 9/10 | Отличные quick start в корневом README, agents, scripts, tg_bot |
| API документация | 4/10 | Отсутствует для tg_bot и benchmark fixtures |
| Troubleshooting / Runbooks | 7/10 | Хороший MAINTENANCE_RUNBOOK, но нет troubleshooting в README |
| Глоссарий терминов | 8/10 | Хороший GLOSSARY.md, но не все термины покрыты |
| Перекрёстные ссылки | 7/10 | Основные документы связаны, но не хватает обратных ссылок |

**Общая оценка: 7.1/10** — хорошая база, требует синхронизации и дополнения.

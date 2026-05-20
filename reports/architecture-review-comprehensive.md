# Комплексный архитектурный обзор многоагентной системы Cursor

**Дата:** 2026-04-04
**Объект:** Репозиторий конфигурации многоагентной системы для Cursor IDE
**Масштаб:** 34 агента, 32 skills, 5 rules, Telegram Bot, benchmarks, CI/CD

---

## СОДЕРЖАНИЕ

1. [Общая оценка архитектуры](#1-общая-оценка-архитектуры)
2. [Архитектура многоагентной системы](#2-архитектура-многоагентной-системы)
3. [Структура проекта и организация файлов](#3-структура-проекта-и-организация-файлов)
4. [Связи между компонентами](#4-связи-между-компонентами)
5. [Архитектурные паттерны и антипаттерны](#5-архитектурные-паттерны-и-антипаттерны)
6. [Масштабируемость и расширяемость](#6-масштабируемость-и-расширяемость)
7. [Модульность и связанность](#7-модульность-и-связанность)
8. [Telegram Bot архитектура](#8-telegram-bot-архитектура)
9. [Система бенчмарков и валидации](#9-система-бенчмарков-и-валидации)
10. [Сводная матрица проблем](#10-сводная-матрица-проблем)
11. [Приоритизированный план исправлений](#11-приоритизированный-план-исправлений)

---

## 1. Общая оценка архитектуры

### 1.1 Сильные стороны

| Аспект | Оценка | Комментарий |
|--------|--------|-------------|
| **Разделение ответственности** | ✅ Отлично | Чёткое разделение: start (роутер) → orchestrator (декомпозиция) → specialists (исполнение) |
| **Контрактная модель** | ✅ Отлично | Delegation contracts с OWNERSHIP, DEPENDENCIES, COMPLETION_CONTRACT |
| **Anti-loop защита** | ✅ Хорошо | Fingerprint-based detection, same-type depth cap = 3, rework_limit |
| **Evidence-first** | ✅ Хорошо | Claim-to-evidence matrix, lazy agent detection, pre-acceptance checklist |
| **CI/CD** | ✅ Хорошо | GitHub Actions на Linux + Windows, cross-platform скрипты (.sh/.py/.ps1) |
| **Документация** | ✅ Хорошо | 30+ документов, глоссарий, карты практик, runbook |
| **Benchmark система** | ✅ Хорошо | Behavior contracts + transcript fixtures + evaluator |

### 1.2 Критические проблемы

| # | Категория | Критичность | Краткое описание |
|---|-----------|-------------|------------------|
| P1 | Оркестрация | **CRITICAL** | `rules/orchestrator.mdc` — 691 строка монолитного промпта |
| P2 | Консистентность | **CRITICAL** | Дублирование правил между orchestrator.mdc, specialists.mdc, agent definitions |
| P3 | tg_bot интеграция | **HIGH** | Нет автоматической связи между оркестрацией и Telegram |
| P4 | Telemetry | **HIGH** | Telemetry contract определён, но не имплементирован |
| P5 | Context management | **HIGH** | Ручное управление контекстом, нет автоматического compaction |
| P6 | Skills дублирование | **MEDIUM** | 32 skills с перекрывающейся функциональностью |
| P7 | Registry drift | **MEDIUM** | Ручная синхронизация реестров при добавлении агентов |
| P8 | Testing gap | **MEDIUM** | Benchmarks проверяют наличие контрактов, но не их корректность |

---

## 2. Архитектура многоагентной системы

### 2.1 Иерархия агентов

```
┌─────────────────────────────────────────────────────────────┐
│                        USER                                  │
│                   /start /code /debug ...                     │
└──────────────────────────┬──────────────────────────────────┘
                           │
              ┌────────────▼────────────┐
              │   ENTRY POINTS (4)      │
              │  start, orchestrator,   │
              │  meta-agent-architect,  │
              │  subagent-factory       │
              └────────────┬────────────┘
                           │
              ┌────────────▼────────────┐
              │   COORDINATION (1)      │
              │     orchestrator        │
              │   (B0 supervisor)       │
              └────────────┬────────────┘
                           │
        ┌──────────────────┼──────────────────┐
        │                  │                  │
   ┌────▼────┐      ┌─────▼─────┐     ┌──────▼──────┐
   │ WRITERS │      │  READERS  │     │ SUB-ORCH    │
   │  code   │      │  review   │     │  (depth 2+) │
   │  test   │      │  security │     │             │
   │  docs   │      │  ask      │     │             │
   └────┬────┘      └─────┬─────┘     └──────┬──────┘
        │                 │                  │
        └─────────────────┼──────────────────┘
                          │
              ┌───────────▼───────────┐
              │   SPECIALISTS (29)    │
              │  domain experts       │
              └───────────────────────┘
```

### 2.2 Проблемы архитектуры агентов

#### P1: Монолитный orchestrator.mdc (CRITICAL)

**Файл:** [`rules/orchestrator.mdc`](rules/orchestrator.mdc) — 691 строка

**Проблема:**
- Файл содержит: протокол оркестрации, priority queue, rate limiting, retry budget, web research, agent council, adversarial refinement, VCS protocol, CAID attribution, ambiguity scoring, evidence schema, thinking checkpoints, delegation prompt hardening
- Это нарушает Single Responsibility Principle на уровне конфигурации
- При изменении одного аспекта (например, retry budget) нужно перечитывать весь файл

**Рекомендация:**
```
rules/orchestrator.mdc          ← Ядро: протокол, anti-loop, synthesis (≤150 строк)
rules/orchestration/
  ├── fan-out-policy.mdc        ← Writer/Reader лимиты, wave management
  ├── retry-budget.mdc          ← Retry limits, backoff strategy
  ├── rate-limiting.mdc         ← Token budget, concurrent tasks
  ├── web-research.mdc          §18 protocol, fact-pack, offline fallback
  ├── council.mdc               §17 Agent Council, judge, cherry-pick
  ├── vcs-protocol.mdc          §1.2 VCS, CAID attribution
  └── evidence-schema.mdc       §5 Evidence schema, completion contract
```

**Шаги:**
1. Выделить §0-§8 (ядро) в `rules/orchestrator.mdc` (сократить до ~150 строк)
2. Вынести §1.2-1.6 в `rules/orchestration/vcs-protocol.mdc`
3. Вынести §14-17 (council, debate, adversarial) в `rules/orchestration/council.mdc`
4. Вынести §18 (web research) в `rules/orchestration/web-research.mdc`
5. Вынести Rate Limiting, Retry Budget, Priority Queue в отдельные файлы
6. Обновить `rules/specialists.mdc` с новыми ссылками
7. Прогнать `scripts/run-full-repo-benchmark.sh` для валидации

---

#### P2: Дублирование правил между файлами (CRITICAL)

**Файлы:**
- [`rules/orchestrator.mdc`](rules/orchestrator.mdc:55-58) — Writer vs Reader таблица
- [`rules/specialists.mdc`](rules/specialists.mdc:84-86) — Та же Writer vs Reader таблица
- [`agents/start.md`](agents/start.md:100-115) — Строгие запреты
- [`agents/orchestrator.md`](agents/orchestrator.md:15-22) — Те же запреты
- [`skills/orchestrator/SKILL.md`](skills/orchestrator/SKILL.md:26-36) — QUICK RULES (дублирует orchestrator.mdc)

**Проблема:**
- Одно и то же правило (3+ parallel writers → escalate) определено в 3+ местах
- При изменении лимита (например, с 3 на 5) нужно обновить все копии
- Высокий риск рассинхронизации

**Рекомендация:**
1. Создать `rules/policy/` как единый источник политик:
   ```
   rules/policy/
   ├── fan-out-limits.yaml     ← Машиночитаемые лимиты
   ├── trust-boundary.yaml     ← TRUSTED_POLICY > TASK_INPUT > UNTRUSTED_EXTERNAL
   └── delegation-rules.yaml   ← Same-type cap, rework limits
   ```
2. В agent definitions и skills использовать ссылки: `См. rules/policy/fan-out-limits.yaml`
3. Добавить валидатор, проверяющий консистентность между policy YAML и текстом правил

---

#### P3: Отсутствие автоматической связи оркестрации с tg_bot (HIGH)

**Файлы:**
- [`tg_bot/main.py`](tg_bot/main.py) — Long-polling процесс
- [`tg_bot/ctl.py`](tg_bot/ctl.py) — CLI для событий
- [`rules/orchestrator.mdc`](rules/orchestrator.mdc:169) — Упоминает `./scripts/run-full-repo-benchmark.sh`

**Проблема:**
- Оркестратор НЕ вызывает `ctl.py event` после завершения волны
- tg_bot работает как отдельный процесс, не интегрированный в цепочку делегирования
- Пользователь должен вручную вызывать `ctl.py` для отправки уведомлений
- Нет автоматического heartbeat от оркестратора к боту

**Рекомендация:**
1. Добавить skill `tg-bot-integration/SKILL.md`:
   ```yaml
   name: tg-bot-integration
   description: Автоматическая отправка событий в Telegram после wave completion
   ```
2. В COMPLETION_CONTRACT добавить опциональное поле:
   ```yaml
   notification:
     send_to_telegram: true
     kind: wave_complete
     title: "Волна N завершена"
   ```
3. Orchestrator после синтеза вызывает:
   ```bash
   python3 tg_bot/ctl.py event --kind wave_complete --title "Волна N" --details "..."
   ```
4. Альтернатива: создать `tg_bot/orchestrator_hook.py` как post-commit hook

---

## 3. Структура проекта и организация файлов

### 3.1 Текущая структура

```
.
├── agents/              # 34 agent definitions (.md)
│   ├── start.md         # Entry point
│   ├── orchestrator.md  # Coordinator
│   └── ...              # 29 specialists + 3 meta
├── rules/               # 5 .mdc files (alwaysApply)
│   ├── orchestrator.mdc      # 691 строка (!)
│   ├── specialists.mdc       # 209 строк
│   ├── aleksander.mdc        # User preferences
│   └── agent-manager/        # Nested rule
├── skills/              # 32 skill directories
│   ├── orchestrator/SKILL.md
│   ├── delegation-contracts/SKILL.md
│   └── ...              # 30 more
├── docs/                # 30+ documentation files
├── benchmarks/          # Behavior contracts + transcript fixtures
├── scripts/             # Validation + benchmark scripts
├── tg_bot/              # Telegram control plane
├── profiles/            # Project-specific extensions
├── agent-tasks/         # Proof-loop artifacts
├── reports/             # Previous analysis reports
└── .github/workflows/   # CI validation
```

### 3.2 Проблемы структуры

#### P4: Несбалансированная глубина вложенности (MEDIUM)

**Проблема:**
- `skills/` — плоская структура (32 директории на одном уровне)
- `rules/` — частично вложенная (`rules/agent-manager/`)
- `docs/` — плоская структура (30+ файлов)
- `agents/` — плоская структура (34 файла)

**Рекомендация:**
```
skills/
├── orchestration/       # orchestrator, budget-orchestration, dag-validation
├── delegation/          # delegation-contracts, context-propagation
├── quality/             # thinking-checkpoints, agent-evals, agent-prompt-quality
├── autonomy/            # autonomous-execution, multi-pass-autonomy
├── discovery/           # specialist-discovery, dynamic-discovery, progressive-mcp
├── governance/          # mcp-governance, human-in-the-loop-gates, circuit-breaker
├── telemetry/           # telemetry-pipeline, structured-agent-logging
└── utilities/           # session-memory-tiers, tool-output-sanitization, ...

docs/
├── architecture/        # agents.md, delegation-chain.md, dag-branch-dependencies.md
├── operations/          # MAINTENANCE_RUNBOOK.md, start-workflow.md, quick-start-orchestration.md
├── quality/             # evidence-first-acceptance.md, process-and-quality-gates.md
├── security/            # security-governance-checklist.md, prompt-injection-probes.md
└── delivery/            # backlog.md, PBI-*/
```

---

#### P5: Отсутствие машиночитаемого реестра (MEDIUM)

**Файлы:**
- [`agents/README.md`](agents/README.md) — Текстовый реестр
- [`rules/specialists.mdc`](rules/specialists.mdc:103-138) — Таблица маршрутизации в markdown
- [`docs/skills-index.md`](docs/skills-index.md) — Текстовый индекс skills

**Проблема:**
- Реестры в текстовом формате, не валидируются автоматически
- При добавлении агента нужно обновить 3+ файла вручную
- [`scripts/validate-agent-registry.py`](scripts/validate-agent-registry.py:154-158) проверяет упоминание, но не структуру

**Рекомендация:**
1. Создать `registry/agents.yaml`:
   ```yaml
   agents:
     - name: start
       type: coordination
       file: agents/start.md
       rules: []
       skills: [start-workflow]
       description: "Главная точка входа..."
     - name: code
       type: specialist
       domain: development
       file: agents/code.md
       rules: [specialists]
       skills: [autonomous-execution]
   ```
2. Создать `registry/skills.yaml` аналогично
3. Генерировать markdown-реестры из YAML автоматически
4. Обновить валидатор для проверки YAML → markdown консистентности

---

## 4. Связи между компонентами

### 4.1 Граф зависимостей

```
agents/*.md ──references──> rules/*.mdc
     │                            │
     │                            │
     v                            v
skills/*/SKILL.md <──references───┘
     │
     v
docs/*.md <──cross-refs──> benchmarks/*.json
     │
     v
scripts/*.py ──validates──> agents/ + rules/ + skills/
     │
     v
.github/workflows/ ──runs──> scripts/
     │
     v
tg_bot/ ──(no direct link)──> orchestrator
```

### 4.2 Проблемы связей

#### P6: Циклические ссылки в документации (LOW)

**Проблема:**
- `rules/orchestrator.mdc` → `skills/thinking-checkpoints/SKILL.md`
- `skills/thinking-checkpoints/SKILL.md` → `rules/orchestrator.mdc`
- `skills/delegation-contracts/SKILL.md` → `rules/orchestrator.mdc` → `skills/delegation-contracts/SKILL.md`

**Рекомендация:**
- Установить иерархию: rules (policy) → skills (workflow) → docs (reference)
- Skills не должны ссылаться обратно на rules в обязательных секциях
- Добавить DAG validation в CI для проверки отсутствия циклов в ссылках

---

#### P7: Жёсткая связанность tg_bot с файловой системой (MEDIUM)

**Файл:** [`tg_bot/main.py`](tg_bot/main.py:287-288)

```python
store = StateStore(root)
store.ensure_layout()
```

**Проблема:**
- tg_bot хранит состояние в `tg_bot/runtime/`
- Нет интеграции с `.plan/` оркестратора
- Состояние бота и состояние оркестрации живут в разных мирах

**Рекомендация:**
1. Создать мост: `tg_bot/orchestrator_bridge.py`
2. Orchestrator после волны пишет в `.plan/wave-N.md`
3. tg_bot мониторит `.plan/` и отправляет обновления
4. Альтернатива: использовать `ctl.py event` как единый интерфейс

---

## 5. Архитектурные паттерны и антипаттерны

### 5.1 Реализованные паттерны

| Паттерн | Реализация | Качество |
|---------|-----------|----------|
| **Supervisor-Worker** | start → orchestrator → specialists | ✅ Хорошо |
| **Contract-First** | Delegation contracts с обязательными полями | ✅ Отлично |
| **Evidence-Based** | Claim-to-evidence matrix | ✅ Хорошо |
| **Circuit Breaker** | [`skills/circuit-breaker/SKILL.md`](skills/circuit-breaker/SKILL.md) | ⚠️ Определён, не enforced |
| **DAG Scheduling** | DEPENDENCIES: after:Bx, blocked-by:By | ✅ Хорошо |
| **Retry Budget** | Per-branch + global retry limits | ✅ Хорошо |
| **Thinking Checkpoints** | CP-1 через CP-6 | ✅ Хорошо |
| **Trust Boundary** | TRUSTED_POLICY > TASK_INPUT > UNTRUSTED_EXTERNAL | ✅ Отлично |

### 5.2 Антипаттерны

#### AP1: Prompt Bloat (CRITICAL)

**Файл:** [`rules/orchestrator.mdc`](rules/orchestrator.mdc) — 691 строка

**Проблема:**
- Один файл содержит 19 секций с разной ответственностью
- LLM будет "забывать" дальние секции при ограниченном контексте
- Невозможно тестировать отдельные аспекты изолированно

**Влияние:**
- При сложных задачах оркестратор может игнорировать правила из конца файла
- Rate limiting (§12), Priority Queue (§11), Retry Budget (§10) — все в одном файле
- Критические правила (§0.1 СТРОГИЕ ЗАПРЕТЫ) могут "теряться" среди менее важных

---

#### AP2: Rule Duplication (CRITICAL)

**Примеры дублирования:**

| Правило | orchestrator.mdc | specialists.mdc | agent definition |
|---------|-----------------|-----------------|------------------|
| Writer fan-out limit | §0 (строка 18) | §0.2 (строка 85) | agents/code.md |
| SINGLE_AGENT_DEGRADED_MODE запрет | §0.5 (строка 97) | §Runtime (строка 163) | agents/start.md |
| FIRST_ACTION gate | §0.6.1 (строка 126) | — | agents/start.md (строка 9) |
| TRUSTED_POLICY порядок | §3 (строка 243) | §Input trust (строка 203) | agents/orchestrator.md |

**Влияние:**
- При изменении правила нужно найти и обновить все копии
- Высокий риск рассинхронизации
- Валидаторы проверяют наличие, но не консистентность

---

#### AP3: Manual Registry Management (MEDIUM)

**Проблема:**
- Добавление нового агента требует обновления:
  1. `agents/<name>.md` (создание)
  2. `agents/README.md` (реестр)
  3. `rules/specialists.mdc` (маршрутизация)
  4. `docs/agents.md` (документация)
  5. `README.md` (корневой счётчик)
- [`scripts/validate-agent-registry.py`](scripts/validate-agent-registry.py) проверяет, но не автоматизирует

---

#### AP4: No Runtime Enforcement (HIGH)

**Проблема:**
- OWNERSHIP — логическая гарантия, не enforced
- DEPENDENCIES — оркестратор обязан соблюдать, но нет валидации
- DEPTH_BUDGET — передаётся в промпте, но не контролируется runtime
- Rate limiting (§12) — описан, но не имплементирован

**Влияние:**
- Агент может нарушить OWNERSHIP — система не обнаружит
- Циклические зависимости возможны при ошибке оркестратора
- Rate limiting существует только как документ

---

## 6. Масштабируемость и расширяемость

### 6.1 Текущие лимиты

| Параметр | Значение | Обоснование |
|----------|----------|-------------|
| Агентов | 34 | 4 coordination + 30 specialists |
| Skills | 32 | Различные workflow |
| L1 writer fan-out | ≤6 | OWNERSHIP safety |
| Specialist writer fan-out | 3+ → escalate | Local coordination |
| Same-type depth | ≤3 | Anti-loop |
| DEPTH_BUDGET max | 15 | Open-ended tasks |
| Max chain length | 10 | DAG validation |

### 6.2 Проблемы масштабируемости

#### P8: Orchestrator как bottleneck (MEDIUM)

**Проблема:**
- Весь fan-out проходит через одного оркестратора
- При 10+ независимых задачах orchestrator становится bottleneck декомпозиции
- Нет механизма разделения orchestration load

**Рекомендация:**
1. При >6 writer-веток — автоматический sub-orchestrator
2. Domain-based routing: code-orchestrator, docs-orchestrator, test-orchestrator
3. Parallel decomposition: независимые поддомены декомпозируются параллельно

---

#### P9: Context Window Management (HIGH)

**Проблема:**
- При 10+ tool calls требуется manual summarization
- Session memory tiers ([`skills/session-memory-tiers/SKILL.md`](skills/session-memory-tiers/SKILL.md)) — ручное управление
- Нет автоматического eviction policy

**Влияние:**
- При длинных сессиях контекст распухает
- LLM "забывает" ранние инструкции
- Quality degradation при deep delegation

**Рекомендация:**
1. Автоматический context compaction при 10+ tool calls
2. Structured context propagation как часть контракта
3. Automated eviction по размеру и age

---

## 7. Модульность и связанность

### 7.1 Матрица связанности

| Компонент | Зависит от | Зависимости | Связанность |
|-----------|-----------|-------------|-------------|
| `agents/start.md` | rules/orchestrator.mdc, docs/delegation-chain.md | 2 | Низкая ✅ |
| `agents/orchestrator.md` | rules/orchestrator.mdc, skills/* | 5+ | Средняя ⚠️ |
| `rules/orchestrator.mdc` | skills/*, docs/* | 10+ | Высокая ❌ |
| `rules/specialists.mdc` | agents/*, skills/* | 35+ | Высокая ❌ |
| `tg_bot/main.py` | tg_bot/config.py, state_store.py | 2 | Низкая ✅ |

### 7.2 Проблемы связанности

#### P10: High coupling rules/specialists.mdc (MEDIUM)

**Файл:** [`rules/specialists.mdc`](rules/specialists.mdc) — 209 строк

**Проблема:**
- Содержит routing table для всех 34 агентов
- Содержит swarm protocol
- Содержит degradation protocol
- Содержит input trust boundary
- Ссылается на 28 skills

**Рекомендация:**
```
rules/specialists.mdc          ← Routing table only (≤50 строк)
rules/specialists/
  ├── swarm.mdc                ← Mandatory SWARM protocol
  ├── degradation.mdc          ← Graceful degradation
  ├── trust-boundary.mdc       ← Input trust, injection defense
  └── cost-aware.mdc           ← Cost-aware routing
```

---

## 8. Telegram Bot архитектура

### 8.1 Архитектура tg_bot

```
┌─────────────────────────────────────────────┐
│              Telegram Bot API                │
│              (long-polling)                  │
└──────────────────┬──────────────────────────┘
                   │
          ┌────────▼────────┐
          │    main.py      │  ← Event loop
          │  (339 строк)    │     process_updates + process_events
          └────────┬────────┘
                   │
     ┌─────────────┼─────────────┐
     │             │             │
┌────▼────┐ ┌─────▼─────┐ ┌────▼────┐
│config.py│ │state_store│ │  ctl.py │
│  (97)   │ │   (N/A)   │ │  (119)  │
└─────────┘ └───────────┘ └─────────┘
                   │
          ┌────────▼────────┐
          │   runtime/      │  ← File-based state
          │  ├── control.md │
          │  ├── heartbeat  │
          │  ├── events/    │
          │  └── approvals/ │
          └─────────────────┘
```

### 8.2 Проблемы tg_bot

#### P11: Отсутствие интеграции с оркестрацией (HIGH)

**Проблема:**
- tg_bot — изолированный компонент
- Оркестратор НЕ отправляет события в Telegram
- Пользователь должен вручную вызывать `ctl.py`
- Нет автоматического уведомления о завершении волн

**Рекомендация:**
1. Добавить post-wave hook в orchestrator:
   ```
   После синтеза → если notification.enabled → ctl.py event
   ```
2. Создать `tg_bot/orchestrator_hook.py`:
   ```python
   def notify_wave_complete(wave_report: dict):
       store.enqueue_event(
           kind="wave_complete",
           title=wave_report["title"],
           details=wave_report["summary"]
       )
   ```
3. Orchestrator вызывает hook через Shell после синтеза

---

#### P12: File-based state management (MEDIUM)

**Проблема:**
- Состояние хранится в markdown-файлах
- Нет атомарных операций
- Возможны race conditions при параллельном доступе

**Рекомендация:**
1. Добавить file locking для записи состояния
2. Использовать атомарные rename (write to .tmp, then rename)
3. Для production рассмотреть SQLite

---

#### P13: Отсутствие тестов (MEDIUM)

**Проблема:**
- Нет unit тестов для tg_bot
- Нет integration тестов
- Нет mock Telegram API

**Рекомендация:**
1. Добавить `tg_bot/tests/`
2. Mock Telegram API responses
3. Test control command handling
4. Test event processing

---

## 9. Система бенчмарков и валидации

### 9.1 Архитектура бенчмарков

```
benchmarks/
├── behavior-contracts.json    # 34 сценария, regex/path проверки
├── transcript-cases.json      # Fixture-suite для evaluator
├── transcript-fixtures/
│   ├── pass/                  # 12 pass fixtures
│   └── fail/                  # 11 fail fixtures
└── exporter-fixtures/
    └── sample-composer-data.json

scripts/
├── validate-agent-registry.py     # Проверка реестра агентов
├── validate-repo-consistency.py   # Проверка консистентности
├── run-behavior-benchmarks.py     # Behavior contract checks
├── evaluate-transcript-runs.py    # Transcript evaluator
├── export-delegation-tree.py      # Delegation tree exporter
├── run-full-repo-benchmark.py     # Full pipeline
└── check-policy-encoding.py       # Encoding validation
```

### 9.2 Проблемы бенчмарков

#### P14: Behavior contracts — только наличие, не корректность (MEDIUM)

**Файл:** [`benchmarks/behavior-contracts.json`](benchmarks/behavior-contracts.json)

**Проблема:**
- Проверяет наличие regex паттернов в файлах
- Не проверяет семантическую корректность
- Не проверяет выполнимость правил
- Пример: проверяет наличие `MULTI_AGENT_PIPELINE_BLOCKED`, но не что правило работает

**Рекомендация:**
1. Добавить semantic validation layer
2. Transcript fixtures покрывают больше — расширить
3. Добавить mutation testing: намеренно сломать правило → benchmark должен обнаружить

---

#### P15: Transcript fixtures — ограниченный coverage (MEDIUM)

**Проблема:**
- 12 pass + 11 fail fixtures
- Не покрывают все edge cases
- Нет fixtures для:
  - Circuit breaker activation
  - Rate limiting
  - Priority queue preemption
  - Multi-wave 24/7 cycle

**Рекомендация:**
1. Добавить fixtures для missing scenarios
2. Генерировать fixtures из реальных транскриптов
3. Добавить property-based testing

---

#### P16: Отсутствие performance benchmarks (LOW)

**Проблема:**
- Нет замеров времени выполнения валидации
- Нет benchmark для large agent registries (100+ агентов)
- Нет stress testing

---

## 10. Сводная матрица проблем

| ID | Категория | Критичность | Файлы | Усилие | Влияние |
|----|-----------|-------------|-------|--------|---------|
| P1 | Монолит orchestrator.mdc | **CRITICAL** | rules/orchestrator.mdc | Medium | High |
| P2 | Дублирование правил | **CRITICAL** | rules/*.mdc, agents/*.md | Medium | High |
| P3 | tg_bot интеграция | **HIGH** | tg_bot/, rules/orchestrator.mdc | Medium | High |
| P4 | Telemetry не имплементирован | **HIGH** | docs/agent-telemetry-contract.md | High | Medium |
| P5 | Context management | **HIGH** | skills/session-memory-tiers/ | Medium | High |
| P6 | Циклические ссылки | LOW | docs/, skills/ | Low | Low |
| P7 | tg_bot state management | MEDIUM | tg_bot/runtime/ | Medium | Medium |
| P8 | Orchestrator bottleneck | MEDIUM | agents/orchestrator.md | High | Medium |
| P9 | Context window | HIGH | skills/session-memory-tiers/ | Medium | High |
| P10 | Coupling specialists.mdc | MEDIUM | rules/specialists.mdc | Medium | Medium |
| P11 | tg_bot ↔ orchestrator | HIGH | tg_bot/, agents/orchestrator.md | Medium | High |
| P12 | File-based state | MEDIUM | tg_bot/runtime/ | Medium | Medium |
| P13 | Нет тестов tg_bot | MEDIUM | tg_bot/ | Medium | Medium |
| P14 | Benchmark coverage | MEDIUM | benchmarks/ | Medium | Medium |
| P15 | Transcript coverage | MEDIUM | benchmarks/transcript-fixtures/ | Low | Medium |
| P16 | Нет perf benchmarks | LOW | benchmarks/ | Low | Low |

---

## 11. Приоритизированный план исправлений

### Wave 1: Критические исправления (1-2 недели)

| Задача | Описание | Файлы | Критерий готовности |
|--------|----------|-------|---------------------|
| **W1-T1** | Рефакторинг orchestrator.mdc | rules/orchestrator.mdc → rules/orchestration/* | orchestrator.mdc ≤ 150 строк, все тесты проходят |
| **W1-T2** | Дедупликация правил | rules/policy/*.yaml | Единый источник для fan-out limits, trust boundary |
| **W1-T3** | Автоматическая валидация контрактов | scripts/validate-contracts.py | Pre-flight check перед Task() |

### Wave 2: Высокий приоритет (2-3 недели)

| Задача | Описание | Файлы | Критерий готовности |
|--------|----------|-------|---------------------|
| **W2-T1** | Интеграция tg_bot с оркестрацией | tg_bot/orchestrator_hook.py | Автоматические уведомления после волн |
| **W2-T2** | Context compaction automation | skills/session-memory-tiers/ | Авто-compaction при 10+ tool calls |
| **W2-T3** | Машиночитаемый реестр | registry/agents.yaml, registry/skills.yaml | YAML → markdown генерация |

### Wave 3: Средний приоритет (3-4 недели)

| Задача | Описание | Файлы | Критерий готовности |
|--------|----------|-------|---------------------|
| **W3-T1** | Рефакторинг specialists.mdc | rules/specialists.mdc → rules/specialists/* | specialists.mdc ≤ 50 строк |
| **W3-T2** | Расширение transcript fixtures | benchmarks/transcript-fixtures/ | +10 fixtures для edge cases |
| **W3-T3** | Тесты для tg_bot | tg_bot/tests/ | 80% coverage |
| **W3-T4** | Telemetry implementation | docs/agent-telemetry-contract.md → имплементация | Сбор метрик в реальном времени |

### Wave 4: Долгосрочные улучшения (1-2 месяца)

| Задача | Описание | Файлы | Критерий готовности |
|--------|----------|-------|---------------------|
| **W4-T1** | Domain-based orchestrators | agents/code-orchestrator.md, ... | Параллельная декомпозиция |
| **W4-T2** | CAID с git worktrees | rules/orchestration/vcs-protocol.mdc | Физическая изоляция веток |
| **W4-T3** | Performance benchmarks | benchmarks/performance/ | Stress testing для 100+ агентов |

---

## ПРИЛОЖЕНИЕ A: Рекомендации по рефакторингу orchestrator.mdc

### Текущая структура (691 строка):

```
§0    Общие принципы (23 строки)
§0.1  СТРОГИЕ ЗАПРЕТЫ (5 строк)
§0.2  ПРАВО НА САМОДЕЛЕГИРОВАНИЕ (67 строк)
§0.5  Runtime capability gate (6 строк)
§0.6  Task-chain consistency (14 строк)
§1    Конверт задачи (60 строк)
§2    Типы задач (4 строки)
§3    Делегирование (60 строк)
§4    Auto-Split Protocol (25 строк)
§5    Priority Queue (25 строк)
§6    Retry Budget (20 строк)
§7    Rate Limiting (25 строк)
§8    Proof-of-delegation (4 строки)
§9    Anti-loop (8 строк)
§10   Quality gates (30 строк)
§11   Синтез результатов (2 строки)
§12   Self-evaluation (2 строки)
§13   Chain Verification (10 строк)
§14   Session Continuation (4 строки)
§15   Thinking Checkpoints (2 строки)
§16   Delegation prompt hardening (25 строк)
§17   Декомпозиция (30 строк)
§18   Core Files Enforcement (4 строки)
§19   Multi-Model Debate (10 строк)
§20   Adversarial Peer Refinement (8 строк)
§21   Phase-Tree Branch IDs (6 строк)
§22   Agent Council (15 строк)
§23   Web Research pre-implementation (30 строк)
§24   /start default execution hardening (15 строк)
```

### Рекомендуемая структура:

```
rules/orchestrator.mdc (≤150 строк):
  §0    Общие принципы + FIRST_ACTION
  §0.1  Runtime capability gate
  §0.2  Task-chain consistency
  §1    Конверт задачи (ссылки на sub-rules)
  §2    Делегирование (ссылки на sub-rules)
  §3    Anti-loop
  §4    Quality gates (ссылки на sub-rules)
  §5    Синтез результатов

rules/orchestration/fan-out-policy.mdc:
  - Writer vs Reader лимиты
  - Auto-Split Protocol
  - Wave Management

rules/orchestration/retry-budget.mdc:
  - Per-branch retry limits
  - Global retry budget
  - Retry strategy

rules/orchestration/rate-limiting.mdc:
  - Orchestrator limits
  - Throttling strategy
  - Token budget tracking

rules/orchestration/council.mdc:
  - Multi-Model Debate
  - Adversarial Peer Refinement
  - Agent Council Protocol

rules/orchestration/web-research.mdc:
  - Fact-pass protocol
  - Implementation branches
  - Offline fallback

rules/orchestration/vcs-protocol.mdc:
  - VCS iteration protocol
  - CAID git attribution
  - Ambiguity scoring

rules/orchestration/evidence-schema.mdc:
  - Evidence schema (YAML)
  - Completion contract
  - Claim-to-evidence matrix

rules/orchestration/prompt-hardening.mdc:
  - Mandatory prompt skeleton
  - RUBRIC_SELF_CHECK
  - Escalation for shallow work

rules/orchestration/decomposition.mdc:
  - Pre-Delegation Structural Check
  - 5-Phase Pipeline
  - Decomposition rules
  - Core Files Enforcement
```

---

## ПРИЛОЖЕНИЕ B: Чеклист для каждого рефакторинга

### Перед началом:
- [ ] Зафиксировать текущее состояние: `git status`
- [ ] Прогнать все валидаторы: `scripts/run-full-repo-benchmark.sh`
- [ ] Сохранить baseline: `git stash`

### Во время:
- [ ] Изменять один аспект за раз
- [ ] После каждого изменения: `scripts/validate-repo-consistency.sh`
- [ ] Обновлять ссылки в зависимых файлах

### После:
- [ ] Прогнать полный benchmark: `scripts/run-full-repo-benchmark.sh`
- [ ] Проверить CI: `gh run list`
- [ ] Smoke test: 4 сценария из README.md
- [ ] Задокументировать изменения в commit message

---

*Отчёт сформирован на основе анализа 40+ файлов: agents/*.md, rules/*.mdc, skills/*/SKILL.md, docs/*.md, benchmarks/*.json, scripts/*.py, tg_bot/*.py*

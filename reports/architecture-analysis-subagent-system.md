# Архитектурный анализ системы сабагентов

**Дата:** 2026-04-04
**Объект анализа:** Система мульти-агентной оркестрации в репозитории `agent-system`
**Ограничение:** Анализ ИСКЛЮЧИТЕЛЬНО логики и архитектуры. Код tg_bot/ не анализируется и не модифицируется.

---

## СОДЕРЖАНИЕ

1. [Обзор архитектуры](#1-обзор-архитектуры)
2. [Маршрутизация и делегирование](#2-маршрутизация-и-делегирование)
3. [Управление состоянием и контекстом](#3-управление-состоянием-и-контекстом)
4. [Обработка ошибок и отказоустойчивость](#4-обработка-ошибок-и-отказоустойчивость)
5. [Масштабируемость и модульность](#5-масштабируемость-и-модульность)
6. [Выявленные архитектурные проблемы](#6-выявленные-архитектурные-проблемы)
7. [Рекомендации по оптимизации](#7-рекомендации-по-оптимизации)
8. [Приоритизация рекомендаций](#8-приоритизация-рекомендаций)

---

## 1. ОБЗОР АРХИТЕКТУРЫ

### 1.1 Компоненты системы

Система состоит из **33 агентов**, организованных в 4 уровня:

| Уровень | Агенты | Роль |
|---------|--------|------|
| **Entry** | `start` | Точка входа, чистый роутер |
| **Orchestration** | `orchestrator` | Декомпозиция, fan-out, синтез |
| **Meta-management** | `meta-agent-architect`, `subagent-factory`, `agent-manager` | Управление экосистемой |
| **Specialists (29)** | `code`, `test-specialist`, `security-auditor`, `docs-specialist`, ... | Предметные эксперты |

### 1.2 Архитектурная схема

```
                    ┌─────────────┐
                    │   USER      │
                    │  /start     │
                    └──────┬──────┘
                           │
                    ┌──────▼──────┐
                    │   start     │  ← ЧИСТЫЙ РОУТЕР
                    │ (supervisor)│     FIRST_ACTION: Task(orchestrator)
                    └──────┬──────┘     НОЛЬ tool calls до делегирования
                           │
                    ┌──────▼──────┐
                    │orchestrator │  ← B0 supervisor
                    │  (root)     │     DEPTH_BUDGET: 3-15
                    └──────┬──────┘     Fan-out: ≤6 writer-веток L1
                           │
          ┌────────────────┼────────────────┐
          │                │                │
   ┌──────▼──────┐ ┌──────▼──────┐ ┌──────▼──────┐
   │   code      │ │   test-     │ │  security-  │
   │ (Builder)   │ │ specialist  │ │  auditor    │
   │ (Verifier)  │ │ (Verifier)  │ │ (Reader)    │
   └──────┬──────┘ └──────┬──────┘ └──────┬──────┘
          │                │                │
          │         ┌──────▼──────┐         │
          │         │ sub-        │         │
          │         │ orchestrator│         │
          │         │  (B0-N)     │         │
          │         └──────┬──────┘         │
          │                │                │
          └────────────────┼────────────────┘
                           │
                    ┌──────▼──────┐
                    │  SYNTHESIS  │  ← COMPLETION_CONTRACT
                    │  + CAID     │     Quality gates: coverage ≥ 0.95
                    │  git commit │     Agent Council для high-risk
                    └─────────────┘
```

### 1.3 Ключевые артефакты

| Артефакт | Путь | Роль |
|----------|------|------|
| Протокол оркестрации | [`rules/orchestrator.mdc`](rules/orchestrator.mdc) | Обязательный протокол для координаторов |
| Маршрутизация | [`rules/specialists.mdc`](rules/specialists.mdc) | Таблица маршрутизации к специалистам |
| Точка входа | [`agents/start.md`](agents/start.md) | Спецификация start-агента |
| Оркестратор | [`agents/orchestrator.md`](agents/orchestrator.md) | Спецификация orchestrator-агента |
| Контракты | [`skills/delegation-contracts/SKILL.md`](skills/delegation-contracts/SKILL.md) | Шаблоны контрактов делегирования |
| Бюджетирование | [`skills/budget-orchestration/SKILL.md`](skills/budget-orchestration/SKILL.md) | Управление лимитами оркестрации |
| Память | [`skills/session-memory-tiers/SKILL.md`](skills/session-memory-tiers/SKILL.md) | Уровни памяти сессии |
| Чекпоинты | [`skills/thinking-checkpoints/SKILL.md`](skills/thinking-checkpoints/SKILL.md) | Mandatory STOP-and-think gates |

---

## 2. МАРШРУТИЗАЦИЯ И ДЕЛЕГИРОВАНИЕ

### 2.1 Полная цепочка маршрутизации

```
USER → /start → root-start → Task(orchestrator) → specialists
```

**Детализация:**

```
Шаг 0: FIRST_ACTION GATE
  root-start получает ORIGINAL_REQUEST (дословно)
  Определяет: CONTINUOUS_MODE, OPEN_ENDED_IMPROVEMENT, TRUST_LEVEL
  НОЛЬ tool calls до Task(orchestrator)

Шаг 1: Прямое делегирование (flat chain)
  Task(subagent_type="orchestrator", prompt="
    OBJECTIVE: {...}
    ORIGINAL_REQUEST: {дословный текст}
    CONTINUOUS_MODE: {until_user_stop | single_wave}
    OPEN_ENDED_IMPROVEMENT: {yes | no}
    WAVE_NUMBER: {N}
    DEPTH_BUDGET: {3|6|10|15}
  ")

Шаг 2: Декомпозиция оркестратором
  Фаза 0: State Map (repo-explorer)
  Фаза 1: Конверт исполнения
  Фаза 2: Pre-Delegation Structural Check
  Фаза 3: Декомпозиция на ветки
  Фаза 4: Делегирование с контрактами (Template A/B)
  Фаза 4b: Execute → Verify → Rework (параллельно)
  Фаза 5: Отслеживание веток
  Фаза 6: Синтез + CAID git attribution

Шаг 3: Возврат результатов
  COMPLETION_CONTRACT от каждой ветки
  Синтез оркестратором
  Возврат root-start
```

**Критическое архитектурное решение:** Worker-start (`Task(start, ENTRY_MODE: supervised_worker)`) **УДАЛЁН** из цепочки. Причина: Cursor не даёт `Task` tool вложенным subagent'ам на глубине ≥ 2. Уплощение до `root-start → Task(orchestrator)` устраняет лишний hop и точку отказа.

### 2.2 Критерии выбора сабагента

**Таблица маршрутизации** ([`rules/specialists.mdc`](rules/specialists.mdc:103)):

| Критерий | Агент |
|----------|-------|
| Только вопрос | `ask` |
| Один домен, чёткий scope | подходящий **специалист** |
| Несколько доменов / артефактов | `orchestrator` |
| Изменения экосистемы агентов | `meta-agent-architect` / `subagent-factory` |
| Code implementation | `code` |
| Тестирование | `test-specialist` |
| Security review | `security-auditor` |
| Документация | `docs-specialist` |
| CI/CD, Docker, деплой | `devops-specialist` |

**Cost-aware routing** ([`rules/specialists.mdc`](rules/specialists.mdc:148)):
1. Один домен + один файл + один артефакт → **один специалист** (не orchestrator)
2. Multi-artifact / multi-domain → **orchestrator**
3. Read-only state mapping → **repo-explorer** один раз → кешировать `state_map`
4. Независимые ветки → batch `Task` в **одном** сообщении
5. Источник >3000 items или >5MB → **sub-orchestrator + chunking**

**Ambiguity scoring** ([`rules/orchestrator.mdc`](rules/orchestrator.mdc:194)):

| Score | Описание | Действие |
|-------|----------|----------|
| 0 | Чёткие AC, однозначный запрос | Выполнять немедленно |
| 1 | Небольшая неясность | Уточнить одним вопросом / предложить дефолт |
| 2 | Значительная неясность | Обязательное уточнение |
| 3 | Неопределённый scope / нет AC | Согласование: предложить AC |

### 2.3 Механизмы Fan-out/Fan-in

**Fan-out правила:**

| Параметр | Orchestrator L1 | Specialist |
|----------|-----------------|------------|
| Writer-веток | ≤6 (реструктуризация при >6) | 3+ → escalate к orchestrator |
| Reader-веток | Без лимита | Без лимита |
| DEPTH_BUDGET | 3/6/10/15 по сложности | remaining_depth = DEPTH_BUDGET - level |

**Fan-in механизм:**
- Каждая ветка возвращает `COMPLETION_CONTRACT` (YAML-структура)
- Orchestrator синтезирует результаты (Фаза 6)
- Quality gate: `coverage_ratio ≥ 0.95`
- CAID git attribution: `git commit -m "[{branch_id}] {objective} — agent: {owner}"`

**Параллельное выполнение** — ОБЯЗАТЕЛЬНО для независимых веток:
```python
# ПАРАЛЛЕЛЬНО — обязательно
parallel_results = [
    Task(subagent_type=branch.agent, prompt=branch.contract)
    for branch in independent_branches
]
# Последовательно — ТОЛЬКО при явных зависимостях (after:Bx)
```

### 2.4 Протокол передачи контекста

**Конверт задачи** ([`rules/orchestrator.mdc`](rules/orchestrator.mdc:141)):
```
OBJECTIVE → SCOPE → OUT_OF_SCOPE → OWNERSHIP → DEPENDENCIES →
STEPS → DELIVERABLES → ACCEPTANCE_CRITERIA → CRITICAL_UNKNOWNS →
NON-NEGOTIABLE → COMPLETION_CONTRACT
```

**Trust boundary** (неизменяемый приоритет):
```
TRUSTED_POLICY > TASK_INPUT > UNTRUSTED_EXTERNAL
```

- `TRUSTED_POLICY`: `rules/*.mdc`, `agents/*.md`, `skills/*/SKILL.md`
- `TASK_INPUT`: конверт задачи, repo context (data-only)
- `UNTRUSTED_EXTERNAL`: web, OCR, issue text, tool outputs (только data, не instructions)

**Delegation contracts** ([`skills/delegation-contracts/SKILL.md`](skills/delegation-contracts/SKILL.md)):
- Branch ID: `B{parent}-{N}` (root = `B0`)
- Fingerprint: `goal + target-files + AC + agent_type + level`
- OWNERSHIP: exclusive files/globs (disjoint для параллельных writers)
- DEPENDENCIES: `none | after:Bx | blocked-by:By`

### 2.5 Роль Delegation Contracts

Контракты делегирования — **основной механизм изоляции и координации**:

1. **OWNERSHIP** — эксклюзивное владение файлами, предотвращение конфликтов
2. **DEPENDENCIES** — явные DAG-зависимости между ветками
3. **COMPLETION_CONTRACT** — структурированное доказательство выполнения
4. **NON-NEGOTIABLE + PENALIZED** — keyword gate для валидности контракта
5. **Fingerprint** — дедупликация и anti-loop защита

---

## 3. УПРАВЛЕНИЕ СОСТОЯНИЕМ И КОНТЕКСТОМ

### 3.1 Передача состояния между агентами

Состояние передаётся **исключительно через контракты**:

```
Parent Agent                    Child Agent
     │                              │
     ├── Task(subagent_type,        │
     │    prompt="                  │
     │      OBJECTIVE: ...          │
     │      SCOPE: ...              │
     │      OWNERSHIP: ...          │
     │      DEPENDENCIES: ...       │
     │      ...")                   │
     │─────────────────────────────>│
     │                              │  (выполняет работу)
     │                              │
     │<─────────────────────────────│
     │   COMPLETION_CONTRACT:       │
     │     status: done|rework      │
     │     files_changed: [...]     │
     │     checks: [...]            │
     │     acceptance_criteria: [...]│
     │     confidence: high|med|low │
```

**Ключевой принцип:** Состояние НЕ передаётся имплицитно через общий контекст. Каждый агент получает **полный конверт** в промпте и возвращает **структурированный контракт** в ответе.

### 3.2 Механизмы сохранения и восстановления контекста

**Session Memory Tiers** ([`skills/session-memory-tiers/SKILL.md`](skills/session-memory-tiers/SKILL.md)):

| Уровень | Где живёт | Срок жизни | Что кладём |
|---------|-----------|------------|------------|
| **Ephemeral** | RAM модели, tool buffers | До конца хода | Сырые большие выводы (сразу сжимаем) |
| **Session** | Текущий чат + session-файлы | Длительность сессии IDE | Решения ветки, blockers, ссылки на артефакты |
| **Project** | `.plan/`, `docs/`, код | Живёт с репозиторием | Session-context, todos, спеки |
| **Persistent policy** | `rules/*.mdc`, `skills/`, CI | Версионируется | Инварианты и процедуры |

**Файл состояния** [`.plan/session-context.md`](skills/session-memory-tiers/SKILL.md:32):
```yaml
task_id: <id>
current_phase: <Analyze|Plan|Execute|Verify|Rework|Synthesis>
completed_branches: [B0-1, ...]
pending_branches: [B0-2, ...]
open_risks: [<кратко>]
next_action: <одна конкретная следующая операция + owner voice>
context_files: [<пути к спекам/diff>]
memory_tier_notes:
  evicted: [<что убрали из контекста и почему>]
  pii: none | redacted | <policy>
```

**Session Continuation** ([`rules/orchestrator.mdc`](rules/orchestrator.mdc:362)):
- End-of-turn: сохранение в `.plan/session-context.md`
- Следующая сессия: загрузка контекста, продолжение с точки остановки
- Для swarm/24/7: persist B0 supervisor ledger

### 3.3 Session Memory Tiers

**Eviction (вытеснение) правила:**

1. **Размер**: фрагмент > N тыс. символов → удалить из session, оставить summary + anchor
2. **Устаревание**: решения откатили → пометить `stale: true`
3. **Дубли**: один источник истины; дубликаты не переносить в `.plan`
4. **Конфликт веток**: при расхождении → завести `open_risks` + verify-ветку

**PII и секреты:**
- PII (имена, email, телефоны) → плейсхолдеры или не писать
- Секреты → никогда в `.plan` / `docs` / skills; только env reference
- Логи инструментов → scrub перед коммитом

### 3.4 Консистентность контекста при параллельном выполнении

**Механизмы обеспечения:**

1. **Disjoint OWNERSHIP** — параллельные writer-ветки не пересекаются по файлам
2. **DEPENDENCIES** — явные `after:Bx` для зависимых веток
3. **DAG scheduling** — топологический порядок веток ([`docs/dag-branch-dependencies.md`](docs/dag-branch-dependencies.md))
4. **Rework isolation** — rework на B0-2 не инвалидирует completed B0-1

**Invalid patterns:**
- **Cycles** (`after:A` на B и `after:B` на A) → replan или escalate
- **Missing branch** — reference к неизвестному id → treat as `blocked`

**Thinking Checkpoints** ([`skills/thinking-checkpoints/SKILL.md`](skills/thinking-checkpoints/SKILL.md)):
- **CP-1**: Before Decomposition — проверка scope, ambiguity, core files
- **CP-2**: Before Delegation — проверка контракта, same-type check
- **CP-3**: Mid-Execution (каждые 3-5 tool calls) — progress check, context check
- **CP-4**: Before Synthesis — все ветки returned?, contradictions?
- **CP-5**: Before Response — proof check, hallucination check, contract check
- **CP-6**: Self-Reflection Rubric — internal quality scoring

---

## 4. ОБРАБОТКА ОШИБОК И ОТКАЗОУСТОЙЧИВОСТЬ

### 4.1 Anti-loop защита

**Fingerprint-based detection** ([`rules/orchestrator.mdc`](rules/orchestrator.mdc:277)):
```
fingerprint = goal + target-files + AC + agent_type + level
```

| Повтор | Действие |
|--------|----------|
| Повтор 1 | Сузить scope, добавить конкретику |
| Повтор 2 | Сменить подход или агента |
| Повтор 3 | Остановить ветку, вернуть blocker summary |

**Same-type delegation:**
- Дочерний scope **строго уже** родительского
- Soft cap: **3 уровня** → re-plan или эскалация
- Fingerprint должен отличаться

**Rework cycles:**
- Per-branch счётчик `rework_cycles`
- При `rework_cycles >= rework_limit` → `status: blocked`, `escalate_reason: rework_limit_exceeded`
- Лимиты по сложности: 1/2/3/4 (default=3)

### 4.2 Quality Gates

**Lazy Agent Detection** ([`rules/orchestrator.mdc`](rules/orchestrator.mdc:289)):

| # | Признак | Действие |
|---|---------|----------|
| 1 | Получил N задач, вернул 0-1 результат | REJECT |
| 2 | Ответ "выполнено" без деталей | REJECT |
| 3 | "done" без доказательств | REJECT |
| 4 | Thin wrapper без value-add | REJECT |
| 5 | Копипаст входных данных | REJECT |
| 6 | Длинный отчёт + нулевой diff | REJECT |
| 7 | "Всё проверил" + нет находок | REJECT |
| 8 | Пустой COMPLETION_CONTRACT | REJECT |

**Pre-Acceptance Checklist:**
```
ARTIFACTS: deliverables соответствуют AC?
SCOPE MATCH: работа в пределах заданного scope?
DEPTH: минимум 5 findings с evidence?
CORE vs PERIPHERAL: затронуты core (rules/agents/skills)?
REPORT RATIO: отчёт пропорционален реальному diff?
ACTION vs META: реальные изменения, не только описание?
COMPLETION: нет "next steps" вместо реальной работы?
RELEVANCE: findings относятся к текущей задаче?
```

**Evidence-first acceptance** ([`docs/evidence-first-acceptance.md`](docs/evidence-first-acceptance.md)):
- Claim-to-evidence matrix для каждого утверждения
- Reviewer checklist с reject при failed checks
- Completion contract с files_changed, checks_run, AC status

### 4.3 Механизмы восстановления после сбоев

**Runtime capability gate** ([`rules/orchestrator.mdc`](rules/orchestrator.mdc:93)):
- `Task` tool доступен → использовать
- Нет → **HARD FAIL**: `MULTI_AGENT_PIPELINE_BLOCKED`
- **ЗАПРЕЩЕНО** при отсутствии `Task` делать работу самому

**Relay-режимы** ([`agents/orchestrator.md`](agents/orchestrator.md:94)):

| Режим | Когда |
|-------|-------|
| `root_task_proxy` | Нет `Task` → wrap запрос в ORCHESTRATOR_RELAY_REQUEST |
| `relay_resume` | Продолжение после предыдущей волны |
| `child_results_return` | Возврат результата дочернего агента вверх |

**VCS pre-flight** ([`docs/autonomous-self-improvement-loop.md`](docs/autonomous-self-improvement-loop.md:39)):
```bash
git fetch --all --prune
git rev-list --left-right --count "origin/${BASE_BRANCH}...HEAD"
git status --short --branch
```

| Состояние | Действие |
|-----------|----------|
| `0 0` (чистое) | Синхронизация через pull --rebase |
| `0 N` (ahead) | Продолжить итерацию |
| `N 0` (behind) | `git rebase origin/${BASE_BRANCH}` |
| `N M` (diverged) | Остановка, эскалация пользователю |
| Грязное дерево | Не выполнять pull/rebase до завершения итерации |

### 4.4 Fallback стратегии

**SINGLE_AGENT_DEGRADED_MODE** — **ЗАПРЕЩЁН** при наличии `Task()`:
- Разрешён ИСКЛЮЧИТЕЛЬНО: явный запрос пользователя + нет `Task()` + не /start/swarm/open-ended
- Обязателен лейбл `SINGLE_AGENT_DEGRADED_MODE`
- Если деградация произошла → **never** continue, немедленно вернуть `blocked`

**Blocker taxonomy** ([`rules/orchestrator.mdc`](rules/orchestrator.mdc:581)):
- `BLOCKED_RUNTIME` — лимиты runtime
- `BLOCKED_POLICY` — нарушение политик
- `BLOCKED_INPUT` — некорректный ввод
- `BLOCKED_EXTERNAL` — недоступность внешних ресурсов
- `BLOCKED_INTEGRATION` — проблемы интеграции

**Web research offline fallback** ([`rules/orchestrator.mdc`](rules/orchestrator.mdc:541)):
- `web_research: not_available` + `blocker_reason` + `residual_risk`
- Никогда не генерировать hallucinated URLs
- При `not_available` → делегировать `security-auditor` для оценки рисков

### 4.5 Thinking Checkpoints

**6 чекпоинтов** ([`skills/thinking-checkpoints/SKILL.md`](skills/thinking-checkpoints/SKILL.md)):

| Чекпоинт | Когда | Цель |
|----------|-------|------|
| **CP-1** | Before Decomposition | Проверка scope, ambiguity score, core files |
| **CP-2** | Before Delegation | Проверка контракта, same-type check |
| **CP-3** | Mid-Execution (3-5 tool calls) | Progress, anti-loop, context usage |
| **CP-4** | Before Synthesis | Все ветки returned?, contradictions |
| **CP-5** | Before Response | Proof, hallucination, contract check |
| **CP-6** | Self-Reflection (complex) | Internal quality rubric |

**Context Check** (встроен в CP-3):
- 10+ tool calls → summarize progress в 3-5 bullets
- Re-reading files → use cached knowledge
- Response длиннее запроса → cut Y and Z
- Near context limit → write state to `.plan/session-context.md`

### 4.6 Human-in-the-loop Gates

**Tier A — Hard stop** ([`skills/human-in-the-loop-gates/SKILL.md`](skills/human-in-the-loop-gates/SKILL.md)):
- Secrets edits, credential rotation
- Destructive VCS/data (force push, rm -rf, DROP)
- DUA **не** override — требуется explicit user confirmation

**STOP packet** (что отправлять пользователю):
- Proposed action
- Risk
- Reversible?
- Exact commands
- Files touched
- Safe alternative (dry-run, diff-only)

---

## 5. МАСШТАБИРУЕМОСТЬ И МОДУЛЬНОСТЬ

### 5.1 Архитектура модульности агентов

**Структура агента** (canonical package):
```
agents/<agent-name>.md    ← Спецификация агента
rules/<agent-name>.mdc    ← Протокол выполнения
skills/<skill-name>/SKILL.md  ← Reusable skill (опционально)
```

**Реестры:**
- [`agents/README.md`](agents/README.md) — реестр агентов
- [`rules/specialists.mdc`](rules/specialists.mdc) — таблица маршрутизации
- [`docs/skills-index.md`](docs/skills-index.md) — реестр skills

**Жизненный цикл агентов:**
- `subagent-factory` — создание/обновление单个 агентов
- `agent-manager` — управление жизненным циклом, RBAC
- `meta-agent-architect` — архитектурные изменения экосистемы

**Решение о новом агенте** ([`agents/meta-agent-architect.md`](agents/meta-agent-architect.md:40)):
- Тип задачи встречается повторяющимся образом
- Существующие агенты требуют избыточного prompt-scaffolding
- Возможность стабильна и имеет рекуррентную ценность
- Перекрытие с существующим агентом минимально

### 5.2 Лимиты Fan-out

| Уровень | Writer-веток | Reader-веток |
|---------|--------------|--------------|
| **L1 Orchestrator** | ≤6 (реструктуризация при >6) | Без лимита |
| **Specialist** | 3+ → escalate к orchestrator | Без лимита |
| **Sub-orchestrator** | 5-7 (split при >7) | Без лимита |

**Динамические параметры** ([`agents/orchestrator.md`](agents/orchestrator.md:73)):

| Параметр | Простая | Средняя | Сложная | Open-ended |
|----------|---------|---------|---------|------------|
| **DEPTH_BUDGET** | 3 | 6 | 10 | 15 |
| **Writer-веток** | 1-2 | 3-4 | 5-7 | 7+ через суб-оркестраторы |
| **Голосов** | 2 (B+V) | 3 (B+S+V) | 4 (B+S+V+E) | 5 (B+S+V+E+Sec) |
| **Rework cycles** | 1 | 2 | 3 | 4 |

**Голоса (Voices):**
- **Builder** — строит решение
- **Skeptic** — оспаривает допущения
- **Verifier** — проверяет AC
- **Explorer** — разведка, web-research
- **Security** — security audit

### 5.3 Механизмы горизонтального масштабирования

**Swarm режим** ([`rules/orchestrator.mdc`](rules/orchestrator.mdc:30)):
- Каждый специалист — локальный мини-оркестратор
- N подзадач → N subagents параллельно
- Каждый может вызывать клонов себя И смежных специалистов

**Mandatory SWARM алгоритм** ([`rules/specialists.mdc`](rules/specialists.mdc:61)):
```
1. Получил задачу от orchestrator
2. Разбей на подзадачи (список todos)
3. Для КАЖДОЙ независимой подзадачи → Task() подходящего агента
4. Запусти ВСЕ независимые Task() ПАРАЛЛЕЛЬНО (один пакет)
5. Дождись результатов и синтезируй
```

**Chunking для больших источников** ([`rules/orchestrator.mdc`](rules/orchestrator.mdc:448)):
- Источник >5MB или >3000 items → обязательный суб-оркестратор + chunking
- Chunks: `ceil(total/3000)`
- Оркестратор НЕ читает data-файлы напрямую

### 5.4 Роль Subagent Factory

**Subagent Factory** ([`skills/subagent-factory/SKILL.md`](skills/subagent-factory/SKILL.md)) — единственное место для создания/обновления агентов:

**Процесс:**
1. Анализ пробела возможностей (overlap check)
2. Спецификация агента (имя, scope, contract)
3. Создание `agents/<name>.md`
4. Создание `rules/<name>.mdc`
5. Опционально: `skills/<name>/SKILL.md`
6. Регистрация в реестрах

**Запреты:**
- Создавать частичные пакеты (без rules.mdc или регистрации)
- Создавать нового агента если существующий можно доработать
- Пропускать проверку на конфликты имён

### 5.5 Swarm режим и его применение

**Swarm** — это режим максимальной параллелизации:

```
Orchestrator получает задачу с 10 независимыми файлами:

❌ НЕЛЬЗЯ — последовательно:
  for file in files:
      Task(code, f"implement: {file}")  # ждём каждый

✅ НУЖНО — параллельный пакет:
  results = [Task(code, f"implement: {f}") for f in files]  # все сразу
```

**Пакетный параллелизм** ([`rules/orchestrator.mdc`](rules/orchestrator.mdc:446)):
- 5+ однотипных независимых задач → ОДИН пакет параллельных `Task`
- Не цикл с ожиданием
- Последовательный запуск независимых веток = баг

---

## 6. ВЫЯВЛЕННЫЕ АРХИТЕКТУРНЫЕ ПРОБЛЕМЫ

### 6.1 Критические проблемы

| # | Проблема | Влияние | Локация |
|---|----------|---------|---------|
| **P1** | Отсутствие `Task` tool на глубине ≥ 2 в Cursor IDE | Блокирует всю цепочку делегирования | Runtime limitation |
| **P2** | Нет подлинной независимости голосов (все голоса = один LLM) | Multi-voice debate может усиливать bias | [`skills/multi-pass-autonomy/SKILL.md`](skills/multi-pass-autonomy/SKILL.md:17) |
| **P3** | OWNERSHIP — логическая гарантия, не enforced runtime | Конфликты записи возможны при ошибках оркестратора | [`docs/autonomous-self-improvement-loop.md`](docs/autonomous-self-improvement-loop.md:190) |

### 6.2 Значительные проблемы

| # | Проблема | Влияние | Локация |
|---|----------|---------|---------|
| **P4** | Нет автоматической валидации контрактов до отправки | Неполные контракты → rework cycles | [`skills/delegation-contracts/SKILL.md`](skills/delegation-contracts/SKILL.md) |
| **P5** | Session memory tiers — ручное управление, нет автоматического eviction | Контекст может распухнуть | [`skills/session-memory-tiers/SKILL.md`](skills/session-memory-tiers/SKILL.md) |
| **P6** | Telemetry contract — target shape, не имплементирован | Нет observability для production | [`docs/agent-telemetry-contract.md`](docs/agent-telemetry-contract.md) |
| **P7** | LLM-as-judge variance — stochastic scores без multiple seeds | Нестабильные eval результаты | [`docs/llm-as-judge-playbook.md`](docs/llm-as-judge-playbook.md:27) |
| **P8** | Web research — offline fallback = blocker + residual risk | Нет graceful degradation | [`rules/orchestrator.mdc`](rules/orchestrator.mdc:541) |

### 6.3 Умеренные проблемы

| # | Проблема | Влияние | Локация |
|---|----------|---------|---------|
| **P9** | DEPTH_BUDGET сбрасывается между волнами | Потеря контекста глубины в 24/7 режиме | [`agents/orchestrator.md`](agents/orchestrator.md:82) |
| **P10** | Нет автоматического discovery специалистов | Orchestrator должен "знать" всех специалистов | [`skills/specialist-discovery/SKILL.md`](skills/specialist-discovery/SKILL.md) |
| **P11** | CAID без git worktrees — логическая изоляция | Нет физической изоляции веток | [`rules/orchestrator.mdc`](rules/orchestrator.mdc:190) |
| **P12** | Ambiguity scoring — субъективная оценка | Разные агенты могут по-разному оценить | [`rules/orchestrator.mdc`](rules/orchestrator.mdc:194) |

### 6.4 Архитектурные узкие места

**1. Orchestrator как single point of decomposition:**
```
start → orchestrator → specialists
         ↑
    Единственный агент декомпозиции
```
- При сложной задаче orchestrator может стать bottleneck
- Нет механизма разделения orchestration load

**2. Flat chain limitation:**
- Worker-start удалён → orchestrator вызывается напрямую
- Это устраняет лишний hop, но означает что orchestrator ВСЕГДА на глубине 1
- Нет возможности иметь orchestrator на глубине 2+ (где `Task` недоступен)

**3. Context window management:**
- При 10+ tool calls требуется manual summarization
- Нет автоматического compaction
- Session memory tiers требуют ручного eviction

**4. Evidence-first overhead:**
- Каждый claim требует evidence_ref
- Для больших задач это создаёт значительный overhead
- Нет автоматического evidence collection

---

## 7. РЕКОМЕНДАЦИИ ПО ОПТИМИЗАЦИИ

### 7.1 Рекомендации по маршрутизации

| # | Рекомендация | Описание | Приоритет |
|---|--------------|----------|-----------|
| **R1** | Автоматическая валидация контрактов | Pre-flight check контракта перед `Task()` — проверка наличия всех mandatory секций | **HIGH** |
| **R2** | Dynamic specialist discovery | Автоматический scan `agents/*.md` для построения routing table вместо hardcoded таблицы | **MEDIUM** |
| **R3** | Cost-aware routing с telemetry | Интеграция agent-telemetry-contract для routing decisions на основе historical cost/performance | **MEDIUM** |
| **R4** | Ambiguity scoring automation | Автоматическая оценка ambiguity по наличию/отсутствию конкретных полей в запросе | **LOW** |

### 7.2 Рекомендации по управлению контекстом

| # | Рекомендация | Описание | Приоритет |
|---|--------------|----------|-----------|
| **R5** | Автоматический context compaction | При 10+ tool calls → автоматический summary + write to session-context | **HIGH** |
| **R6** | Structured context propagation | Передача context_files + completed_branches как часть контракта, не только в промпте | **HIGH** |
| **R7** | Automated eviction policy | Правила eviction на основе размера и age, не manual | **MEDIUM** |
| **R8** | Context window budgeting | Явный budget для context usage в DEPTH_BUDGET | **MEDIUM** |

### 7.3 Рекомендации по отказоустойчивости

| # | Рекомендация | Описание | Приоритет |
|---|--------------|----------|-----------|
| **R9** | Graceful degradation для web research | Вместо `not_available` → cached knowledge base + explicit staleness marker | **HIGH** |
| **R10** | Multiple seed judge evals | Для LLM-as-judge — запуск N trials с reporting mean + spread | **MEDIUM** |
| **R11** | Circuit breaker для specialists | При N consecutive failures → mark specialist as degraded, route to alternative | **MEDIUM** |
| **R12** | Automated evidence collection | Автоматический сбор evidence из tool outputs в completion contract | **LOW** |

### 7.4 Рекомендации по масштабируемости

| # | Рекомендация | Описание | Приоритет |
|---|--------------|----------|-----------|
| **R13** | Sub-orchestrator auto-split | При L1 writer count > 4 → автоматическое предложение sub-orchestrator | **HIGH** |
| **R14** | CAID с git worktrees | Полная CAID-изоляция через `git worktree add` для каждой writer-ветки | **MEDIUM** |
| **R15** | Telemetry implementation | Имплементация agent-telemetry-contract для observability | **HIGH** |
| **R16** | Parallel batch optimization | Автоматическое grouping независимых задач в один batch | **MEDIUM** |

---

## 8. ПРИОРИТИЗАЦИЯ РЕКОМЕНДАЦИЙ

### P0 — Критические (немедленно)

| Рекомендация | Влияние | Усилие |
|--------------|---------|--------|
| **R1** — Автоматическая валидация контрактов | Предотвращает rework cycles от неполных контрактов | Low |
| **R5** — Автоматический context compaction | Предотвращает context overflow при длинных сессиях | Medium |
| **R9** — Graceful degradation для web research | Устраняет blocker при недоступности web | Medium |
| **R13** — Sub-orchestrator auto-split | Предотвращает OWNERSHIP конфликты при большом fan-out | Medium |
| **R15** — Telemetry implementation | Даёт observability для всех остальных оптимизаций | High |

### P1 — Значительные (следующая итерация)

| Рекомендация | Влияние | Усилие |
|--------------|---------|--------|
| **R2** — Dynamic specialist discovery | Устраняет необходимость manual routing table updates | Medium |
| **R6** — Structured context propagation | Улучшает консистентность контекста между агентами | Medium |
| **R7** — Automated eviction policy | Предотвращает context bloat | Low |
| **R10** — Multiple seed judge evals | Стабилизирует eval результаты | Low |
| **R11** — Circuit breaker для specialists | Улучшает отказоустойчивость маршрутизации | Medium |
| **R14** — CAID с git worktrees | Даёт физическую изоляцию веток | High |
| **R16** — Parallel batch optimization | Улучшает throughput | Medium |

### P2 — Умеренные (долгосрочный backlog)

| Рекомендация | Влияние | Усилие |
|--------------|---------|--------|
| **R3** — Cost-aware routing с telemetry | Оптимизирует cost/performance | High (зависит от R15) |
| **R4** — Ambiguity scoring automation | Устраняет субъективность | Medium |
| **R8** — Context window budgeting | Fine-grained control context usage | Medium |
| **R12** — Automated evidence collection | Reduces overhead | Medium |

---

## ПРИЛОЖЕНИЕ A: Схемы взаимодействия

### A.1 Полная цепочка делегирования

```
┌─────────────────────────────────────────────────────────────────┐
│                        USER REQUEST                             │
│                    /start "улучши систему"                       │
└────────────────────────────┬────────────────────────────────────┘
                             │
                    ┌────────▼────────┐
                    │   root-start    │  ← FIRST_ACTION GATE
                    │   (supervisor)  │     НОЛЬ tool calls до Task(orchestrator)
                    │                 │     CONTINUOUS_MODE: until_user_stop?
                    │                 │     OPEN_ENDED_IMPROVEMENT: yes?
                    └────────┬────────┘
                             │
                    Task(orchestrator, prompt="
                      OBJECTIVE: улучшить систему
                      ORIGINAL_REQUEST: {дословно}
                      CONTINUOUS_MODE: until_user_stop
                      OPEN_ENDED_IMPROVEMENT: yes
                      WAVE_NUMBER: 1
                      DEPTH_BUDGET: 15
                    ")
                             │
                    ┌────────▼────────┐
                    │   orchestrator  │  ← B0 supervisor
                    │    (root)       │     CP-1: Before Decomposition
                    │                 │     Фаза 0: State Map
                    │                 │     Фаза 1: Конверт исполнения
                    │                 │     Фаза 2: Pre-Delegation Check
                    └────────┬────────┘
                             │
              ┌──────────────┼──────────────┐
              │              │              │
     ┌────────▼────┐ ┌──────▼──────┐ ┌─────▼──────┐
     │ B0-1: code  │ │ B0-2: test  │ │ B0-3: sec  │
     │ Builder     │ │ Verifier    │ │ Reader     │
     │ OWNERSHIP:  │ │ OWNERSHIP:  │ │ OWNERSHIP: │
     │ src/**      │ │ tests/**    │ │ ALL (read) │
     │ DEPENDENCIES│ │ after:B0-1  │ │ none       │
     │ none        │ │             │ │            │
     └────────┬────┘ └──────┬──────┘ └─────┬──────┘
              │              │              │
              │       ┌──────▼──────┐       │
              │       │ B0-2-1:     │       │
              │       │ sub-orch    │       │
              │       │ DEPTH: 5    │       │
              │       └──────┬──────┘       │
              │              │              │
              └──────────────┼──────────────┘
                             │
                    ┌────────▼────────┐
                    │   SYNTHESIS     │  ← CP-4: Before Synthesis
                    │   (orchestrator)│     coverage_ratio ≥ 0.95
                    │                 │     CAID: git commit per branch
                    │                 │     Agent Council для high-risk
                    └────────┬────────┘
                             │
                    COMPLETION_CONTRACT:
                      status: done
                      files_changed: [...]
                      checks: [...]
                      AC status: [...]
                      next_packet: {...}
                             │
                    ┌────────▼────────┐
                    │   root-start    │  ← Анализ START_REPORT
                    │                 │     24/7: Волна 2?
                    │                 │     OPEN_ENDED: next gap?
                    └─────────────────┘
```

### A.2 Fan-out/Fan-in паттерн

```
                    ┌─────────────┐
                    │ Orchestrator│
                    │   (B0)      │
                    └──────┬──────┘
                           │
              ┌────────────┼────────────┐
              │            │            │
     ┌────────▼───┐ ┌─────▼────┐ ┌─────▼────┐
     │ B0-1       │ │ B0-2     │ │ B0-3     │
     │ code       │ │ docs     │ │ review   │
     │ (writer)   │ │ (writer) │ │ (reader) │
     │ parallel   │ │ parallel │ │ parallel │
     └─────┬──────┘ └────┬─────┘ └────┬─────┘
           │              │            │
           │              │            │
     ┌─────▼──────────────▼────────────▼─────┐
     │          FAN-IN (Synthesis)            │
     │ 1. Собрать все COMPLETION_CONTRACT     │
     │ 2. Проверить coverage_ratio ≥ 0.95     │
     │ 3. CAID git attribution                │
     │ 4. Agent Council для high-risk         │
     │ 5. Вернуть родителю                    │
     └────────────────────────────────────────┘
```

### A.3 DAG зависимостей веток

```
         B0 (root)
          │
    ┌─────┼─────┐
    │     │     │
   B0-1  B0-2  B0-3
   (none) (none) (none)
    │     │      │
    │     │     B0-4 (after:B0-1)
    │     │      │
   B0-5 (after:B0-1, B0-2)
    │
   B0-6 (after:B0-5)

Топологический порядок:
Wave 1: B0-1, B0-2, B0-3 (parallel, none)
Wave 2: B0-4 (after B0-1 done), B0-5 (after B0-1, B0-2 done)
Wave 3: B0-6 (after B0-5 done)
```

### A.4 Session Memory Tiers

```
┌─────────────────────────────────────────────────────────┐
│                    Ephemeral (RAM)                       │
│  Сырые tool outputs, промежуточные результаты            │
│  TTL: до конца хода                                      │
└────────────────────────┬────────────────────────────────┘
                         │ compaction
                         ▼
┌─────────────────────────────────────────────────────────┐
│                    Session (Chat)                        │
│  Решения веток, blockers, ссылки на артефакты            │
│  TTL: длительность сессии IDE                            │
└────────────────────────┬────────────────────────────────┘
                         │ summarization
                         ▼
┌─────────────────────────────────────────────────────────┐
│                 Project (.plan/)                         │
│  session-context.md, todos.md, session-context.md        │
│  TTL: живёт с репозиторием                               │
└────────────────────────┬────────────────────────────────┘
                         │ versioning
                         ▼
┌─────────────────────────────────────────────────────────┐
│              Persistent Policy (rules/)                  │
│  *.mdc, skills/, CI pipelines                            │
│  TTL: версионируется, изменения через PR + eval gate     │
└─────────────────────────────────────────────────────────┘
```

---

## ПРИЛОЖЕНИЕ B: Глоссарий терминов

| Термин | Определение |
|--------|-------------|
| **DUA** | Direct User Authorization — императивный глагол / slash-команда, снимающая блок перед исполнением |
| **FIRST_ACTION GATE** | Обязательный первый tool call root-start = Task(orchestrator), ноль tool calls до него |
| **Flat chain** | Уплощённая цепочка: root-start → orchestrator напрямую, без worker-start |
| **COMPLETION_CONTRACT** | Структурированный YAML-блок с доказательствами выполнения ветки |
| **OWNERSHIP** | Эксклюзивный набор файлов/глобов для writer-ветки |
| **DEPENDENCIES** | DAG-зависимости: `none`, `after:Bx`, `blocked-by:By` |
| **DEPTH_BUDGET** | Бюджет глубины делегирования: 3/6/10/15 по сложности |
| **Rework cycles** | Счётчик циклов переделки; при достижении лимита → blocked |
| **Fingerprint** | `goal + target-files + AC + agent_type + level` для anti-loop |
| **CAID** | CMU Attribution Isolation and Diff — паттерн git attribution per branch |
| **B0 supervisor** | Корневой orchestrator с Branch ID B0 |
| **Writer-ветка** | Ветка, изменяющая файлы (code, docs, etc.) |
| **Reader-ветка** | Ветка, только анализирующая (review, security audit) |
| **Swarm** | Режим максимальной параллелизации через Task() |
| **Trust boundary** | `TRUSTED_POLICY > TASK_INPUT > UNTRUSTED_EXTERNAL` |
| **Agent Council** | Multiple parallel ветки с разными подходами + judge |
| **Thinking Checkpoints** | 6 mandatory STOP-and-think gates (CP-1 через CP-6) |
| **Evidence-first** | Каждый claim требует evidence_ref |
| **24/7 mode** | `CONTINUOUS_MODE: until_user_stop` — цикл волн |
| **Open-ended** | `OPEN_ENDED_IMPROVEMENT: yes` — бесконечный поиск улучшений |

---

## ПРИЛОЖЕНИЕ C: Матрица покрытия документов

| Документ | Покрытые аспекты |
|----------|-----------------|
| [`rules/orchestrator.mdc`](rules/orchestrator.mdc) | Протокол оркестрации, anti-loop, quality gates, trust boundary |
| [`rules/specialists.mdc`](rules/specialists.mdc) | Маршрутизация, swarm, runtime gates |
| [`agents/start.md`](agents/start.md) | Точка входа, FIRST_ACTION, 24/7 loop |
| [`agents/orchestrator.md`](agents/orchestrator.md) | Декомпозиция, шаблоны, voices, relay |
| [`skills/delegation-contracts/SKILL.md`](skills/delegation-contracts/SKILL.md) | Шаблоны контрактов, fingerprint, relay |
| [`skills/budget-orchestration/SKILL.md`](skills/budget-orchestration/SKILL.md) | Бюджетирование, chunking, parallelism |
| [`skills/session-memory-tiers/SKILL.md`](skills/session-memory-tiers/SKILL.md) | Уровни памяти, eviction, PII |
| [`skills/thinking-checkpoints/SKILL.md`](skills/thinking-checkpoints/SKILL.md) | 6 чекпоинтов, context check |
| [`skills/human-in-the-loop-gates/SKILL.md`](skills/human-in-the-loop-gates/SKILL.md) | Hard stop gates, STOP packet |
| [`skills/subagent-factory/SKILL.md`](skills/subagent-factory/SKILL.md) | Создание агентов, lifecycle |
| [`docs/delegation-chain.md`](docs/delegation-chain.md) | Цепочка делегирования, allowed/forbidden |
| [`docs/start-workflow.md`](docs/start-workflow.md) | Runbook для /start |
| [`docs/dag-branch-dependencies.md`](docs/dag-branch-dependencies.md) | DAG зависимостей, rework limits |
| [`docs/evidence-first-acceptance.md`](docs/evidence-first-acceptance.md) | Claim-to-evidence matrix |
| [`docs/autonomous-self-improvement-loop.md`](docs/autonomous-self-improvement-loop.md) | Спираль самоулучшения |
| [`docs/security-governance-checklist.md`](docs/security-governance-checklist.md) | Trust boundary, injection guardrails |
| [`docs/agent-telemetry-contract.md`](docs/agent-telemetry-contract.md) | Telemetry schema (target) |
| [`docs/model-routing.md`](docs/model-routing.md) | Fast vs capable tiers |
| [`docs/llm-as-judge-playbook.md`](docs/llm-as-judge-playbook.md) | Rubric-first eval |

---

*Отчёт сформирован на основе анализа 40+ архитектурных документов системы. Код tg_bot/ не анализировался и не модифицировался.*

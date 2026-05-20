---
name: delegation-contracts
description: Шаблоны OBJECTIVE/SCOPE/OWNERSHIP/DEPENDENCIES/AC/COMPLETION_CONTRACT, anti-loop, fingerprint, relay; согласованность с оркестратором.
---

## ЦЕЛЬ

Обеспечить повторяемый, проверяемый конверт для любого `Task(...)` / `Task(...)`: однозначный scope, изоляция владения файлами, явные зависимости между ветками и завершаемый completion contract. Согласовать терминологию с каноническими правилами и документами цепочки делегирования.

## КОГДА ИСПОЛЬЗОВАТЬ

- Перед отправкой пакета задач оркестратору или специалисту
- При разбиении работы на параллельные writer-ветки (disjoint OWNERSHIP)
- После эскалации «неясный AC» или «scope creep»
- При настройке relay / handoff между уровнями агентов (см. delegation-chain)

## КАНОНИЧЕСКИЕ ССЫЛКИ

- Полный протокол и запреты супервизора: **`rules/orchestrator.mdc`**
- Семантика `/start`, relay, цепочка root → worker → orchestrator: **`docs/delegation-chain.md`**, **`docs/start-workflow.md`**
- Минимальные поля промпта: **`skills/agent-prompt-quality/SKILL.md`**

## ШАБЛОНЫ СЕКЦИЙ

### OBJECTIVE

Одно предложение, измеримый результат для **этой** ветки (не «улучшить всё»).

```text
OBJECTIVE: <глагол + объект + критерий готовности одной фразой>
```

### SCOPE / OUT_OF_SCOPE

```text
SCOPE: <явные пути, компоненты, типы артефактов>
OUT_OF_SCOPE: <соседние модули, массовый рефакторинг, изменение политик без явного запроса>
```

### OWNERSHIP

Исключительные glob/файлы ветки. Для параллельных writer-веток множества OWNERSHIP **не пересекаются**.

```text
OWNERSHIP: <path-or-glob-1>, <path-or-glob-2>
```

### DEPENDENCIES

```text
DEPENDENCIES: none | after:B0-2 | blocked-by:B0-3
```

### ACCEPTANCE_CRITERIA

Только наблюдаемые проверки: команда, файл, diff, тест. Избегать «качественно» без метрики.

```text
ACCEPTANCE_CRITERIA:
- [ ] <команда или артефакт + ожидаемый результат>
- [ ] ...
```

### COMPLETION_CONTRACT

YAML- или структурированный блок в конце ответа исполнителя (см. evidence schema в `rules/orchestrator.mdc` §5):

```yaml
branch_id: <id>
status: approval|pause|blocked|resume
approval_state: not_required|requested|approved|rejected
execution_state: in_progress|paused|done|rework|blocked|aborted
files_changed: [<path>]
checks:
  - name: <command>
    result: pass|fail|not_run
    evidence: <кратко>
acceptance_criteria:
  - criterion: <text>
    status: met|not_met
confidence: high|medium|low
unknowns: [none | <вопрос>]
```

### NON-NEGOTIABLE

Должно содержать **`PENALIZED`** (keyword gate оркестратора).

```text
NON-NEGOTIABLE:
- You will be PENALIZED for skipping steps
- NEVER say done without listing changes + evidence
```

## Contract Validation Checklist

### Pre-flight (вход — проверяет orchestrator перед Task()):
- [ ] OBJECTIVE: одно предложение, измеримый результат
- [ ] SCOPE: границы явно определены, что ВКЛЮЧЕНО и что ИСКЛЮЧЕНО
- [ ] OWNERSHIP: один владелец (agent name), нет shared ownership
- [ ] DEPENDENCIES: список зависимостей или "none"
- [ ] Acceptance Criteria: конкретные, проверяемые условия
- [ ] NON-NEGOTIABLE: если содержит "PENALIZED" — агент обязан выполнить
- [ ] COMPLETION_CONTRACT: все 7 полей заполнены (evidence, scope_met, ac_verified, non_negotiable_met, risks, next_steps, confidence)

### Post-flight (выход — проверяет orchestrator при получении результата):
- [ ] evidence: конкретные файлы/строки/артефакты
- [ ] scope_met: true/false с обоснованием
- [ ] ac_verified: true/false с проверкой каждого AC
- [ ] non_negotiable_met: true/false, если было — подтверждение
- [ ] risks: список или "none"
- [ ] next_steps: конкретные действия или "complete"
- [ ] confidence: 0.0-1.0 с обоснованием

### INVALID контракт → REJECT с указанием конкретных нарушенных полей

## ANTI-LOOP И FINGERPRINT

**Fingerprint ветки** (для дедупликации и лимита глубины):

`goal + target-files + AC + agent_type + level`

Правила из `rules/orchestrator.mdc`:

- Same-type делегирование только если дочерний контракт **строже** родительского (уже scope, уже файлы, жёстче AC).
- Мягкий лимит глубины same-type цепочки: **3 уровня** — далее re-plan или эскалация к orchestrator.
- **Writer fan-out ≥ 3** от одного специалиста → эскалация к orchestrator. **Reader-ветки** (code-reviewer, security-auditor, ask, repo-explorer, code-skeptic) — **без лимита**, не считаются для порога эскалации.
- Специалист может делегировать **любому подходящему агенту** (не только клонам): code → test-specialist, docs-specialist, frontend-specialist и т.д.
- Счётчик **rework_cycles**: при `rework_cycles >= rework_limit` → `status: blocked`, `escalate_reason: rework_limit_exceeded`, не продолжать слепо.

## RELAY (КРАТКИЕ ЗАМЕТКИ)

- Relay допустим как **транспорт** точного пакета дочерних `Task` + `resume`, без принятия решений на стороне relay.
- Если дочерний субагент возвращает `ORCHESTRATOR_RELAY_REQUEST`, родитель проксирует **конкретные** payloads, не «пересказывает» устно.
- При недоступности `Task` / Task — не эмулировать оркестрацию в одиночку: зафиксировать blocker (`rules/orchestrator.mdc` §0.5).

## ШАГИ

1. Прочитать актуальные требования в `rules/orchestrator.mdc` (completeness gate §3) и `docs/delegation-chain.md` для вашего режима (root vs nested).
2. Назначить **Branch ID** в формате `B{parent}-{N}` (корень `B0`).
3. Заполнить шаблон секций; проверить OWENRSHIP на пересечения с соседними ветками.
4. Задать `DEPENDENCIES` и порядок синтеза; независимые ветки планировать **параллельным пакетом** Task.
5. После выполнения — заполнить COMPLETION_CONTRACT с evidence; верификатор сверяет AC, не доверяет голому «done».

## ЧЕКЛИСТ

- [ ] Все обязательные секции конверта присутствуют (см. `agent-prompt-quality`)
- [ ] OWNERSHIP disjoint для параллельных writers
- [ ] AC измеримы; есть чек или артефакт
- [ ] NON-NEGOTIABLE содержит `PENALIZED`
- [ ] Fingerprint ветки возможно вычислить однозначно
- [ ] Relay, если используется — только транспорт пакета, без решений
- [ ] При rework исчерпан лимит — эскалация, не бесконечный цикл
- [ ] Терминология согласована с `docs/delegation-chain.md` и `docs/start-workflow.md`

## СВЯЗАННЫЕ ДОКУМЕНТЫ

- **`rules/orchestrator.mdc`** — completeness gate, parallel writer safety, proof-of-delegation
- **`docs/delegation-chain.md`** — детальная цепочка и relay
- **`docs/evidence-first-acceptance.md`** — матрица claim/evidence для приёмки
- См. реестр: `docs/skills-index.md` (forward ref)
- Смежно: `skills/structured-policy-yaml/SKILL.md` для машиночитаемых фрагментов политики в задачах

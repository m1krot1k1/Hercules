---
name: start-workflow
description: "Когда и как использовать /start: архитектура, паттерны, интеграция с orchestrator."
---

## ЦЕЛЬ

Инициировать долгосрочную сессию через правильную цепочку делегирования.

## КОГДА ИСПОЛЬЗОВАТЬ

| Использовать | Не использовать |
|---|---|
| Новый проект / PBI | Одиночная быстрая задача |
| Несколько доменов | Простой вопрос |
| Нужен .plan/ | Уже есть активный plan |
| 24/7 / continuous mode | Одноразовая правка |

## АРХИТЕКТУРА (УПЛОЩЁННАЯ ЦЕПОЧКА)

> **ВАЖНО**: Worker-start УДАЛЁН из активной `/start`-цепочки.
> Канонический вход теперь flat-chain: root-start вызывает orchestrator НАПРЯМУЮ.
> `Task()` при этом доступен вложенным subagent'ам; ограничения задаются ролью и правилами, а не глубиной как таковой.

```
/start (root supervisor)
   └→ Task(orchestrator, ORIGINAL_REQUEST: {...})  ← ПЕРВЫЙ И ЕДИНСТВЕННЫЙ tool call
        ├→ Task(code, ...)
        ├→ Task(test-specialist, ...)
        ├→ Task(security-auditor, ...)
        └→ Task(orchestrator, ...)  ← sub-orchestrators для сложных задач
```

### FIRST_ACTION Gate (КРИТИЧЕСКИ ВАЖНО)

- Root-start: **НОЛЬ tool calls** до спавна orchestrator
- Первый tool call = `Task(orchestrator, ORIGINAL_REQUEST: {дословный текст})`
- До этого ЗАПРЕЩЕНО: Read, Write, Grep, Shell, SemanticSearch, Task(start)
- `ORIGINAL_REQUEST` = **дословный текст пользователя** — ЗАПРЕЩЕНО менять

### Запрещённые паттерны

| Паттерн | Почему запрещён |
|---|---|
| `Task(start, ENTRY_MODE: supervised_worker)` | Legacy hop: нарушает flat-chain и размывает ответственность root-start |
| Root-start → Read/Write → Task(start, "acknowledge") | Фейковая делегация |
| "Нет Task — выполняем напрямую" | SINGLE_AGENT_FALLBACK запрещён |

## РЕЖИМЫ

| Режим | Триггер | Поведение |
|---|---|---|
| `single_wave` | по умолчанию | Одна волна → результат |
| `until_user_stop` | "24/7", "непрерывно", "пока не скажу стоп", "/swarm" | Цикл волн |
| `OPEN_ENDED_IMPROVEMENT` | "улучши всё", "найди все проблемы" | Бесконечный поиск |

### 24/7 Loop (root-start)

При `until_user_stop` root-start запускает `Task(orchestrator)` для каждой волны:
```
Волна 1: Task(orchestrator, WAVE_NUMBER: 1) → результат
Волна 2: Task(orchestrator, WAVE_NUMBER: 2) → результат  ← ОБЯЗАТЕЛЬНО!
```

## TROUBLESHOOTING

| Проблема | Решение |
|---|---|
| start читает файлы сам | **НАРУШЕНИЕ** — только Task(orchestrator) |
| В цепочке появился worker-start | **Legacy drift** — вернуться к `root-start → Task(orchestrator)` |
| Orchestrator не вызван | **НАРУШЕНИЕ** — FIRST_ACTION = Task(orchestrator) |
| 24/7 не пошла волна 2 | Проверить loop в root-start — ОБЯЗАН запускать следующую волну |
| Specialist делает всё сам | **НАРУШЕНИЕ** — Mandatory SWARM: Task() для каждой подзадачи |

## ЧЕКЛИСТ

- [ ] FIRST_ACTION: первый tool call = Task(orchestrator)
- [ ] ORIGINAL_REQUEST содержит дословный текст пользователя
- [ ] CONTINUOUS_MODE определён корректно (24/7 → until_user_stop)
- [ ] Orchestrator декомпозировал на параллельные ветки
- [ ] Specialists используют Task() для подзадач (Mandatory SWARM)
- [ ] 24/7: root-start запускает следующую волну после каждой

# Profile: msnmp — Penetration Testing Specialists

Профиль `msnmp` добавляет специализированный pipeline для penetration testing / network security задач.

## Назначение

Этот профиль предназначен для работы с репозиториями/проектами, где требуется:
- разведка и сканирование сети (SNMP, TCP/UDP enumeration)
- анализ уязвимостей конкретных протоколов
- оркестрация pentest-инструментов через агентную систему

## Что добавляет профиль

```text
profiles/msnmp/
├── agents/
│   └── pentest-pipeline.md    # Агент: оркестрация pentest-задач
└── rules/
    └── pentest-pipeline.mdc   # Правила: ограничения и контракты pentest-режима
```

### `pentest-pipeline` агент
Специалист по: SNMP enumeration, network scanning, CVE mapping, отчётам об уязвимостях. Работает **только** в явно авторизованных пентестах.

### `pentest-pipeline` правила
Устанавливают жёсткие ограничения: агент действует только при наличии явного письменного разрешения (`DUA = explicit written authorization`), запрещают использование вне sandbox/lab-окружения.

## Как активировать профиль в проекте

1. Скопировать агента в runtime `.cursor/agents/`:
   ```bash
   cp profiles/msnmp/agents/pentest-pipeline.md .cursor/agents/
   ```
2. Скопировать правила в runtime `.cursor/rules/`:
   ```bash
   cp profiles/msnmp/rules/pentest-pipeline.mdc .cursor/rules/
   ```
3. После работы — **удалить** из `.cursor/` для изоляции от core-системы.

## Ограничения и изоляция

- `pentest-pipeline.md` **не** добавляется в `agents/` (core-реестр) — только в profile-subtree.
- `pentest-pipeline.mdc` **не** добавляется в `rules/` (core-правила) — только в profile-subtree.
- Срабатывание контракта `profile_isolation_enforced` в `benchmarks/behavior-contracts.json` нарушается, если эти файлы окажутся в core.
- Профиль несовместим с использованием за пределами явно авторизованных тестов.

## Совместимость

Совместим с любой конфигурацией core-агентов (33 agents). Профиль работает поверх orchestrator и code-агентов, расширяя их pentest-контекстом.

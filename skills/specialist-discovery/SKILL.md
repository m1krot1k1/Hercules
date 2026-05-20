---
name: specialist-discovery
description: Таблица субагентов и условия их выбора.
---

## ЦЕЛЬ

Быстро найти нужного субагента для делегирования.

## ТАБЛИЦА СУБАГЕНТОВ

| Задача | Агент |
|--------|-------|
| Архитектурное решение / ADR | `@architect` |
| Дизайн агентов и rules | `@agent-architect` |
| Написание / рефакторинг кода | `@code` |
| Ревью PR / кода | `@code-reviewer` |
| Диагностика бага | `@bug-triage` |
| Отладка / root cause analysis | `@debug` |
| Формальный git-diff review | `@review` |
| Стресс-тест плана / верификация | `@code-skeptic` |
| Управление агентами экосистемы | `@agent-manager` |
| Тест-стратегия, тесты | `@test-specialist` |
| REST/gRPC контракты | `@api-designer` |
| Схемы БД, миграции | `@database-specialist` |
| CI/CD, инфраструктура | `@devops-specialist` |
| UI/UX, компоненты | `@frontend-specialist` |
| iOS / Android | `@mobile-specialist` |
| Данные, метрики, EDA | `@data-analyst` |
| Исследование кодовой базы | `@repo-explorer` |
| OWASP, CVE, threat model | `@security-auditor` |
| Latency, CPU, память | `@performance-optimizer` |
| Снижение сложности | `@code-simplifier` |
| README, ADR, CHANGELOG | `@docs-specialist` |
| Changelog, release notes | `@release-manager` |
| Observability, алерты | `@monitoring-specialist` |
| API / сторонние провайдеры | `@provider-integrator` |
| Управление профилями | `@profile-manager` |
| Новые агенты | `@meta-agent-architect` |
| Сборка агентных пакетов | `@subagent-factory` |
| Обновление *.mdc правил | `@rules-specialist` |
| Создание / обновление SKILL.md | `@skills-specialist` |
| Контракты поведения, бенчмарки | `@benchmark-specialist` |
| Уточнить задачу | `@ask` |
| Долгосрочный план / PBI | `@start` |

## ДОПОЛНИТЕЛЬНО

- Профили пользователей: `profiles/<name>/`  применять автоматически при наличии
- Неизвестный агент  `@repo-explorer` для поиска, затем `@agent-architect` для создания

---
name: dynamic-discovery
description: Dynamic specialist discovery based on capability index and historical performance
---

# Dynamic Discovery

## Purpose
Автоматическое обнаружение и маршрутизация к специалистам на основе актуального индекса возможностей и исторической производительности.

## Specialist Index

### Format
```yaml
specialists:
  - name: code
    file: agents/code.md
    keywords: [implementation, coding, development, refactoring]
    cost_tier: 2          # 1=cheap, 2=medium, 3=expensive
    success_rate: 0.95    # обновляется из telemetry
    avg_duration_ms: 45000
    total_tasks: 150
    last_active: "2026-04-04T10:00:00Z"
```

### Scoring Algorithm
```
score(specialist, task) = 
  keyword_match * 0.4 +
  success_rate * 0.3 +
  (1 - cost_tier/3) * 0.15 +
  recency_factor * 0.15

where:
  keyword_match = overlap(task_keywords, specialist.keywords) / len(task_keywords)
  recency_factor = 1.0 if last_active < 24h else 0.5
```

### Discovery Process
1. Scan agents/*.md для актуального списка
2. Извлечь keywords из frontmatter
3. Рассчитать score для каждого кандидата
4. Выбрать top-N (default N=3)
5. Предложить orchestrator для финального выбора

### Auto-Update
- success_rate обновляется после каждого task.completed
- last_active обновляется при каждом вызове
- Индекс пересчитывается каждые 100 задач или 1 час

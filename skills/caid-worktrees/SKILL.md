---
name: caid-worktrees
description: Concurrent Agent Isolation via git worktrees per delegation branch
---

# CAID Worktrees

## Purpose
Изоляция параллельных задач через git worktrees для предотвращения конфликтов и обеспечения атомарного коммита.

## Workflow

### 1. Branch Creation
```
Root task → create main branch: task/{trace_id}
Each delegation branch → create worktree: worktrees/{branch_id}
```

### 2. Isolation
- Каждый агент работает в своём worktree
- Нет доступа к файлам других агентов
- Конфликты обнаруживаются при merge

### 3. Diff Collection
- После завершения ветки → collect diff
- Diff добавляется в evidence контракта
- Формат: unified diff с контекстом

### 4. Synthesis & Merge
- Orchestrator synthesizes результаты и выбирает порядок интеграции
- Sequential merge выполняет delegated git-ветка или `devops-specialist`, не orchestrator напрямую
- При конфликте → delegated merge branch resolve или escalate

### 5. Cleanup
- После успешного merge → delete worktree
- При abort → delete branch + worktree

## Configuration
```yaml
caid:
  worktree_base_dir: ".caid/worktrees"
  branch_prefix: "task/"
  max_concurrent_worktrees: 6
  auto_cleanup: true
  merge_strategy: "sequential"  # sequential | parallel
```

## Benefits
- Полная изоляция параллельных задач
- Атомарный коммит результатов
- Возможность rollback через git
- Audit trail через git history

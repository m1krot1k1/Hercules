---
name: budget-orchestration
description: Plan and enforce orchestration budgets—max_parallel, rework_limit, DEPTH_BUDGET, and chunking thresholds (3000 items / 5MB)—using canonical rules as the single source of truth.
---

## OVERVIEW

Keep multi-branch work **bounded and cheap**: explicit limits on parallelism, recursion depth, rework cycles, and source size before delegation. **Canonical numeric gates and anti-patterns** live in `rules/orchestrator.mdc`; this skill tells you **what to extract** and **how to declare** budgets in task packets—without copying the full rule file.

## КОГДА ИСПОЛЬЗОВАТЬ

- Authoring or reviewing `Task(...)` / orchestration packets
- Flat writer fan-out is growing (>6 L1 writer children) or same-type depth is unclear
- Source material may exceed **~3000 items** or **~5MB** (requires chunking / sub-orchestrator)

## WORKFLOW

### Шаг 1: Declare recursion and rework budgets

1. From `rules/orchestrator.mdc`: use **§0** (depth cap / `DEPTH_BUDGET` vs default depth), **§1** (`rework_limit`, `target_depth`, `max_parallel` in task contracts), and **§8** (chain verification—stop after rework limit).
2. In the task envelope, set explicit fields: `max_parallel`, `rework_limit`, `target_depth` or `DEPTH_BUDGET` per parent instructions. If open-ended mode applies, use the rule's note on higher `DEPTH_BUDGET`—see §0 CONF-FIX.
3. Each branch owns a `rework_cycles` counter; at limit return `blocked` + `rework_limit_exceeded`—see **§1 ENFORCE** and **§8**.

### Шаг 2: Size-aware chunking (3000 / 5MB)

1. Apply **§12** chunking: sources **>3000 items** or **>5MB** require sub-orchestrator + chunks (`ceil(total/3000)` chunks); do not dump wholesale into one branch.
2. Phase 0–1 pipeline and "large source" behavior: **§12** five-phase pipeline and **§12** structural pre-flight (`BRANCH COUNT`, `CHUNKING PLAN`).
3. Reader protocol for huge artifacts: prefer terminal slicing / ranged reads as required by workspace rules—do not inflate every chunk into the model at once.

### Шаг 3: Parallelism vs restructuring

1. Independent branches: **one batch** of parallel `Task` / Task calls—**§12** ("ПАРАЛЛЕЛИЗМ — ОБЯЗАТЕЛЕН"); sequential fan-out for independent work is a bug.
2. If **L1 writer fan-out > 6**: **§0** / **§12** hierarchical enforcement—restructure with sub-orchestrators before executing. **Reader-branches** (code-reviewer, security-auditor, ask, repo-explorer, code-skeptic, review, benchmark-specialist) are **exempt** from this limit.
3. **Writer fan-out ≥ 3** from any specialist: escalate to orchestrator for OWNERSHIP management—**§3** delegation rules. Reader-branches — no limit.
4. Specialists may delegate to **any suitable agent type** (not only same-type clones): code → test-specialist, frontend-specialist, docs-specialist, etc. Count only writer-branches for escalation threshold.

## CHECKLIST

- [ ] Task lists `max_parallel`, `rework_limit`, and depth/debt fields where applicable
- [ ] Source size assessed; chunking plan present if over §12 thresholds
- [ ] L1 **writer** branch count ≤ 6 or explicitly sub-orchestrated per §0/§12 (reader branches exempt)
- [ ] Independent branches launched as one parallel batch, not a serial loop
- [ ] Specialist delegation uses domain-fit agents, not only same-type clones

---
name: caid-ownership-matrix
description: Parallel writer safety under CAID-style attribution—disjoint OWNERSHIP sets, branch metadata, and devops-specialist commit pattern per orchestrator rules.
---

## OVERVIEW

When multiple branches write files concurrently, **overlap is a merge and audit hazard**. `rules/orchestrator.mdc` **§3** (Parallel writer safety: disjoint OWNERSHIP, exclusive globs) and **§1.3** (CAID git attribution at branch completion) define the canonical rules. This skill operationalizes a simple **ownership matrix** and commit ceremony—without restating the full §1.3 text.

## КОГДА ИСПОЛЬЗОВАТЬ

- Orchestrator plans **2+ writer branches** in one wave
- Builders need clear **file/glob exclusive** assignments before execution
- You need post-branch **git attribution** commits per branch

## WORKFLOW

### Шаг 1: Build the OWNERSHIP matrix before execution

1. For each branch: list **exclusive** `OWNERSHIP` as exact paths or globs. Cross-check pairwise intersection; if any overlap → split scope or serialize—**§3** Parallel writer safety.
2. Record `Branch ID` (see **§16** phase-tree IDs, e.g. `B0-1`), parent, level, dependencies.
3. Flag **reader-only** branches (review/security): they should not claim write OWNERSHIP—**§1.3** notes reader branches do not do attribution commits for writes they did not make.

### Шаг 2: Execute writes strictly inside OWNERSHIP

1. Writers refuse out-of-scope paths; escalations go to orchestrator for re-planning—**§3**.
2. **3+ parallel writer-branches** (any agent type that modifies files): escalate to orchestrator per **§3** for OWNERSHIP management. **Reader-branches** (code-reviewer, security-auditor, ask, repo-explorer) are exempt — unlimited parallel fan-out. See **`skills/budget-orchestration/SKILL.md`**.
3. On conflict at commit time: run `git status`, resolve **overlap** before any CAID commit—**§1.3** conflict note.

### Шаг 3: CAID commit via devops-specialist pattern

1. After a writer branch completes, **`devops-specialist`** (or policy-approved commit actor) stages **only** files from that branch’s OWNERSHIP contract.
2. Commit message template from **§1.3**: `[{branch_id}] {objective} — agent:{owner}`.
3. Synthesis wave close: optional aggregate commit per **§1.3** (`[synthesis] wave-N complete — …`) when policy calls for it.

## CHECKLIST

- [ ] Pairwise disjoint OWNERSHIP verified for all parallel writers
- [ ] Branch ID + owner recorded for each writer branch
- [ ] No reader branch forced into writer CAID commit
- [ ] Staged files ⊆ OWNERSHIP before CAID commit

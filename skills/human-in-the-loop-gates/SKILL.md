---
name: human-in-the-loop-gates
description: Mandatory STOP and user escalation before irreversible or high-privilege actions—secrets edits, deploy/publish, force-push, destructive DB/file ops—and DUA limits from workspace policy.
---

## OVERVIEW

Some actions are **never** silently autonomous. Workspace policy (`skills/autonomous-execution/SKILL.md`, **aleksander.mdc** security invariants) and **`rules/orchestrator.mdc`** high-privilege / external norms require explicit human authorization. This skill lists **hard gates** and the expected escalation payload—links replace duplicating full policy text.

## КОГДА ИСПОЛЬЗОВАТЬ

- About to touch **secrets**, production credentials, or token-bearing config
- Deploy, publish, package release, or **network egress** not pre-approved
- **Destructive** git (`force push`, history rewrite), `rm -rf`, `DROP`, bulk overwrite
- Sandbox escape patterns (scripts to bypass tool restrictions)—see autonomous-execution / security rules

## WORKFLOW

### Шаг 1: Classify the action tier

1. **Tier A — Hard stop**: secrets in files, credential rotation without ticket, destructive VCS/data—requires **explicit user confirmation**; DUA does **not** override—`skills/autonomous-execution/SKILL.md` + aleksander **§2.6 / §2.6.3**.
2. **Tier B — Orchestrator policy**: multi-agent external deploy only with allowlist / dry-run expectations—align with **`rules/orchestrator.mdc` §3** trust boundary and **§18/§19** when external verification needed.
3. **Tier C — Normal writes**: code/docs within scoped OWNERSHIP; still avoid scope creep per task envelope.

### Шаг 2: STOP packet (what to send the user)

1. Halt tool execution; do **not** partial-apply destructive steps.
2. Message must include: **proposed action**, **risk**, **reversible?**, **exact commands** (if any), **files** touched, and **safe alternative** (dry-run, diff-only).
3. If blocked by policy: return `BLOCKED_POLICY` / `BLOCKED_EXTERNAL` style taxonomy when parent requests it—**§19** Blocker taxonomy in `rules/orchestrator.mdc`.

### Шаг 3: Resume criteria

1. Continue **only** after user message explicitly approves the bounded action or supplies revised scope.
2. Log the approval reference in completion contract (quote user line or task ID)—pair with **`skills/structured-agent-logging/SKILL.md`** when traces are required.
3. If user rejects: document blocker + residual risk; do not attempt covert workarounds.

## CHECKLIST

- [ ] Tier A action detected → stopped before execution
- [ ] User packet lists risks, reversibility, and exact scope
- [ ] No secrets printed in full in chat logs unless user explicitly requires and sec review path exists
- [ ] Resume only on explicit approval

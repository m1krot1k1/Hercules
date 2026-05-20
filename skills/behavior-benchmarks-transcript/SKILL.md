---
name: behavior-benchmarks-transcript
description: Transcript-grounded behavior verification—replay or analyze runs, invoke benchmark-specialist, and satisfy challenge-pass expectations tied to orchestrator completion gates.
---

## OVERVIEW

**Behavior benchmarks** and **transcript evaluation** prove agent/router compliance without hand-wavy “it works.” Canonical placement for challenge pass items appears in **`rules/orchestrator.mdc` §19** (`evaluate-transcript-runs` + benchmark) and quality gates in **§5 / §8**. Route specialists per **`rules/specialists.mdc`**: **`benchmark-specialist`** owns benchmark contracts in-repo.

## КОГДА ИСПОЛЬЗОВАТЬ

- After changing **rules/agents/skills** that affect behavior—large core deltas may require review gates per **§3** Large core-delta verify gate
- `/start` or FULL_FORCE profiles demand challenge pass—**§1.1** and **§19**
- Regression suspicion: orchestration drift, lazy-agent pattern failures—**§5** Lazy Agent Detection

## WORKFLOW

### Шаг 1: Capture or locate transcripts

1. Identify transcript artifacts (platform export, JSONL, internal `agent-transcripts` store—follow workspace privacy norms; do not exfiltrate).
2. Tag run metadata: model, profile, rules version, task ID—correlate via **`skills/structured-agent-logging/SKILL.md`** fields where available.
3. Redact secrets/PII before sharing logs externally.

### Шаг 2: Define or run benchmark-specialist checks

1. Delegate **`benchmark-specialist`**: behavior contracts, transcript replay expectations, pass/fail rubric—per specialist table in `rules/specialists.mdc`.
2. Align checks with **§8** chain verification: parents must not accept child “done” without mapped evidence.
3. If benchmarks fail: open targeted rework branches with **rework_limit** discipline—**`skills/budget-orchestration/SKILL.md`** + **§1** / **§8**.

### Шаг 3: Challenge pass packaging

1. Produce outputs consistent with **§19**: benchmark + transcript evaluation cited in completion ledger / claim-to-evidence matrix when parent profile requires it.
2. For adversarial depth, pair with **§1.1** challenge pass roles (`code-reviewer`, `code-skeptic`, `security-auditor`)—do not conflate benchmark green with security sign-off.
3. Record `checks[]` with `pass|fail|not_run` + evidence string—schema **§5** Evidence schema.

## CHECKLIST

- [ ] Transcript or run log identified and minimally redacted
- [ ] benchmark-specialist engaged with explicit AC
- [ ] Results mapped to §19 / evidence schema fields for the parent contract
- [ ] Failures routed to rework, not silent acceptance

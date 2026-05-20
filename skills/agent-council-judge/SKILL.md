---
name: agent-council-judge
description: Multi-variant proposals with a judge step and explicit Council triggers—aligns with rules §17 Agent Council Protocol and related debate/adversarial sections.
---

## OVERVIEW

For high-stakes or ambiguous core decisions, produce **2–3 concrete variants**, then a **judge** selects, scores, and cherry-picks—per **`rules/orchestrator.mdc` §17** (Agent Council Protocol). Related patterns: **§14** Multi-Model Debate, **§15** Adversarial Peer Refinement, **§18** shared cited fact-pack when variants depend on external facts.

## КОГДА ИСПОЛЬЗОВАТЬ

- `rules/*.mdc` changes with material behavior impact—**§17** explicitly ties Council to core rules
- Large extraction / many candidate changes (>30 candidates or high ambiguity)—see **§17** and **§12** extraction density
- Single-writer consensus would hide trade-offs; stakeholders need explicit variant + rationale

## WORKFLOW

### Шаг 1: Confirm Council is mandatory or valuable

1. Read **§17** in `rules/orchestrator.mdc`: triggers (e.g., core rules, candidate count), max **3 variants**, judge role (**producer type** must match §17—typically code-reviewer as judge selecting among implementations).
2. If only a cited fact-pack resolves factual disagreement, run **`skills/web-research-fact-pack/SKILL.md`** first; Council votes use one **`same cited fact-pack`** per §17/§18 linkage.
3. If L1 fan-out or depth is at risk, reconcile with **§0**, **§12** restructuring before spawning variants.

### Шаг 2: Produce capped variants in parallel

1. Spawn **Variant A / B (/ C)** with **disjoint or clearly scoped OWNERSHIP** if they touch files—parallel writer safety in **§3** (CAID-oriented ownership discipline; see also `skills/caid-ownership-matrix/SKILL.md`).
2. Each variant: goal, diff sketch, risks, rollback; no more than three.
3. Keep factual claims anchored; if external facts matter, cite §18 pack only.

### Шаг 3: Judge, score, cherry-pick

1. **Judge** task: score each variant /10 per agreed criteria, pick winner, list gaps, **cherry-pick up to two items from non-winners**—exact pattern in **§17**.
2. Record decision + dissenting merits for future audits (short matrix, not prose novels).
3. If judge finds policy violations (security-only work in wrong agent, etc.), reject per **§3** Role-Match.

## CHECKLIST

- [ ] §17 preconditions checked; variant count ≤ 3
- [ ] Fact-pack shared if web-dependent (§18)
- [ ] Judge output includes scores, winner, cherry-picks
- [ ] Ownership conflicts absent or escalated before merge

# Spec: Agent Registry Expansion — 28 → 33 agents

**TASK_ID:** `agent-registry-expansion-001`
**Status:** CLOSED (evidence collected, verdict issued)
**Owner:** meta-agent-architect + orchestrator

---

## Context

The canonical `agents/` directory contained 28 agents. Six agents referenced in `.github/agents/` and `rules/specialists.mdc` routing had no canonical `.md` counterpart. Cross-platform scripts for VCS preflight were also missing on Windows/Python.

## Acceptance Criteria

- **AC1:** All 33 agent `.md` files exist in `agents/` with correct YAML frontmatter (`name` matches filename, `description` present).
- **AC2:** `agents/README.md` declares `33 agent definitions` and `29 domain specialists`.
- **AC3:** `rules/specialists.mdc` declares `**33 agent definitions**` and `**29**` domain specialists with routing entries for all 33.
- **AC4:** Root `README.md` declares `33 agent definitions`.
- **AC5:** `scripts/iteration-vcs-preflight.ps1` and `scripts/iteration-vcs-preflight.py` exist and match exit-code contract of `.sh` version (0/2/3).
- **AC6:** `benchmarks/behavior-contracts.json` contains contracts for `agent_registry_completeness` and `vcs_preflight_cross_platform`.

## Out of Scope

- Python runtime availability (blocked on environment; scripts are runnable when Python is installed)
- Deletion of deprecated `pr-agent-workflow` skill (kept as redirect stub)

# Evidence: Agent Registry Expansion

**TASK_ID:** `agent-registry-expansion-001`
**Collected by:** orchestrator wave execution

---

## AC1 — All 33 agent files exist with correct frontmatter

```
agents/
  agent-architect.md      ✓
  api-designer.md         ✓
  architect.md            ✓
  ask.md                  ✓
  benchmark-specialist.md ✓ (new)
  bug-triage.md           ✓
  code-reviewer.md        ✓
  code-simplifier.md      ✓
  code-skeptic.md         ✓
  code.md                 ✓
  data-analyst.md         ✓
  database-specialist.md  ✓
  debug.md                ✓
  devops-specialist.md    ✓
  docs-specialist.md      ✓
  frontend-specialist.md  ✓
  meta-agent-architect.md ✓
  mobile-specialist.md    ✓
  monitoring-specialist.md ✓
  orchestrator.md         ✓
  performance-optimizer.md ✓
  profile-manager.md      ✓ (new)
  provider-integrator.md  ✓
  release-manager.md      ✓
  repo-explorer.md        ✓
  review.md               ✓
  rules-specialist.md     ✓ (new)
  security-auditor.md     ✓
  skills-specialist.md    ✓ (new)
  start.md                ✓
  subagent-factory.md     ✓
  test-specialist.md      ✓
  tgbot-specialist.md     ✓ (new)
```

Newly created agents verified: frontmatter `name:` matches filename for all 5 new files.

## AC2 — agents/README.md count

```
grep "agent definitions" agents/README.md
→ *33 agent definitions (4 coordination + 29 domain specialists in core)*   ✓
```

## AC3 — rules/specialists.mdc count

```
grep "agent definitions" rules/specialists.mdc
→ **33 agent definitions** ... **29** domain specialists   ✓

New routing entries confirmed (lines 71-75):
  tgbot-specialist       ✓
  benchmark-specialist   ✓
  rules-specialist       ✓
  skills-specialist      ✓
  profile-manager        ✓
```

## AC4 — Root README.md count

```
grep "agent definitions" README.md
→ **33 agent definitions** (4 coordination + 29 domain specialists)   ✓
```

## AC5 — Cross-platform preflight scripts

```
scripts/iteration-vcs-preflight.sh   ✓ (pre-existing)
scripts/iteration-vcs-preflight.ps1  ✓ (created)
scripts/iteration-vcs-preflight.py   ✓ (created)
```
All three use exit codes 0 (ok), 2 (dirty-tree), 3 (behind-remote).

## AC6 — Behavior contracts

```json
"agent_registry_completeness"      — present ✓
"vcs_preflight_cross_platform"     — present ✓
"branch_count_cap_before_suborchestrator" — present ✓
"profile_isolation_enforced"       — present ✓
```

## Notes

- Python not available on this machine: `validate-agent-registry.py` and `run-behavior-benchmarks.py` untestable without installing Python 3.
- All verifications above done via file-system inspection (grep_search, list_dir).

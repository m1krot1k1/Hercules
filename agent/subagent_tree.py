"""
Subagent tree renderer for TUI overlay displays (CLI spinner, /agents, dashboard).

Consumes the thread-safe ``list_active_subagents()`` snapshot from
``tools/delegate_tool`` and produces a compact tree string suitable for
inline rendering above a prompt_toolkit spinner, in a curses pane, or in
a gateway status message.

Status icons (rotated per tick for "running"):
    🗘  running (frame 1),  🌀 running (frame 2),  ⚡ running (frame 3)
    ✓  completed
    ✗  failed / error
    ⏸  interrupted (uses completed marker in tree but less prominent)
"""

import time
from typing import Any, Dict, List, Optional

from tools.delegate_tool import (
    _gc_completed_subagents,
    list_active_subagents as _list_active_subagents,
)

# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

# Spinner frame sequence for running agents — switched every second so the
# eye catches "something is alive" without burning too much terminal BW.
_RUNNING_ICONS = ["🗘", "🌀", "⚡"]

# Maximum tree width in terminal columns.  Trees wider than this get
# truncated so they don't wrap and ruin the spinner overlay alignment.
_MAX_TREE_WIDTH = 72

# Max goal label length per node; longer strings get "..."
_MAX_GOAL_CHARS = 28

# How long (seconds) after completion a subagent stays in the tree
# before GC sweeps it.  Matches _MAX_COMPLETED_AGE in delegate_tool.py.
_VISIBLE_AFTER_COMPLETION = 60.0

_tick_counter: List[int] = [0]


def _running_icon() -> str:
    """Return the current spinner frame character for running agents."""
    _tick_counter[0] += 1
    return _RUNNING_ICONS[_tick_counter[0] % len(_RUNNING_ICONS)]


def _elapsed_short(started_at: float) -> str:
    """Human-readable elapsed time (e.g. '3s', '1m', '2m30s', '5m')."""
    delta = max(0, time.monotonic() - started_at)
    if delta < 60:
        return f"{int(delta)}s"
    minutes = int(delta / 60)
    seconds = int(delta % 60)
    if minutes < 10:
        return f"{minutes}m{seconds}s"
    return f"{minutes}m"


def _icon_for_status(status: str) -> str:
    """Return the icon for a subagent node."""
    if status == "running":
        return _running_icon()
    if status == "completed":
        return "✓"
    if status in {"failed", "error", "timeout"}:
        return "✗"
    if status == "interrupted":
        return "⏸"
    return "?"


def render_subagent_tree(
    *,
    max_tree_width: int = _MAX_TREE_WIDTH,
    max_goal_chars: int = _MAX_GOAL_CHARS,
    gc: bool = True,
) -> Optional[str]:
    """Render a compact tree view of the subagent spawn hierarchy.

    Returns None when no subagents are known (tree is empty).

    When *gc* is True (default), sweeps stale completed/failed records
    before rendering so the tree doesn't accumulate dead nodes forever.
    Callers that render on a sub-second timer can set *gc* to False; a
    separate slower timer should still call it periodically.
    """
    if gc:
        _gc_completed_subagents()

    # Snapshot — thread-safe, returns a copy
    agents: List[Dict[str, Any]] = _list_active_subagents()
    if not agents:
        return None

    # Filter out records that have been "done" for too long.
    # _gc_completed_subagents handles the module-level dict; this is belt-and-suspenders
    # for the render snapshot so we don't bloat a visible tree.
    now = time.monotonic()
    visible: List[Dict[str, Any]] = []
    for rec in agents:
        status = rec.get("status", "running")
        if status == "running":
            visible.append(rec)
            continue
        completed_at = rec.get("completed_at", 0)
        if now - completed_at < _VISIBLE_AFTER_COMPLETION:
            visible.append(rec)
        # else: drop from render

    if not visible:
        return None

    # ── Build parent→children lookup ────────────────────────────────
    by_id: Dict[str, Dict[str, Any]] = {r["subagent_id"]: r for r in visible}
    children_by_parent: Dict[Optional[str], List[Dict[str, Any]]] = {}
    for r in visible:
        pid = r.get("parent_id")
        children_by_parent.setdefault(pid, []).append(r)

    # Sort children by depth then started_at for stable ordering
    for pid in list(children_by_parent):
        children_by_parent[pid].sort(
            key=lambda r: (r.get("depth", 0), r.get("started_at", 0))
        )

    # ── Count statistics ────────────────────────────────────────────
    running = sum(1 for r in visible if r.get("status") == "running")
    completed = sum(1 for r in visible if r.get("status") == "completed")
    failed = sum(
        1 for r in visible if r.get("status") in {"failed", "error", "timeout"}
    )
    interrupted = sum(1 for r in visible if r.get("status") == "interrupted")

    parts: List[str] = []
    status_parts: List[str] = []
    if running:
        status_parts.append(f"{running} running")
    if completed:
        status_parts.append(f"{completed} done")
    if failed:
        status_parts.append(f"{failed} failed")
    if interrupted:
        status_parts.append(f"{interrupted} interrupted")
    status_str = ", ".join(status_parts) if status_parts else "idle"

    parts.append(f" {_running_icon()} Delegation ({status_str})")

    # ── Recursive tree builder ──────────────────────────────────────
    def _render_node(
        node: Dict[str, Any],
        prefix: str = "",
        is_last: bool = True,
    ):
        status = node.get("status", "running")
        icon = _icon_for_status(status)
        goal = (node.get("goal") or "")[:max_goal_chars]
        if len(node.get("goal") or "") > max_goal_chars:
            goal = goal.rstrip() + "..."
        elapsed = _elapsed_short(node.get("started_at", now))
        tool_count = node.get("tool_count", 0)
        last_tool = node.get("last_tool", "")
        model = node.get("model", "") or ""

        # Compact: depth indentation + icon + goal + elapsed
        branch = "└── " if is_last else "├── "
        indent = prefix + branch

        # Node line:  ⚡ code-reviewer (3s, 12 tools, file_read)
        tool_part = f", {tool_count}t" if tool_count else ""
        model_part = f" [{model}]" if model else ""
        node_line = f"{icon} {goal}{model_part} ({elapsed}{tool_part})"

        line = f"{indent}{node_line}"
        if len(line) > max_tree_width:
            line = line[: max_tree_width - 3] + "..."

        parts.append(line)

        # Render children recursively
        cid = node.get("subagent_id")
        children = children_by_parent.get(cid, [])
        if children:
            child_prefix = prefix + ("    " if is_last else "│   ")
            for i, child in enumerate(children):
                child_is_last = i == len(children) - 1
                _render_node(child, prefix=child_prefix, is_last=child_is_last)

    # ── Root nodes (parent_id is None) ──────────────────────────────
    root_nodes = children_by_parent.get(None, [])
    for i, root in enumerate(root_nodes):
        root_is_last = i == len(root_nodes) - 1
        _render_node(root, prefix=" ", is_last=root_is_last)

    return "\n".join(parts)


# ---------------------------------------------------------------------------
# Structured tree snapshot for TUI panel
# ---------------------------------------------------------------------------

def get_subagent_tree_snapshot() -> List[Dict[str, Any]]:
    """Return a structured list of subagent records for the TUI panel.

    Each record has: subagent_id, goal, status, depth, parent_id,
    started_at, tool_count, last_tool, model, reasoning.
    """
    _gc_completed_subagents()
    agents: List[Dict[str, Any]] = _list_active_subagents()

    now = time.monotonic()
    visible: List[Dict[str, Any]] = []
    for rec in agents:
        status = rec.get("status", "running")
        if status == "running":
            visible.append(rec)
            continue
        completed_at = rec.get("completed_at", 0)
        if now - completed_at < _VISIBLE_AFTER_COMPLETION:
            visible.append(rec)

    return visible


def get_subagent_detail(subagent_id: str) -> Optional[Dict[str, Any]]:
    """Return detailed info about a specific subagent by ID.

    Includes reasoning/thoughts if available.
    """
    agents: List[Dict[str, Any]] = _list_active_subagents()
    for rec in agents:
        if rec.get("subagent_id") == subagent_id:
            return rec
    return None
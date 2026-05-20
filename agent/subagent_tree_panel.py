"""
Subagent tree panel for Hercules CLI — split-pane view.

When /tree mode is active, renders a left panel with the subagent
delegation tree and a right panel showing the selected subagent's
reasoning. Navigation:
  - Up/Down: move selection in tree
  - Right/Enter: expand node or select to view reasoning
  - Left/Esc: collapse node or exit tree mode
  - Tab: toggle focus between tree and chat input

Layout when tree is active:
  +------------------------+---------------------------+
  | ⚕ Agents (yellow)     | Selected Subagent Output  |
  | (navigable tree)       | (reasoning / thoughts)    |
  +------------------------+---------------------------+
  | Chat input (bottom, as usual)                     |
  +---------------------------------------------------+
"""

import time
import threading
from typing import Any, Callable, Dict, List, Optional, Tuple

from prompt_toolkit.formatted_text import FormattedText
from prompt_toolkit.layout import (
    ConditionalContainer,
    Container,
    Dimension,
    HSplit,
    VSplit,
    Window,
    FormattedTextControl,
)
from prompt_toolkit.filters import Condition
from prompt_toolkit.widgets import Frame

from agent.subagent_tree import (
    _list_active_subagents,
    _gc_completed_subagents,
    get_subagent_detail,
)


# ── Constants ─────────────────────────────────────────────────────────────

_MAX_TREE_WIDTH = 36
_MAX_GOAL_CHARS = 24
_VISIBLE_AFTER_COMPLETION = 60.0

_RUNNING_ICONS = ["ŀ", "ÿ", "âš"]  # will use unicode later


# ── Tree node ─────────────────────────────────────────────────────────────

class TreeNode:
    """A node in the subagent tree for interactive navigation."""
    __slots__ = (
        "subagent_id", "goal", "status", "depth", "started_at",
        "tool_count", "last_tool", "model", "parent_id",
        "children", "expanded", "reasoning",
    )

    def __init__(self, data: Dict[str, Any]):
        self.subagent_id = data.get("subagent_id", "")
        self.goal = (data.get("goal") or "")[:_MAX_GOAL_CHARS]
        self.status = data.get("status", "running")
        self.depth = data.get("depth", 0)
        self.started_at = data.get("started_at", time.monotonic())
        self.tool_count = data.get("tool_count", 0)
        self.last_tool = data.get("last_tool", "")
        self.model = data.get("model", "")
        self.parent_id = data.get("parent_id")
        self.children: List["TreeNode"] = []
        self.expanded = False
        self.reasoning = data.get("reasoning", "")

    @property
    def icon(self) -> str:
        if self.status == "running":
            return "âśš"
        if self.status == "completed":
            return "âśš"
        if self.status in ("failed", "error", "timeout"):
            return "âś—"
        if self.status == "interrupted":
            return "âš"
        return "?"

    @property
    def elapsed(self) -> str:
        delta = max(0, time.monotonic() - self.started_at)
        if delta < 60:
            return f"{int(delta)}s"
        m = int(delta / 60)
        s = int(delta % 60)
        return f"{m}m{s}s" if m < 10 else f"{m}m"

    @property
    def has_children(self) -> bool:
        return len(self.children) > 0


# ── SubagentTreePanel ─────────────────────────────────────────────────────

class SubagentTreePanel:
    """Interactive subagent tree panel for the split-pane TUI.

    Manages tree data, selection state, and navigation.
    Renders formatted text for prompt_toolkit.
    """

    def __init__(self, on_select: Optional[Callable] = None):
        self.on_select = on_select  # Called with (subagent_id, reasoning)
        self.nodes: List[TreeNode] = []
        self.flat_nodes: List[TreeNode] = []
        self.selected_index = 0
        self._selected_id: Optional[str] = None
        self._selected_reasoning: str = ""
        self._lock = threading.Lock()

    def refresh(self) -> bool:
        """Refresh tree data from delegate_tool. Returns True if changed."""
        _gc_completed_subagents()
        agents = _list_active_subagents()
        now = time.monotonic()

        visible = []
        for rec in agents:
            status = rec.get("status", "running")
            if status == "running":
                visible.append(rec)
                continue
            completed_at = rec.get("completed_at", 0)
            if now - completed_at < _VISIBLE_AFTER_COMPLETION:
                visible.append(rec)

        with self._lock:
            # Preserve expanded state
            old_expanded = {n.subagent_id for n in self.flat_nodes if n.expanded}
            old_selected = self._selected_id

            by_id: Dict[str, TreeNode] = {}
            children_by_parent: Dict[Optional[str], List[TreeNode]] = {}
            for rec in visible:
                node = TreeNode(rec)
                by_id[node.subagent_id] = node
                pid = node.parent_id
                children_by_parent.setdefault(pid, []).append(node)

            for pid in list(children_by_parent):
                children_by_parent[pid].sort(key=lambda n: n.started_at)

            for node in by_id.values():
                node.children = children_by_parent.get(node.subagent_id, [])

            self.nodes = children_by_parent.get(None, [])
            self._rebuild_flat()

            # Restore expanded state
            for node in self.flat_nodes:
                if node.subagent_id in old_expanded:
                    node.expanded = True

            # Restore selection
            if old_selected:
                for i, n in enumerate(self.flat_nodes):
                    if n.subagent_id == old_selected:
                        self.selected_index = i
                        break

            return True

    def _rebuild_flat(self):
        """Rebuild the flat list of visible nodes."""
        self.flat_nodes = []
        self._flatten(self.nodes)
        if self.flat_nodes:
            self.selected_index = min(self.selected_index, len(self.flat_nodes) - 1)
        else:
            self.selected_index = 0

    def _flatten(self, nodes: List[TreeNode]):
        for node in nodes:
            self.flat_nodes.append(node)
            if node.expanded and node.has_children:
                self._flatten(node.children)

    def move_up(self):
        with self._lock:
            if self.flat_nodes and self.selected_index > 0:
                self.selected_index -= 1

    def move_down(self):
        with self._lock:
            if self.flat_nodes and self.selected_index < len(self.flat_nodes) - 1:
                self.selected_index += 1

    def move_right(self) -> Optional[str]:
        """Expand node or select subagent. Returns subagent_id if selected."""
        with self._lock:
            if not self.flat_nodes:
                return None
            node = self.flat_nodes[self.selected_index]
            if node.has_children and not node.expanded:
                node.expanded = True
                self._rebuild_flat()
                return None
            # Select this subagent
            self._selected_id = node.subagent_id
            self._selected_reasoning = node.reasoning
            if self.on_select:
                self.on_select(node.subagent_id, node.reasoning)
            return node.subagent_id

    def move_left(self) -> bool:
        """Collapse node. Returns True if tree mode should be exited."""
        with self._lock:
            if not self.flat_nodes:
                return True
            node = self.flat_nodes[self.selected_index]
            if node.expanded:
                node.expanded = False
                self._rebuild_flat()
                return False
            return True  # Signal to exit tree mode or deselect

    def get_selected_detail(self) -> Optional[Dict[str, Any]]:
        """Get detail dict for the currently selected subagent."""
        with self._lock:
            if not self.flat_nodes or self.selected_index >= len(self.flat_nodes):
                return None
            node = self.flat_nodes[self.selected_index]
            return get_subagent_detail(node.subagent_id)

    def render_tree(self) -> FormattedText:
        """Render the tree panel as FormattedText."""
        with self._lock:
            if not self.flat_nodes:
                return FormattedText([
                    ("class:tree.header", " \u2695 Agents"),
                    ("class:tree.empty", "\n   (no active agents)"),
                ])

            running = sum(1 for n in self.flat_nodes if n.status == "running")
            completed = sum(1 for n in self.flat_nodes if n.status == "completed")
            failed = sum(1 for n in self.flat_nodes if n.status in ("failed", "error", "timeout"))

            parts: List[Tuple[str, str]] = []
            status_parts = []
            if running:
                status_parts.append(f"{running}\u21bb")
            if completed:
                status_parts.append(f"{completed}\u2713")
            if failed:
                status_parts.append(f"{failed}\u2717")
            status_str = " ".join(status_parts) if status_parts else "idle"
            parts.append(("class:tree.header", f" \u2695 Agents ({status_str})\n"))

            for i, node in enumerate(self.flat_nodes):
                is_selected = (i == self.selected_index)
                indent = "  " * node.depth
                expand_marker = ""
                if node.has_children:
                    expand_marker = "\u25b8 " if not node.expanded else "\u25be "
                elif node.depth > 0:
                    expand_marker = "  "

                if node.status == "running":
                    style = "class:tree.running"
                elif node.status == "completed":
                    style = "class:tree.completed"
                elif node.status in ("failed", "error", "timeout"):
                    style = "class:tree.failed"
                else:
                    style = "class:tree.idle"

                if is_selected:
                    style = "class:tree.selected"

                tool_part = f" {node.tool_count}t" if node.tool_count else ""
                line = f"{indent}{expand_marker}{node.icon} {node.goal} ({node.elapsed}{tool_part})\n"
                parts.append((style, line))

            return FormattedText(parts)

    def render_reasoning(self) -> FormattedText:
        """Render the reasoning panel for the selected subagent."""
        with self._lock:
            if not self.flat_nodes or self.selected_index >= len(self.flat_nodes):
                return FormattedText([("", "  Select a subagent to view output")])

            node = self.flat_nodes[self.selected_index]

            # Try to get live reasoning from delegate_tool
            detail = get_subagent_detail(node.subagent_id)
            reasoning = ""
            if detail:
                reasoning = detail.get("reasoning", "") or detail.get("goal", "")
            
            parts: List[Tuple[str, str]] = []
            # Header with subagent name
            status_icon = node.icon
            parts.append(("class:tree.header", f" {status_icon} {node.goal}\n"))

            # Status line
            model_str = f" [{node.model}]" if node.model else ""
            parts.append(("class:tree.idle", f"   Status: {node.status}{model_str}\n"))
            parts.append(("class:tree.idle", f"   Elapsed: {node.elapsed}"))
            if node.tool_count:
                parts.append(("class:tree.idle", f"  Tools: {node.tool_count}"))
            parts.append(("", "\n\n"))

            # Reasoning content
            if reasoning:
                parts.append(("class:tree.reasoning", f"  {reasoning}"))
            elif node.status == "running":
                parts.append(("class:tree.running", "  Working...\n"))
                # Show last tool if available
                if node.last_tool:
                    parts.append(("class:tree.idle", f"  Last tool: {node.last_tool}"))
            elif node.status == "completed":
                parts.append(("class:tree.completed", "  Completed."))
            elif node.status in ("failed", "error", "timeout"):
                parts.append(("class:tree.failed", f"  {node.status.upper()}"))

            return FormattedText(parts)

    @property
    def selected_subagent_id(self) -> Optional[str]:
        with self._lock:
            if self.flat_nodes and 0 <= self.selected_index < len(self.flat_nodes):
                return self.flat_nodes[self.selected_index].subagent_id
            return None


# ── Tree style dict ───────────────────────────────────────────────────────

TREE_STYLES = {
    "tree.header": "bold #FFD700",          # yellow bold
    "tree.empty": "#666666",
    "tree.running": "#00ff00",              # green
    "tree.completed": "#888888",            # grey
    "tree.failed": "#ff4444",               # red
    "tree.idle": "#aaaaaa",                  # light grey
    "tree.selected": "bg:#0044aa #ffffff bold",  # white on blue
    "tree.reasoning": "#FFF8DC",             # cornsilk
    "tree.border": "#FFFF00",                # yellow border
}


# ── Build the split-pane layout ───────────────────────────────────────────

def build_tree_split_layout(panel: SubagentTreePanel) -> Container:
    """Build a VSplit layout: tree on the left, reasoning on the right."""

    tree_control = FormattedTextControl(panel.render_tree)
    tree_window = Window(
        content=tree_control,
        width=Dimension(preferred=_MAX_TREE_WIDTH, min=25, max=50),
        height=Dimension(min=8),
        wrap_lines=True,
    )

    reasoning_control = FormattedTextControl(panel.render_reasoning)
    reasoning_window = Window(
        content=reasoning_control,
        height=Dimension(min=8),
        wrap_lines=True,
    )

    # Left panel: tree in a yellow frame
    left_frame = Frame(
        tree_window,
        title="\u2695 Agents",
        style="class:tree.border",
        width=Dimension(preferred=_MAX_TREE_WIDTH, min=27, max=52),
    )

    # Right panel: reasoning
    right_frame = Frame(
        reasoning_window,
        title="Subagent Output",
        style="class:tree.border",
    )

    # Side-by-side layout
    return VSplit([left_frame, right_frame])
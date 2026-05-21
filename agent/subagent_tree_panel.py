"""
Subagent tree panel for Hercules CLI — full-screen split-pane view.

When /tree mode is active, renders:
  LEFT: Subagent delegation tree with per-agent tokens, time, cost
  RIGHT: Selected subagent output (reasoning / thinking / tool calls)
  Toggle: Tab switches between "Show Output" (default) and "Hide Output" (tree-only)

Navigation:
  - Up/Down: move selection in tree
  - Right/Enter: expand node or select to view reasoning
  - Left/Esc: collapse node or exit tree mode
  - Tab: toggle focus between tree and chat input

Layout (full-screen):
  +------------------------+------------------------------------------+
  | ⚕ Agents (tree)        | Subagent Output (thinking / tools / msg) |
  | per-agent: time, tokens,| <thinking>, tool calls, responses       |
  | cost. Cumulative totals | Toggle: Tab to Show/Hide output         |
  +------------------------+------------------------------------------+
  | Chat input (bottom, as usual)                                      |
  +--------------------------------------------------------------------+
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

_MAX_TREE_WIDTH = 40
_MAX_GOAL_CHARS = 24
_VISIBLE_AFTER_COMPLETION = 120.0   # Show completed agents for 2 min (was 24h — too noisy)
_KEYBINDING_HINT = "↑↓:sel  ←→:expand/collapse  Tab:Show/Hide output  Esc:exit tree"


# ── Tree node ─────────────────────────────────────────────────────────────

class TreeNode:
    """A node in the subagent tree for interactive navigation."""
    __slots__ = (
        "subagent_id", "goal", "agent_name", "status", "depth", "started_at",
        "tool_count", "last_tool", "recent_tools", "model", "parent_id",
        "children", "expanded", "reasoning",
        "tokens_in", "tokens_out", "cost_usd", "messages",
        # Rollup metrics
        "total_tokens_rollup", "total_cost_rollup", "total_tools_rollup", "total_time_rollup",
        # Display toggles
        "show_output", "show_thinking", "show_tool_calls", "show_intermediate",
    )

    def __init__(self, data: Dict[str, Any]):
        self.subagent_id = data.get("subagent_id", "")
        self.goal = (data.get("goal") or "")[:_MAX_GOAL_CHARS]
        self.agent_name = data.get("agent_name", data.get("goal", "unknown")[:_MAX_GOAL_CHARS])
        self.status = data.get("status", "running")
        self.depth = data.get("depth", 0)
        self.started_at = data.get("started_at", time.monotonic())
        self.tool_count = data.get("tool_count", 0)
        self.last_tool = data.get("last_tool", "")
        self.recent_tools = data.get("recent_tools", [])
        self.model = data.get("model", "")
        self.parent_id = data.get("parent_id")
        self.children: List["TreeNode"] = []
        self.expanded = False
        self.reasoning = data.get("reasoning", "")
        # Token/cost tracking
        self.tokens_in = data.get("tokens_in", 0)
        self.tokens_out = data.get("tokens_out", 0)
        self.cost_usd = data.get("cost_usd", 0.0)
        self.messages = data.get("messages", [])
        # Rollup metrics (computed later)
        self.total_tokens_rollup = self.tokens_in + self.tokens_out
        self.total_cost_rollup = self.cost_usd
        self.total_tools_rollup = self.tool_count
        self.total_time_rollup = 0.0
        # Display toggles
        self.show_output = False  # Toggle for showing/hiding agent output in TUI
        self.show_thinking = False
        self.show_tool_calls = False
        self.show_intermediate = False

    @property
    def icon(self) -> str:
        if self.status == "running":
            return "⚡"
        if self.status == "completed":
            return "✓"
        if self.status in ("failed", "error", "timeout"):
            return "✗"
        if self.status == "interrupted":
            return "⏸"
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

    @property
    def total_tokens(self) -> int:
        """Tokens used by this node (self + cumulative children)."""
        return self.total_tokens_rollup

    @property
    def total_cost(self) -> float:
        """Cost USD for this node (self + cumulative children)."""
        return self.total_cost_rollup
    
    @property
    def total_tools(self) -> int:
        """Total tools called by this node and children."""
        return self.total_tools_rollup
    
    @property
    def total_time(self) -> float:
        """Total execution time for this node and children."""
        return self.total_time_rollup
    
    def total_tools(self) -> int:
        """Total tools called by this node and children."""
        return self.total_tools_rollup
    
    def total_time(self) -> float:
        """Total execution time for this node and children."""
        return self.total_time_rollup

    def tokens_str(self) -> str:
        t = self.total_tokens
        if t >= 1000:
            return f"{t/1000:.1f}K"
        return str(t)

    def cost_str(self) -> str:
        c = self.total_cost
        if c <= 0:
            return ""
        if c < 0.01:
            return "<$0.01"
        return f"${c:.2f}"
    
    def compute_rollup(self):
        """Recursively compute rollup metrics from children."""
        # Start with direct metrics
        total_tokens = self.tokens_in + self.tokens_out
        total_cost = self.cost_usd
        total_tools = self.tool_count
        total_time = 0.0  # We don't have execution time yet
        
        # Add children rollup
        for child in self.children:
            child.compute_rollup()
            total_tokens += child.total_tokens_rollup
            total_cost += child.total_cost_rollup
            total_tools += child.total_tools_rollup
            total_time += child.total_time_rollup
        
        self.total_tokens_rollup = total_tokens
        self.total_cost_rollup = total_cost
        self.total_tools_rollup = total_tools
        self.total_time_rollup = total_time


# ── SubagentTreePanel ─────────────────────────────────────────────────────

class SubagentTreePanel:
    """Interactive subagent tree panel for the full-screen TUI.

    Manages tree data, selection state, navigation, and token/cost tracking.
    Renders formatted text for prompt_toolkit.
    """

    def __init__(self, on_select: Optional[Callable] = None):
        self.on_select = on_select
        self.nodes: List[TreeNode] = []
        self.flat_nodes: List[TreeNode] = []
        self.selected_index = 0
        self._selected_id: Optional[str] = None
        self._selected_reasoning: str = ""
        self._show_output: bool = True   # Toggle: Show/Hide output panel
        self._lock = threading.Lock()

    def toggle_output(self):
        """Toggle between Show Output and Hide Output modes."""
        self._show_output = not self._show_output

    def toggle_agent_output(self, agent_id: str) -> bool:
        """Toggle output visibility for a specific agent by ID.
        
        Returns True if agent was found and toggled, False otherwise.
        """
        with self._lock:
            for node in self.flat_nodes:
                if node.subagent_id == agent_id:
                    node.show_output = not node.show_output
                    return True
            return False

    @property
    def show_output(self) -> bool:
        return self._show_output

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

            for node in by_id.values():
                if node.subagent_id in old_expanded:
                    node.expanded = True

            self.nodes = children_by_parent.get(None, [])
            self._rebuild_flat()

            # Compute rollup metrics for root nodes
            for node in self.nodes:
                node.compute_rollup()

            if old_selected:
                for i, n in enumerate(self.flat_nodes):
                    if n.subagent_id == old_selected:
                        self.selected_index = i
                        break
            if self.flat_nodes and 0 <= self.selected_index < len(self.flat_nodes):
                self._selected_id = self.flat_nodes[self.selected_index].subagent_id

            return True

    def _rebuild_flat(self):
        self.flat_nodes = []
        self._flatten(self.nodes)
        if self.flat_nodes:
            self.selected_index = min(self.selected_index, len(self.flat_nodes) - 1)
            node = self.flat_nodes[self.selected_index]
            self._selected_id = node.subagent_id
        else:
            self.selected_index = 0
            self._selected_id = None

    def _flatten(self, nodes: List[TreeNode]):
        for node in nodes:
            self.flat_nodes.append(node)
            if node.expanded and node.has_children:
                self._flatten(node.children)

    # ── Cumulative totals ────────────────────────────────────────────────

    def _cumulative_totals(self) -> Tuple[int, int, float, int, int, int]:
        """Return (total_tokens_in, total_tokens_out, total_cost,
        running_count, completed_count, failed_count) for all nodes."""
        ti = to = rc = cc = fc = 0
        tc = 0.0
        for n in self.flat_nodes:
            ti += n.tokens_in
            to += n.tokens_out
            tc += n.cost_usd
            if n.status == "running":
                rc += 1
            elif n.status == "completed":
                cc += 1
            elif n.status in ("failed", "error", "timeout"):
                fc += 1
        return ti, to, tc, rc, cc, fc

    # ── Navigation ───────────────────────────────────────────────────────

    def move_up(self):
        with self._lock:
            if self.flat_nodes and self.selected_index > 0:
                self.selected_index -= 1
                node = self.flat_nodes[self.selected_index]
                self._selected_id = node.subagent_id

    def move_down(self):
        with self._lock:
            if self.flat_nodes and self.selected_index < len(self.flat_nodes) - 1:
                self.selected_index += 1
                node = self.flat_nodes[self.selected_index]
                self._selected_id = node.subagent_id

    def move_right(self) -> Optional[str]:
        with self._lock:
            if not self.flat_nodes:
                return None
            node = self.flat_nodes[self.selected_index]
            if node.has_children and not node.expanded:
                node.expanded = True
                self._rebuild_flat()
                return None
            self._selected_id = node.subagent_id
            self._selected_reasoning = node.reasoning
            if self.on_select:
                self.on_select(node.subagent_id, node.reasoning)
            return node.subagent_id

    def move_left(self) -> bool:
        with self._lock:
            if not self.flat_nodes:
                return True
            node = self.flat_nodes[self.selected_index]
            if node.expanded:
                node.expanded = False
                self._rebuild_flat()
                return False
            return True

    # ── Rendering ─────────────────────────────────────────────────────────

    def render_tree(self) -> FormattedText:
        """Render the tree panel with per-agent tokens, time, cost."""
        with self._lock:
            if not self.flat_nodes:
                return FormattedText([
                    ("class:tree.header", " ⚕ Agents\n"),
                    ("class:tree.empty", "\n   (no active agents)\n\n"),
                    ("class:tree.idle", "   Use /start <task> to launch\n"),
                    ("class:tree.idle", "   an orchestrator, or use\n"),
                    ("class:tree.idle", "   delegate_task for workers.\n"),
                ])

            # Get status counts and rollup totals
            _, _, _, rc, cc, fc = self._cumulative_totals()
            parts: List[Tuple[str, str]] = []

            # Compute rollup totals from root nodes
            total_tokens = sum(n.total_tokens_rollup for n in self.nodes)
            total_cost = sum(n.total_cost_rollup for n in self.nodes)
            total_tools = sum(n.total_tools_rollup for n in self.nodes)

            # Header with rollup totals
            status_parts = []
            if rc:
                status_parts.append(f"{rc}⚡")
            if cc:
                status_parts.append(f"{cc}✓")
            if fc:
                status_parts.append(f"{fc}✗")
            status_str = " ".join(status_parts) if status_parts else "idle"
            total_t_str = f"{total_tokens/1000:.1f}K" if total_tokens >= 1000 else str(total_tokens)
            cost_str = f" ${total_cost:.2f}" if total_cost > 0 else ""
            header = f" ⚕ Agents ({status_str}) Σ{total_t_str}t{cost_str}\n"

            for i, node in enumerate(self.flat_nodes):
                is_selected = (i == self.selected_index)
                indent = "  " * node.depth
                expand_marker = ""
                if node.has_children:
                    expand_marker = "▸ " if not node.expanded else "▾ "
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

                # Per-agent info line: icon + agent_name + elapsed + tools + tokens + cost
                info_parts = []
                if node.total_tools_rollup:
                    info_parts.append(f"{node.total_tools_rollup}t")
                info_parts.append(node.elapsed)
                tt = node.total_tokens
                if tt:
                    info_parts.append(f"{tt/1000:.1f}Kt" if tt >= 1000 else f"{tt}t")
                if node.total_cost_rollup > 0:
                    info_parts.append(f"${node.total_cost_rollup:.3f}")
                info = " ".join(info_parts)
                line = f"{indent}{expand_marker}{node.icon} {node.agent_name} ({info})\n"
                parts.append((style, line))

            # Footer: keybinding hint
            parts.append(("class:tree.idle", f"\n {_KEYBINDING_HINT}\n"))
            return FormattedText(parts)

    def render_reasoning(self) -> FormattedText:
        """Render the output panel for the selected subagent."""
        with self._lock:
            if not self._show_output:
                return FormattedText([
                    ("class:tree.header", " ⚕ Subagent Output (hidden)\n"),
                    ("class:tree.idle", "\n  Output hidden. Press Tab to show.\n"),
                    ("class:tree.idle", "  ↑↓ to select agent.\n"),
                ])

            if not self.flat_nodes or self.selected_index >= len(self.flat_nodes):
                return FormattedText([("class:tree.idle", "  ↑ Use arrows to select an agent")])

            node = self.flat_nodes[self.selected_index]
            detail = get_subagent_detail(node.subagent_id)
            reasoning = detail.get("reasoning", "") if detail else ""
            summary_text = (detail.get("summary", "") or "") if detail else ""
            messages = detail.get("messages", []) if detail else []

            parts: List[Tuple[str, str]] = []

            # ── Header: agent info + token/cost bar ──
            parts.append(("class:tree.header", f" {node.icon} {node.agent_name}\n"))
            model_str = f" [{node.model}]" if node.model else ""
            status_style = "class:tree.running" if node.status == "running" else "class:tree.idle"
            parts.append((status_style, f"   Status: {node.status}{model_str}\n"))

            # Token/cost bar
            info_line = f"   ⏱ {node.elapsed}"
            if node.total_tools_rollup:
                info_line += f"  🔧 {node.tool_count} tools"
            ti = node.tokens_in
            to = node.tokens_out if node.tokens_out else 0
            if ti or to:
                info_line += f"  📊 in:{ti/1000:.1f}K" if ti >= 1000 else f"  📊 in:{ti}"
                info_line += f" out:{to/1000:.1f}K" if to >= 1000 else f" out:{to}"
            if node.total_cost_rollup > 0:
                info_line += f"  💰 ${node.cost_usd:.4f}"
            parts.append(("class:tree.idle", info_line + "\n\n"))

            # ── Running agent: thinking ──
            if node.status == "running":
                if reasoning:
                    parts.append(("class:tree.running", "  💭 Thinking:\n"))
                    parts.append(("class:tree.reasoning", f"  {reasoning}\n"))
                else:
                    parts.append(("class:tree.running", "  ⚡ Running — waiting for first action...\n"))

                recent = node.recent_tools if node.recent_tools else (
                    detail.get("recent_tools", []) if detail else []
                )
                if recent:
                    parts.append(("class:tree.idle", "\n  Recent tools:\n"))
                    for tool_name, tool_preview in recent[-5:]:
                        tool_emoji = "🔧" if "search" not in tool_name and "read" not in tool_name and "terminal" not in tool_name else \
                                     "🔍" if "search" in tool_name else \
                                     "📖" if "read" in tool_name else \
                                     "⚡" if "terminal" in tool_name else "🔧"
                        tool_line = f"    {tool_emoji} {tool_name}"
                        if tool_preview:
                            preview_trunc = tool_preview[:45] + ("..." if len(tool_preview) > 45 else "")
                            tool_line += f": {preview_trunc}"
                        parts.append(("class:tree.idle", tool_line + "\n"))

            # ── Completed agent: summary ──
            elif node.status == "completed":
                if summary_text:
                    summary_short = summary_text[:800]
                    parts.append(("class:tree.completed", f"  ✓ {summary_short}\n"))
                elif reasoning:
                    parts.append(("class:tree.reasoning", f"  {reasoning}\n"))
                else:
                    parts.append(("class:tree.completed", "  ✓ Completed successfully.\n"))

            # ── Failed ──
            elif node.status in ("failed", "error", "timeout"):
                error_text = summary_text or (detail.get("error", "") if detail else "")
                parts.append(("class:tree.failed", f"  ✗ {node.status.upper()}"))
                if error_text:
                    parts.append(("class:tree.failed", f": {error_text[:300]}"))
                parts.append(("", "\n"))

            # ── Messages from agent ──
            if messages:
                parts.append(("class:tree.idle", "\n  ── Messages ──\n"))
                for msg in messages[-3:]:  # last 3 messages
                    role = msg.get("role", "")
                    content = msg.get("content", "")
                    if isinstance(content, str) and content.strip():
                        trunc = content[:200] + ("..." if len(content) > 200 else "")
                        parts.append(("class:tree.idle", f"  [{role}] {trunc}\n"))

            # Footer hint
            parts.append(("class:tree.idle", f"\n {_KEYBINDING_HINT}\n"))
            return FormattedText(parts)

    @property
    def selected_subagent_id(self) -> Optional[str]:
        with self._lock:
            if self.flat_nodes and 0 <= self.selected_index < len(self.flat_nodes):
                return self.flat_nodes[self.selected_index].subagent_id
            return None


# ── Tree style dict ───────────────────────────────────────────────────────

TREE_STYLES = {
    "tree.header": "bold #FFD700",
    "tree.empty": "#666666",
    "tree.running": "#00ff00",
    "tree.completed": "#888888",
    "tree.failed": "#ff4444",
    "tree.idle": "#aaaaaa",
    "tree.selected": "bg:#0044aa #ffffff bold",
    "tree.reasoning": "#FFF8DC",
    "tree.border": "#FFFF00",
}


# ── Build the full-screen split-pane layout ───────────────────────────────

def build_tree_split_layout(panel: SubagentTreePanel) -> Container:
    """Build a VSplit layout: tree on the left, output on the right (full-screen)."""

    tree_control = FormattedTextControl(panel.render_tree)
    tree_window = Window(
        content=tree_control,
        width=Dimension(preferred=_MAX_TREE_WIDTH, min=28, max=55),
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
        title="⚕ Agents",
        style="class:tree.border",
        width=Dimension(preferred=_MAX_TREE_WIDTH, min=30, max=57),
    )

    # Right panel: output with toggle
    right_title = "Subagent Output (Tab: Show/Hide)" if panel.show_output else "Subagent Output (Hidden — Tab to show)"
    right_frame = Frame(
        reasoning_window,
        title=right_title,
        style="class:tree.border",
    )

    return VSplit([left_frame, right_frame])
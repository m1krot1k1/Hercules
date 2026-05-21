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
    get_telemetry_tree,
    format_total_metrics,
)

from agent.dependency_graph import get_dependency_graph, TaskDependencyGraph, TaskStatus

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
# before GC sweeps it.  Set to 24h for session-persistent visibility.
_VISIBLE_AFTER_COMPLETION = 86400.0

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

    # ── Get telemetry tree for rollup metrics ──────────────────
    telemetry_tree = get_telemetry_tree()
    
    # DEBUG: Print telemetry data
    import sys
    print(f"DEBUG: telemetry_tree = {telemetry_tree}", file=sys.stderr)
    
    # Build a lookup from subagent_id to telemetry for quick access
    telemetry_by_id: Dict[str, Any] = {}
    
    def _build_telemetry_lookup(node: Dict[str, Any]):
        agent = node.get("agent")
        if agent:
            telemetry_by_id[agent.agent_id] = agent
            # DEBUG: Print each agent's telemetry
            print(f"DEBUG: agent_id={agent.agent_id}, tokens_in={agent.tokens_input}, tokens_out={agent.tokens_output}, cost={agent.cost_usd}", file=sys.stderr)
        for child in node.get("children", []):
            _build_telemetry_lookup(child)
    
    if telemetry_tree:
        _build_telemetry_lookup(telemetry_tree)

    # ── Count statistics ────────────────────────────────────
    running = sum(1 for r in visible if r.get("status") == "running")
    completed = sum(1 for r in visible if r.get("status") == "completed")
    failed = sum(
        1 for r in visible if r.get("status") in {"failed", "error", "timeout"}
    )
    interrupted = sum(1 for r in visible if r.get("status") == "interrupted")

    # Calculate total rollup metrics for the header
    total_tools = 0
    total_tokens = 0
    total_cost = 0.0
    for tid, tel in telemetry_by_id.items():
        if tel.parent_id is None:  # Only count root agents for total
            total_tools += tel.total_tools
            total_tokens += tel.total_tokens
            total_cost += tel.total_cost

    parts: List[str] = []
    status_parts: List[str] = []
    if running:
        status_parts.append(f"{running}⚡")
    if completed:
        status_parts.append(f"{completed}✓")
    if failed:
        status_parts.append(f"{failed}✗")
    if interrupted:
        status_parts.append(f"{interrupted}⏸")
    status_str = " ".join(status_parts) if status_parts else "idle"

    # Format header with totals
    tokens_str = f"{total_tokens:,}" if total_tokens >= 1000 else str(total_tokens)
    cost_str = f" ${total_cost:.2f}" if total_cost > 0 else ""
    header = f" ⚕ Agents ({status_str}) Σ{tokens_str}t{cost_str}"
    parts.append(header)

    # ── Recursive tree builder ──────────────────────────────────────
    def _render_node(
        node: Dict[str, Any],
        prefix: str = "",
        is_last: bool = True,
    ):
        status = node.get("status", "running")
        icon = _icon_for_status(status)
        agent_name = node.get("agent_name", node.get("goal", "unknown")[:max_goal_chars])
        if len(node.get("agent_name") or node.get("goal") or "") > max_goal_chars:
            agent_name = agent_name.rstrip() + "..."
        elapsed = _elapsed_short(node.get("started_at", now))
        tool_count = node.get("tool_count", 0)
        last_tool = node.get("last_tool", "")
        model = node.get("model", "") or ""

        # Get telemetry for this node
        sid = node.get("subagent_id")
        tel = telemetry_by_id.get(sid) if sid else None

        # Compact: depth indentation + icon + goal + elapsed
        branch = "└── " if is_last else "├── "
        indent = prefix + branch

        # Node line with rollup metrics
        # Format: ✓ code (50t in, 30t out, $0.05 total: 80t, $0.10)
        tokens_in = node.get("tokens_in", 0) or 0
        tokens_out = node.get("tokens_out", 0) or 0
        cost = node.get("cost_usd", 0) or 0

        # Build metrics part
        metrics_parts = []
        if tokens_in or tokens_out:
            metrics_parts.append(f"{tokens_in}t in")
            metrics_parts.append(f"{tokens_out}t out")
        if cost > 0:
            metrics_parts.append(f"${cost:.2f}")

        # Add rollup totals if available
        if tel and (tel.total_tokens > (tokens_in + tokens_out) or tel.total_cost > cost):
            metrics_parts.append(f"total: {tel.total_tokens}t")
            if tel.total_cost > 0:
                metrics_parts.append(f"${tel.total_cost:.2f}")

        metrics_str = ", ".join(metrics_parts) if metrics_parts else ""
        model_part = f" [{model}]" if model else ""

        if status == "running" and node.get("reasoning", ""):
            reasoning = node.get("reasoning", "") or ""
            short_reason = reasoning[:40] + ("..." if len(reasoning) > 40 else "")
            node_line = f"{icon} {agent_name}{model_part} ({elapsed}"
            if metrics_str:
                node_line += f", {metrics_str}"
            node_line += ")"
            reason_line = f"{indent}   ┈ {short_reason}"
        elif last_tool and status == "running":
            node_line = f"{icon} {agent_name}{model_part} ({elapsed}"
            if metrics_str:
                node_line += f", {metrics_str}"
            node_line += f", {last_tool})"
            reason_line = None
        else:
            node_line = f"{icon} {agent_name}{model_part} ({elapsed}"
            if metrics_str:
                node_line += f", {metrics_str}"
            node_line += ")"
            reason_line = None

        line = f"{indent}{node_line}"
        if len(line) > max_tree_width:
            line = line[: max_tree_width - 3] + "..."

        parts.append(line)

        # Show reasoning line if agent is actively thinking
        if reason_line:
            parts.append(reason_line)

        # Render children recursively
        cid = node.get("subagent_id")
        children = children_by_parent.get(cid, [])
        if children:
            child_prefix = prefix + ("    " if is_last else "│   ")
            for i, child in enumerate(children):
                child_is_last = i == len(children) - 1
                _render_node(child, prefix=child_prefix, is_last=child_is_last)

    # Render root nodes (those with parent_id is None)
    root_ids = [rid for rid in by_id if by_id[rid].get("parent_id") is None]
    for root_id in root_ids:
        _render_node(by_id[root_id], prefix="", is_last=True)
    
    # Add total summary line
    if total_tools > 0 or total_tokens > 0:
        summary = format_total_metrics(total_tools, total_tokens, total_cost)
        parts.append(f"\n{summary}")
    
    return "\n".join(parts)

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


def get_dependency_graph_data(graph_id: str = "default") -> Dict[str, Any]:
    """
    Возвращает данные графа зависимостей для визуализации.
    
    Args:
        graph_id: ID графа зависимостей
        
    Returns:
        Словарь с узлами и ребрами для UI.
    """
    graph = get_dependency_graph(graph_id)
    return graph.get_graph_visualization_data()


def update_task_status_in_graph(task_id: str, status: str, graph_id: str = "default") -> bool:
    """
    Обновляет статус задачи в графе зависимостей.
    
    Args:
        task_id: ID задачи
        status: Новый статус ('completed', 'failed', 'running', etc.)
        graph_id: ID графа
        
    Returns:
        True если обновление успешно
    """
    graph = get_dependency_graph(graph_id)
    if status == "completed":
        return graph.mark_completed(task_id)
    elif status == "failed":
        return graph.mark_failed(task_id, "Error")
    elif status == "running":
        return graph.mark_running(task_id)
    return False


def register_subagent_in_graph(
    task_id: str,
    goal: str = "",
    depends_on: List[str] = None,
    graph_id: str = "default",
    **metadata
) -> bool:
    """
    Регистрирует субагента в графе зависимостей.
    
    Args:
        task_id: ID субагента (используется как ID задачи в графе)
        goal: Цель/описание задачи
        depends_on: Список ID задач, от которых зависит данная
        graph_id: ID графа
        **metadata: Дополнительные метаданные
        
    Returns:
        True если регистрация успешна
    """
    try:
        graph = get_dependency_graph(graph_id)
        graph.add_task(
            task_id=task_id,
            name=goal[:50] if goal else task_id,
            description=goal,
            depends_on=depends_on or [],
            **metadata
        )
        return True
    except ValueError as e:
        print(f"Ошибка регистрации субагента в графе: {e}")
        return False


def complete_subagent_in_graph(task_id: str, graph_id: str = "default") -> bool:
    """
    Отмечает субагента как завершенного в графе зависимостей.
    
    Args:
        task_id: ID субагента
        graph_id: ID графа
        
    Returns:
        True если обновление успешно
    """
    return update_task_status_in_graph(task_id, "completed", graph_id)


def fail_subagent_in_graph(task_id: str, error_message: str = "", graph_id: str = "default") -> bool:
    """
    Отмечает субагента как завершившегося с ошибкой в графе зависимостей.
    
    Args:
        task_id: ID субагента
        error_message: Сообщение об ошибке
        graph_id: ID графа
        
    Returns:
        True если обновление успешно
    """
    graph = get_dependency_graph(graph_id)
    return graph.mark_failed(task_id, error_message or "Error")


def start_subagent_in_graph(task_id: str, graph_id: str = "default") -> bool:
    """
    Отмечает субагента как выполняющегося в графе зависимостей.
    
    Args:
        task_id: ID субагента
        graph_id: ID графа
        
    Returns:
        True если обновление успешно
    """
    return update_task_status_in_graph(task_id, "running", graph_id)


def get_subagent_with_dependencies(subagent_id: str = None, graph_id: str = "default") -> List[Dict[str, Any]]:
    """
    Возвращает список субагентов с информацией о зависимостях из графа.
    
    Args:
        subagent_id: Если указан, возвращает только этого субагента с его зависимостями
        graph_id: ID графа зависимостей
        
    Returns:
        Список субагентов с добавленными полями:
        - depends_on: список ID задач, от которых зависит
        - blocked_by: список ID задач, которые блокируют выполнение
        - graph_status: статус в графе зависимостей
    """
    graph = get_dependency_graph(graph_id)
    agents: List[Dict[str, Any]] = _list_active_subagents()
    
    result = []
    for rec in agents:
        # Фильтр по ID если указан
        if subagent_id and rec.get("subagent_id") != subagent_id:
            continue
            
        # Копируем запись
        enriched = dict(rec)
        task_id = rec.get("subagent_id", "")
        
        # Получаем данные из графа если есть
        task_node = graph.get_task(task_id)
        if task_node:
            enriched["depends_on"] = task_node.depends_on
            enriched["graph_status"] = task_node.status.value
            
            # Определяем блокирующие задачи
            blocked_by = []
            for dep_id in task_node.depends_on:
                dep_task = graph.get_task(dep_id)
                if dep_task and dep_task.status != TaskStatus.COMPLETED:
                    blocked_by.append(dep_id)
            enriched["blocked_by"] = blocked_by
        else:
            enriched["depends_on"] = []
            enriched["graph_status"] = None
            enriched["blocked_by"] = []
            
        result.append(enriched)
        
        if subagent_id:
            break
            
    return result


def render_subagent_tree_with_dependencies(
    *,
    graph_id: str = "default",
    max_tree_width: int = _MAX_TREE_WIDTH,
    max_goal_chars: int = _MAX_GOAL_CHARS,
    gc: bool = True,
) -> Optional[str]:
    """
    Расширенная версия render_subagent_tree с информацией о графе зависимостей.
    
    Показывает зависимости между задачами и статусы в графе.
    """
    if gc:
        _gc_completed_subagents()

    agents: List[Dict[str, Any]] = _list_active_subagents()
    if not agents:
        return None

    # Получаем данные графа
    graph = get_dependency_graph(graph_id)
    
    # Обогащаем данные о субагентах информацией из графа
    enriched_agents = []
    for rec in agents:
        enriched = dict(rec)
        task_id = rec.get("subagent_id", "")
        task_node = graph.get_task(task_id)
        if task_node:
            enriched["graph_status"] = task_node.status.value
            enriched["depends_on"] = task_node.depends_on
        else:
            enriched["graph_status"] = None
            enriched["depends_on"] = []
        enriched_agents.append(enriched)
    
    # Фильтруем завершенные
    now = time.monotonic()
    visible = []
    for rec in enriched_agents:
        status = rec.get("status", "running")
        if status == "running":
            visible.append(rec)
            continue
        completed_at = rec.get("completed_at", 0)
        if now - completed_at < _VISIBLE_AFTER_COMPLETION:
            visible.append(rec)

    if not visible:
        return None

    # Строим дерево как в оригинальной функции
    by_id: Dict[str, Dict[str, Any]] = {r["subagent_id"]: r for r in visible}
    children_by_parent: Dict[Optional[str], List[Dict[str, Any]]] = {}
    for r in visible:
        pid = r.get("parent_id")
        children_by_parent.setdefault(pid, []).append(r)

    for pid in list(children_by_parent):
        children_by_parent[pid].sort(
            key=lambda r: (r.get("depth", 0), r.get("started_at", 0))
        )

    telemetry_tree = get_telemetry_tree()
    telemetry_by_id: Dict[str, Any] = {}

    def _build_telemetry_lookup(node: Dict[str, Any]):
        agent = node.get("agent")
        if agent:
            telemetry_by_id[agent.agent_id] = agent
        for child in node.get("children", []):
            _build_telemetry_lookup(child)

    if telemetry_tree:
        _build_telemetry_lookup(telemetry_tree)

    running = sum(1 for r in visible if r.get("status") == "running")
    completed = sum(1 for r in visible if r.get("status") == "completed")
    failed = sum(1 for r in visible if r.get("status") in {"failed", "error", "timeout"})
    interrupted = sum(1 for r in visible if r.get("status") == "interrupted")

    total_tools = 0
    total_tokens = 0
    total_cost = 0.0
    for tid, tel in telemetry_by_id.items():
        if tel.parent_id is None:
            total_tools += tel.total_tools
            total_tokens += tel.total_tokens
            total_cost += tel.total_cost

    parts: List[str] = []
    status_parts: List[str] = []
    if running:
        status_parts.append(f"{running}⚡")
    if completed:
        status_parts.append(f"{completed}✓")
    if failed:
        status_parts.append(f"{failed}✗")
    if interrupted:
        status_parts.append(f"{interrupted}⏸")
    status_str = " ".join(status_parts) if status_parts else "idle"

    tokens_str = f"{total_tokens:,}" if total_tokens >= 1000 else str(total_tokens)
    cost_str = f" ${total_cost:.2f}" if total_cost > 0 else ""
    header = f" ⚕ Agents ({status_str}) Σ{tokens_str}t{cost_str}"
    parts.append(header)

    # Добавляем информацию о графе зависимостей
    graph_data = graph.get_graph_visualization_data()
    if graph_data and graph_data.get("nodes"):
        nodes_with_deps = [n for n in graph_data["nodes"] if n.get("status") != "completed"]
        if nodes_with_deps:
            deps_info = f"  Graph: {len(graph_data['nodes'])} tasks"
            blocked = [n for n in graph_data["nodes"] if n.get("status") == "blocked"]
            if blocked:
                deps_info += f", {len(blocked)} blocked"
            parts.append(deps_info)

    def _render_node(node: Dict[str, Any], prefix: str = "", is_last: bool = True):
        status = node.get("status", "running")
        icon = _icon_for_status(status)
        goal = (node.get("goal") or "")[:max_goal_chars]
        if len(node.get("goal") or "") > max_goal_chars:
            goal = goal.rstrip() + "..."
        elapsed = _elapsed_short(node.get("started_at", now))
        
        # Добавляем информацию о зависимостях
        deps_info = ""
        if node.get("depends_on"):
            deps_info = f" [deps: {', '.join(node['depends_on'][:2])}"
            if len(node["depends_on"]) > 2:
                deps_info = deps_info.rstrip("]") + f" +{len(node['depends_on']) - 2}]"
            else:
                deps_info += "]"
        
        tool_count = node.get("tool_count", 0)
        last_tool = node.get("last_tool", "")
        model = node.get("model", "") or ""

        sid = node.get("subagent_id")
        tel = telemetry_by_id.get(sid) if sid else None

        branch = "└── " if is_last else "├── "
        indent = prefix + branch

        tokens_in = node.get("tokens_in", 0) or 0
        tokens_out = node.get("tokens_out", 0) or 0
        cost = node.get("cost_usd", 0) or 0

        metrics_parts = []
        if tokens_in or tokens_out:
            metrics_parts.append(f"{tokens_in}t in")
            metrics_parts.append(f"{tokens_out}t out")
        if cost > 0:
            metrics_parts.append(f"${cost:.2f}")

        if tel and (tel.total_tokens > (tokens_in + tokens_out) or tel.total_cost > cost):
            metrics_parts.append(f"total: {tel.total_tokens}t")
            if tel.total_cost > 0:
                metrics_parts.append(f"${tel.total_cost:.2f}")

        metrics_str = ", ".join(metrics_parts) if metrics_parts else ""
        model_part = f" [{model}]" if model else ""
        
        # Добавляем статус графа если есть
        graph_status_part = ""
        if node.get("graph_status"):
            gs = node["graph_status"]
            if gs == "blocked":
                graph_status_part = " 🔒"
            elif gs == "ready":
                graph_status_part = " 🔓"
            elif gs == "pending":
                graph_status_part = " ⏳"

        if status == "running" and node.get("reasoning", ""):
            reasoning = node.get("reasoning", "") or ""
            short_reason = reasoning[:40] + ("..." if len(reasoning) > 40 else "")
            node_line = f"{icon} {goal}{model_part}{graph_status_part}{deps_info} ({elapsed}"
            if metrics_str:
                node_line += f", {metrics_str}"
            node_line += ")"
            reason_line = f"{indent}   ┈ {short_reason}"
        elif last_tool and status == "running":
            node_line = f"{icon} {goal}{model_part}{graph_status_part}{deps_info} ({elapsed}"
            if metrics_str:
                node_line += f", {metrics_str}"
            node_line += f", {last_tool})"
            reason_line = None
        else:
            node_line = f"{icon} {goal}{model_part}{graph_status_part}{deps_info} ({elapsed}"
            if metrics_str:
                node_line += f", {metrics_str}"
            node_line += ")"
            reason_line = None

        line = f"{indent}{node_line}"
        if len(line) > max_tree_width:
            line = line[: max_tree_width - 3] + "..."

        parts.append(line)

        if reason_line:
            parts.append(reason_line)

        cid = node.get("subagent_id")
        children = children_by_parent.get(cid, [])
        if children:
            child_prefix = prefix + ("    " if is_last else "│   ")
            for i, child in enumerate(children):
                child_is_last = i == len(children) - 1
                _render_node(child, prefix=child_prefix, is_last=child_is_last)

    root_ids = [rid for rid in by_id if by_id[rid].get("parent_id") is None]
    for root_id in root_ids:
        _render_node(by_id[root_id], prefix="", is_last=True)

    if total_tools > 0 or total_tokens > 0:
        summary = format_total_metrics(total_tools, total_tokens, total_cost)
        parts.append(f"\n{summary}")

    return "\n".join(parts)
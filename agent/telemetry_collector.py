"""
Telemetry Collector for Hercules Agent.

Provides granular telemetry per agent and rollup metrics that aggregate
direct costs + all descendants in the subagent tree.
"""

import time
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional


@dataclass
class AgentTelemetry:
    """Telemetry for a single agent with rollup support."""
    agent_id: str
    agent_name: str
    parent_id: Optional[str] = None

    # Direct metrics
    execution_time: float = 0.0
    tokens_input: int = 0
    tokens_output: int = 0
    tools_called: int = 0
    cost_usd: float = 0.0

    # Children tracking
    children: List[str] = field(default_factory=list)

    # Rollup metrics (populated recursively)
    total_tokens: int = 0
    total_cost: float = 0.0
    total_tools: int = 0
    total_time: float = 0.0

    def __post_init__(self):
        """Initialize rollup metrics from direct metrics if not set."""
        if self.total_tokens == 0:
            self.total_tokens = self.tokens_input + self.tokens_output
        if self.total_cost == 0.0:
            self.total_cost = self.cost_usd
        if self.total_tools == 0:
            self.total_tools = self.tools_called
        if self.total_time == 0.0:
            self.total_time = self.execution_time


def calculate_rollup_metrics(
    agent_id: str,
    telemetry_dict: Dict[str, AgentTelemetry]
) -> AgentTelemetry:
    """
    Recursively calculate rollup metrics for an agent.

    Sums direct metrics + all descendants' metrics.
    Updates the agent's rollup fields in-place and returns the agent.
    """
    agent = telemetry_dict[agent_id]

    # Start with direct metrics
    total_tokens = agent.tokens_input + agent.tokens_output
    total_cost = agent.cost_usd
    total_tools = agent.tools_called
    total_time = agent.execution_time

    # Recursively add all children's rollup metrics
    for child_id in agent.children:
        if child_id in telemetry_dict:
            child_rollup = calculate_rollup_metrics(child_id, telemetry_dict)
            total_tokens += child_rollup.total_tokens
            total_cost += child_rollup.total_cost
            total_tools += child_rollup.total_tools
            total_time += child_rollup.total_time

    # Update rollup fields
    agent.total_tokens = total_tokens
    agent.total_cost = total_cost
    agent.total_tools = total_tools
    agent.total_time = total_time

    return agent


def format_agent_metrics(agent: AgentTelemetry) -> str:
    """
    Format: Agent A: 50 tokens, Subagent X: 30 tokens, Total: 80 tokens

    Shows the agent's direct tokens and total including descendants.
    """
    direct_tokens = agent.tokens_input + agent.tokens_output
    children_tokens = agent.total_tokens - direct_tokens

    parts = [f"{agent.agent_name}: {direct_tokens} tokens"]
    if children_tokens > 0:
        parts.append(f"Subagents: {children_tokens} tokens")
    parts.append(f"Total: {agent.total_tokens} tokens")

    return ", ".join(parts)


def format_total_metrics(agent: AgentTelemetry) -> str:
    """
    Format: Общее: 23 tools called · 102,176 tokens · $0.10

    Shows aggregate metrics for the agent including all descendants.
    """
    # Format token count with commas for thousands
    tokens_str = f"{agent.total_tokens:,}" if agent.total_tokens >= 1000 else str(agent.total_tokens)

    parts = [f"{agent.total_tools} tools called", f"{tokens_str} tokens"]

    # Always show cost, format as $0.00 for zero
    cost_str = f"${agent.total_cost:.2f}"
    parts.append(cost_str)

    return "Общее: " + " · ".join(parts)


class TelemetryCollector:
    """
    Collects telemetry during agent execution.

    Usage:
        collector = TelemetryCollector(agent_id="agent-123")
        # ... during execution ...
        collector.add_tokens(input_tokens=100, output_tokens=50)
        collector.add_tool_call(cost=0.05)
        # ... at end ...
        telemetry = collector.finalize()
    """

    def __init__(self, agent_id: str, agent_name: str = "", parent_id: Optional[str] = None):
        self.agent_id = agent_id
        self.agent_name = agent_name or agent_id
        self.parent_id = parent_id
        self.start_time = time.time()
        self.tokens_input = 0
        self.tokens_output = 0
        self.tools_called = 0
        self.cost_usd = 0.0
        self._children: List[str] = []

    def add_tokens(self, input_tokens: int, output_tokens: int) -> None:
        """Add token usage."""
        self.tokens_input += input_tokens
        self.tokens_output += output_tokens

    def add_tool_call(self, cost: float = 0.0) -> None:
        """Record a tool call with optional cost."""
        self.tools_called += 1
        self.cost_usd += cost

    def add_child(self, child_id: str) -> None:
        """Register a child agent."""
        if child_id not in self._children:
            self._children.append(child_id)

    def finalize(self) -> AgentTelemetry:
        """
        Create an AgentTelemetry object upon completion.

        Calculates execution time and populates all fields.
        """
        execution_time = time.time() - self.start_time
        return AgentTelemetry(
            agent_id=self.agent_id,
            agent_name=self.agent_name,
            parent_id=self.parent_id,
            execution_time=execution_time,
            tokens_input=self.tokens_input,
            tokens_output=self.tokens_output,
            tools_called=self.tools_called,
            cost_usd=self.cost_usd,
            children=self._children.copy(),
            # Rollup fields initialized from direct metrics
            total_tokens=self.tokens_input + self.tokens_output,
            total_cost=self.cost_usd,
            total_tools=self.tools_called,
            total_time=execution_time,
        )


def build_telemetry_tree(
    root_agent_id: str,
    telemetry_dict: Dict[str, AgentTelemetry]
) -> Dict[str, Any]:
    """
    Build a tree structure from telemetry dict for display purposes.

    Returns a nested dict with 'agent' and 'children' keys.
    """
    if root_agent_id not in telemetry_dict:
        return {}

    # First calculate all rollup metrics
    calculate_rollup_metrics(root_agent_id, telemetry_dict)

    def _build_node(agent_id: str) -> Dict[str, Any]:
        agent = telemetry_dict[agent_id]
        node = {
            "agent": agent,
            "children": []
        }
        for child_id in agent.children:
            if child_id in telemetry_dict:
                node["children"].append(_build_node(child_id))
        return node

    return _build_node(root_agent_id)

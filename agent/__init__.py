"""Agent internals -- extracted modules from run_agent.py.

These modules contain pure utility functions and self-contained classes
that were previously embedded in the 3,600-line run_agent.py. Extracting
them makes run_agent.py focused on the AIAgent orchestrator class.
"""

# Meta-Analysis and Dynamic Agent Creation
from agent.meta_analysis import MetaAnalysisAgent
from agent.agent_factory import (
    AgentFactory,
    DYNAMIC_AGENTS,
    register_dynamic_agent,
    get_dynamic_agent,
    list_dynamic_agents,
    load_dynamic_agents_on_startup,
)

# Self-Evaluation and Autonomy Engine
from agent.self_evaluation import SelfEvaluation
from agent.autonomy_engine import AutonomyEngine

__all__ = [
    "MetaAnalysisAgent",
    "AgentFactory",
    "DYNAMIC_AGENTS",
    "register_dynamic_agent",
    "get_dynamic_agent",
    "list_dynamic_agents",
    "load_dynamic_agents_on_startup",
    "SelfEvaluation",
    "AutonomyEngine",
]

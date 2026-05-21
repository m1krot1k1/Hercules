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

# Checkpoint Manager
from agent.checkpoint_manager import (
    AgentCheckpoint,
    save_checkpoint,
    load_checkpoint,
    list_checkpoints,
)

# Swarm Bus
from agent.swarm_bus import (
    SwarmBus,
    SwarmMessage,
    MessagePriority,
    get_swarm_bus,
    publish,
    subscribe,
    get_messages,
)

# Dependency Graph
from agent.dependency_graph import (
    TaskDependencyGraph,
    TaskStatus,
    TaskNode,
    get_dependency_graph,
)

# Personality Manager
from agent.personality_manager import (
    PersonalityManager,
    Personality,
    PersonalityType,
    get_personality_manager,
    get_personality_prompt,
    apply_personality_to_system_prompt,
)

# Achievement System
from agent.achievement_system import (
    AchievementSystem,
    Achievement,
    AchievementTier,
    get_achievement_system,
    check_achievements,
    unlock_achievement,
    get_unlocked_achievements,
)

__all__ = [
    # Meta-Analysis and Dynamic Agent Creation
    "MetaAnalysisAgent",
    "AgentFactory",
    "DYNAMIC_AGENTS",
    "register_dynamic_agent",
    "get_dynamic_agent",
    "list_dynamic_agents",
    "load_dynamic_agents_on_startup",
    # Self-Evaluation and Autonomy Engine
    "SelfEvaluation",
    "AutonomyEngine",
    # Checkpoint Manager
    "AgentCheckpoint",
    "save_checkpoint",
    "load_checkpoint",
    "list_checkpoints",
    # Swarm Bus
    "SwarmBus",
    "SwarmMessage",
    "MessagePriority",
    "get_swarm_bus",
    "publish",
    "subscribe",
    "get_messages",
    # Dependency Graph
    "TaskDependencyGraph",
    "TaskStatus",
    "TaskNode",
    "get_dependency_graph",
    # Personality Manager
    "PersonalityManager",
    "Personality",
    "PersonalityType",
    "get_personality_manager",
    "get_personality_prompt",
    "apply_personality_to_system_prompt",
    # Achievement System
    "AchievementSystem",
    "Achievement",
    "AchievementTier",
    "get_achievement_system",
    "check_achievements",
    "unlock_achievement",
    "get_unlocked_achievements",
]

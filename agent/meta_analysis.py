"""
Meta-Analysis Subagent -- Dynamic Agent Creation System

Analyzes tasks to determine if a specialized agent is needed, and if so,
generates the agent specification and coordinates with the AgentFactory.
"""

import json
import logging
import os
from pathlib import Path
from typing import Any, Dict, List, Optional

from hermes_constants import get_hermes_home

logger = logging.getLogger(__name__)


class MetaAnalysisAgent:
    """Analyzes the need for a specialized agent and generates agent specifications.
    
    This agent is called right after the Orchestrator's task decomposition
    to determine if any of the decomposed tasks require a specialist that
    doesn't exist yet.
    """
    
    def __init__(self, model: str = None, provider: str = None):
        """Initialize the MetaAnalysisAgent.
        
        Args:
            model: The model to use for analysis (optional, uses default if None)
            provider: The provider to use (optional, uses default if None)
        """
        self.model = model
        self.provider = provider
        self.agents_dir = get_hermes_home() / "agents"
        
    def analyze_task(self, goal: str, context: str, available_agents: List[str]) -> Dict[str, Any]:
        """Analyze whether a specialized agent is needed for the given task.
        
        Args:
            goal: The goal/objective of the task
            context: Additional context about the task
            available_agents: List of already available agent names
            
        Returns:
            Dict with keys:
                - need_specialist: bool
                - specialist_type: str or None
                - reasoning: str
                - suggested_tools: list or None
        """
        # Build the analysis prompt
        prompt = self._build_analysis_prompt(goal, context, available_agents)
        
        # In a real implementation, this would call the LLM
        # For now, we'll implement a basic heuristic-based analysis
        # that can be replaced with LLM calls later
        
        result = self._heuristic_analysis(goal, context, available_agents)
        return result
    
    def generate_agent_spec(self, specialist_type: str, goal: str) -> Dict[str, Any]:
        """Generate an agent specification for creating a new specialist.
        
        Args:
            specialist_type: The type of specialist to create (e.g., "rust-specialist")
            goal: The goal/objective this specialist will handle
            
        Returns:
            Dict with keys:
                - name: "specialist-name"
                - description: "..."
                - system_prompt: "..."  # Contents for agents/specialist-name.md
                - toolsets: [...]
                - role: "leaf" or "orchestrator"
        """
        # Build the generation prompt
        prompt = self._build_generation_prompt(specialist_type, goal)
        
        # In a real implementation, this would call the LLM
        # For now, we'll create a basic template-based spec
        return self._template_agent_spec(specialist_type, goal)
    
    def _build_analysis_prompt(self, goal: str, context: str, available_agents: List[str]) -> str:
        """Build the prompt for analyzing if a specialist is needed."""
        agents_list = "\n".join(f"- {agent}" for agent in sorted(available_agents))
        return f"""# Meta-Analysis: Specialist Need Assessment

## Task Goal
{goal}

## Context
{context}

## Available Agents
{agents_list if agents_list else "No agents available"}

## Instructions
Analyze the task and determine:
1. Does this task require domain-specific knowledge or tools that existing agents don't have?
2. Is there a clear specialist type that would be beneficial?
3. What tools would this specialist need?

Return a JSON object with:
- need_specialist: boolean
- specialist_type: string or null (kebab-case name like "rust-specialist")
- reasoning: string (explanation)
- suggested_tools: array of toolset names or null
"""
    
    def _build_generation_prompt(self, specialist_type: str, goal: str) -> str:
        """Build the prompt for generating an agent specification."""
        return f"""# Agent Specification Generation

## Specialist Type
{specialist_type}

## Goal
{goal}

## Instructions
Generate a complete agent specification including:
1. A clear system prompt for the agent (to be saved in agents/{specialist_type}.md)
2. The optimal toolsets for this agent
3. Whether this should be a "leaf" or "orchestrator" role

Return a JSON object with:
- name: "{specialist_type}"
- description: "One-line description"
- system_prompt: "Full system prompt content for the .md file"
- toolsets: array of toolset names
- role: "leaf" or "orchestrator"
"""
    
    def _heuristic_analysis(self, goal: str, context: str, available_agents: List[str]) -> Dict[str, Any]:
        """Basic heuristic-based analysis (placeholder for LLM-based analysis).
        
        This method provides a simple rule-based analysis that can be
        replaced with actual LLM calls in production.
        """
        goal_lower = goal.lower()
        context_lower = context.lower() if context else ""
        combined = f"{goal_lower} {context_lower}"
        
        # Check for common specialist needs based on keywords
        specialist_keywords = {
            "rust": "rust-specialist",
            "go ": "go-specialist", 
            "golang": "go-specialist",
            "ios": "ios-specialist",
            "swift": "ios-specialist",
            "android": "android-specialist",
            "kotlin": "android-specialist",
            "blockchain": "blockchain-specialist",
            "solidity": "blockchain-specialist",
            "smart contract": "blockchain-specialist",
            "ml": "ml-specialist",
            "machine learning": "ml-specialist",
            "tensorflow": "ml-specialist",
            "pytorch": "ml-specialist",
            "graphql": "graphql-specialist",
            "grpc": "grpc-specialist",
            "microservice": "microservices-specialist",
        }
        
        for keyword, specialist in specialist_keywords.items():
            if keyword in combined:
                # Check if this specialist already exists
                if specialist in available_agents or f"{specialist}" in available_agents:
                    continue
                return {
                    "need_specialist": True,
                    "specialist_type": specialist,
                    "reasoning": f"Task involves {keyword} which requires specialized knowledge. No existing {specialist} found.",
                    "suggested_tools": self._suggest_toolsets_for_specialist(specialist),
                }
        
        return {
            "need_specialist": False,
            "specialist_type": None,
            "reasoning": "No clear need for a specialist based on current analysis.",
            "suggested_tools": None,
        }
    
    def _suggest_toolsets_for_specialist(self, specialist_type: str) -> List[str]:
        """Suggest toolsets based on specialist type."""
        toolset_map = {
            "rust-specialist": ["terminal", "file", "web", "code_execution"],
            "go-specialist": ["terminal", "file", "web", "code_execution"],
            "ios-specialist": ["terminal", "file", "web"],
            "android-specialist": ["terminal", "file", "web"],
            "blockchain-specialist": ["terminal", "file", "web", "code_execution"],
            "ml-specialist": ["terminal", "file", "web", "code_execution"],
            "graphql-specialist": ["terminal", "file", "web", "code_execution"],
            "grpc-specialist": ["terminal", "file", "web"],
            "microservices-specialist": ["terminal", "file", "web", "delegation"],
        }
        return toolset_map.get(specialist_type, ["terminal", "file", "web"])
    
    def _template_agent_spec(self, specialist_type: str, goal: str) -> Dict[str, Any]:
        """Generate a template-based agent specification."""
        # Clean up the specialist type for display
        display_name = specialist_type.replace("-", " ").title()
        
        system_prompt = f"""# {display_name}

## Role
You are a specialized agent focused on {display_name} tasks. Your expertise covers the specific domain and tools required for this type of work.

## Goal
{goal}

## Constraints
- Focus only on tasks within your specialization domain
- Use appropriate tools for your domain
- Delegate tasks outside your expertise to other agents
- Follow best practices for {display_name} development

## Tools
{self._format_toolsets(self._suggest_toolsets_for_specialist(specialist_type))}

## Instructions
1. Analyze the task to understand the specific requirements
2. Use domain-appropriate tools and techniques
3. Follow best practices and coding standards for {display_name}
4. Provide clear documentation and explanations
5. If the task is outside your domain, request delegation to a more appropriate agent
"""
        
        return {
            "name": specialist_type,
            "description": f"Specialized agent for {display_name} tasks",
            "system_prompt": system_prompt,
            "toolsets": self._suggest_toolsets_for_specialist(specialist_type),
            "role": "leaf",  # Most specialists are leaves, not orchestrators
        }
    
    def _format_toolsets(self, toolsets: List[str]) -> str:
        """Format toolsets list for markdown."""
        return "\n".join(f"- `{toolset}`" for toolset in toolsets)
    
    def load_available_agents(self) -> List[str]:
        """Load the list of available agents from the agents/ directory."""
        agents = []
        if not self.agents_dir.exists():
            return agents
        
        for agent_file in self.agents_dir.glob("*.md"):
            # Skip README and other non-agent files
            if agent_file.stem in ["README", "specialist-analyzer", "subagent-factory"]:
                continue
            agents.append(agent_file.stem)
        
        return sorted(agents)

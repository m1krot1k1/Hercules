"""
Agent Factory -- Dynamic Agent Creation System

Dynamically creates agent definition files, registers them in the
delegation system, and updates the agents/README.md.
"""

import json
import logging
import os
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

from hermes_constants import get_hermes_home

logger = logging.getLogger(__name__)

# Module-level registry for dynamic agents
# This is populated at startup by load_dynamic_agents() and
# can be updated at runtime by register_dynamic_agent()
DYNAMIC_AGENTS: Dict[str, Dict[str, Any]] = {}


class AgentFactory:
    """Dynamically creates and registers agents at runtime."""
    
    def __init__(self, model: str = None, provider: str = None):
        """Initialize the AgentFactory.
        
        Args:
            model: The model to use for agent generation (optional)
            provider: The provider to use (optional)
        """
        self.model = model
        self.provider = provider
        self.agents_dir = get_hermes_home() / "agents"
        self.readme_path = self.agents_dir / "README.md"
        
    def create_agent_file(self, agent_spec: Dict[str, Any]) -> str:
        """Create agents/<name>.md, returns the file path.
        
        Args:
            agent_spec: Dict with keys:
                - name: "specialist-name"
                - description: "..."
                - system_prompt: "..."  # Contents for agents/specialist-name.md
                - toolsets: [...]
                - role: "leaf" or "orchestrator"
                
        Returns:
            Path to the created agent file
        """
        name = agent_spec.get("name", "").strip()
        if not name:
            raise ValueError("agent_spec must contain 'name'")
            
        # Sanitize name for filename (kebab-case)
        filename = name.lower().replace(" ", "-").replace("_", "-")
        if not filename.endswith(".md"):
            filename += ".md"
            
        agent_file = self.agents_dir / filename
        
        # Use system_prompt if provided, otherwise generate from spec
        content = agent_spec.get("system_prompt")
        if not content:
            content = self._generate_agent_content(agent_spec)
        
        # Write the agent file
        agent_file.write_text(content, encoding="utf-8")
        logger.info(f"Created agent file: {agent_file}")
        
        return str(agent_file.relative_to(get_hermes_home()))
    
    def register_agent(self, agent_name: str, agent_spec: Dict[str, Any]):
        """Register an agent in the delegation system.
        
        This makes the agent available for delegate_task() calls.
        
        Args:
            agent_name: The name of the agent (kebab-case)
            agent_spec: The agent specification dict
        """
        global DYNAMIC_AGENTS
        
        DYNAMIC_AGENTS[agent_name] = {
            "name": agent_name,
            "spec": agent_spec,
            "registered_at": datetime.utcnow().isoformat(),
            "file_path": str(self.agents_dir / f"{agent_name}.md"),
        }
        
        logger.info(f"Registered dynamic agent: {agent_name}")
        
        # In a full implementation, this would also update
        # tools/delegate_tool.py's agent resolution logic
        # For now, we store in the module-level registry
        
    def update_readme(self, agent_name: str, description: str):
        """Update agents/README.md with information about the new agent.
        
        Args:
            agent_name: The name of the agent
            description: Brief description of the agent
        """
        if not self.readme_path.exists():
            logger.warning(f"README.md not found at {self.readme_path}")
            return
            
        content = self.readme_path.read_text(encoding="utf-8")
        
        # Check if agent already listed
        if f"agents/{agent_name}.md" in content:
            logger.info(f"Agent {agent_name} already in README.md")
            return
            
        # Find the Agents section and add the new agent
        # This is a simple implementation - in production you'd want
        # more sophisticated markdown parsing
        agent_entry = f"\n| **{agent_name}** | {description} | Dynamically created specialist |\n"
        
        # Try to find the Agents table and append
        if "## 🚀" in content or "## Central Intelligence" in content:
            # Find the table and append
            lines = content.split("\n")
            new_lines = []
            table_found = False
            for i, line in enumerate(lines):
                new_lines.append(line)
                if "| Agent | Role |" in line or "|---|---|" in line:
                    table_found = True
                elif table_found and line.strip() and not line.strip().startswith("|"):
                    # End of table, insert before this line
                    new_lines.append(agent_entry.strip())
                    table_found = False
                elif table_found and i == len(lines) - 1:
                    # End of file, append
                    new_lines.append(agent_entry.strip())
                    
            content = "\n".join(new_lines)
            self.readme_path.write_text(content, encoding="utf-8")
            logger.info(f"Updated README.md with agent: {agent_name}")
        else:
            # Append at the end
            content += f"\n\n## Dynamically Created Agents\n{agent_entry}"
            self.readme_path.write_text(content, encoding="utf-8")
            logger.info(f"Appended to README.md with agent: {agent_name}")
    
    def load_dynamic_agents(self):
        """Load dynamically created agents at startup.
        
        Scans the agents/ directory for agent files that were
        dynamically created and registers them in DYNAMIC_AGENTS.
        """
        global DYNAMIC_AGENTS
        
        if not self.agents_dir.exists():
            logger.warning(f"Agents directory not found: {self.agents_dir}")
            return
            
        # Look for marker files or metadata that indicate dynamic creation
        # For now, we'll check all .md files and skip the known ones
        known_agents = {
            "orchestrator", "start", "meta-agent-architect", 
            "subagent-factory", "specialist-analyzer", "README"
        }
        
        for agent_file in self.agents_dir.glob("*.md"):
            agent_name = agent_file.stem
            if agent_name in known_agents:
                continue
                
            # Check if this is a dynamically created agent
            # (In production, you might have a metadata section or marker)
            try:
                content = agent_file.read_text(encoding="utf-8")
                # Simple heuristic: if it has certain markers or was created
                # by the AgentFactory, register it
                if agent_name not in DYNAMIC_AGENTS:
                    DYNAMIC_AGENTS[agent_name] = {
                        "name": agent_name,
                        "spec": self._parse_agent_file(agent_file),
                        "registered_at": datetime.utcnow().isoformat(),
                        "file_path": str(agent_file),
                        "loaded_at_startup": True,
                    }
                    logger.info(f"Loaded dynamic agent at startup: {agent_name}")
            except Exception as e:
                logger.error(f"Error loading agent {agent_name}: {e}")
        
        logger.info(f"Loaded {len(DYNAMIC_AGENTS)} dynamic agents")
    
    def create_full_agent(self, agent_spec: Dict[str, Any]) -> Dict[str, Any]:
        """Create a complete agent: file + registration + README update.
        
        Args:
            agent_spec: The agent specification
            
        Returns:
            Dict with keys: file_path, registered, readme_updated
        """
        result = {
            "file_path": None,
            "registered": False,
            "readme_updated": False,
        }
        
        # 1. Create agent file
        try:
            file_path = self.create_agent_file(agent_spec)
            result["file_path"] = file_path
        except Exception as e:
            logger.error(f"Failed to create agent file: {e}")
            return result
            
        # 2. Register agent
        try:
            self.register_agent(agent_spec["name"], agent_spec)
            result["registered"] = True
        except Exception as e:
            logger.error(f"Failed to register agent: {e}")
            
        # 3. Update README
        try:
            description = agent_spec.get("description", "Dynamically created specialist")
            self.update_readme(agent_spec["name"], description)
            result["readme_updated"] = True
        except Exception as e:
            logger.error(f"Failed to update README: {e}")
            
        return result
    
    def _generate_agent_content(self, agent_spec: Dict[str, Any]) -> str:
        """Generate the content for an agent .md file."""
        name = agent_spec.get("name", "unknown")
        description = agent_spec.get("description", "")
        toolsets = agent_spec.get("toolsets", [])
        role = agent_spec.get("role", "leaf")
        
        # Format toolsets
        toolsets_str = "\n".join(f"- `{t}`" for t in toolsets) if toolsets else "- (none specified)"
        
        content = f"""# {name.replace("-", " ").title()} Agent

## Role
{description}

## Goal
{agent_spec.get("goal", "Handle specialized tasks in this domain")}

## Constraints
- Stay within your domain of expertise
- Use only the tools appropriate for your specialization
- Delegate tasks outside your scope to other agents
- Follow best practices for your domain

## Tools
{toolsets_str}

## Instructions
1. Analyze the task to understand requirements
2. Apply domain-specific knowledge and tools
3. Follow best practices and coding standards
4. Provide clear documentation
5. If the task is outside your domain, request delegation

## Metadata
- Type: Dynamically created specialist
- Role: {role}
- Created: {datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC")}
"""
        return content
    
    def _parse_agent_file(self, agent_file: Path) -> Dict[str, Any]:
        """Parse an agent .md file to extract the spec."""
        try:
            content = agent_file.read_text(encoding="utf-8")
            # Simple parsing - extract key information
            spec = {
                "name": agent_file.stem,
                "system_prompt": content,
                "description": "",
                "toolsets": [],
                "role": "leaf",
            }
            
            # Extract description from first heading or Role section
            for line in content.split("\n"):
                if line.startswith("## Role"):
                    # Next non-empty line might be the description
                    pass
                    
            return spec
        except Exception as e:
            logger.error(f"Error parsing agent file {agent_file}: {e}")
            return {"name": agent_file.stem, "system_prompt": ""}


def register_dynamic_agent(name: str, spec: Dict[str, Any]):
    """Module-level function to register a dynamic agent.
    
    This can be called from tools/delegate_tool.py to register
    new agents at runtime.
    """
    global DYNAMIC_AGENTS
    DYNAMIC_AGENTS[name] = {
        "name": name,
        "spec": spec,
        "registered_at": datetime.utcnow().isoformat(),
    }
    logger.info(f"Dynamically registered agent: {name}")


def get_dynamic_agent(name: str) -> Optional[Dict[str, Any]]:
    """Get a dynamically registered agent by name."""
    return DYNAMIC_AGENTS.get(name)


def list_dynamic_agents() -> List[str]:
    """List all dynamically registered agent names."""
    return list(DYNAMIC_AGENTS.keys())


def load_dynamic_agents_on_startup():
    """Call this at system startup to load dynamic agents."""
    factory = AgentFactory()
    factory.load_dynamic_agents()

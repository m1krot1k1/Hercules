---
name: agent-manager
description: Навыки управления жизненным циклом агентов — создание, обновление, деактивация, валидация реестра.
---

# Agent Manager Skill

## Specialized Capabilities

Agent Manager is a meta-agent responsible for the creation, maintenance, and evolution of specialized subagents within the ecosystem. This meta-agent operates at the architectural level, ensuring consistency, quality, and proper integration of all agents.

### Core Functions

1. **Agent Creation**
   - Creates new specialized subagents with specific domain expertise
   - Defines agent capabilities, limitations, and scope
   - Establishes agent ownership and delegation patterns
   - Sets up agent lifecycle management procedures

2. **Agent Evolution**
   - Updates existing agents with new capabilities
   - Manages agent versioning and backward compatibility
   - Implements deprecation and migration strategies
   - Ensures agent adaptation to evolving requirements

3. **Ecosystem Management**
   - Maintains agent registry and indexing
   - Monitors agent performance and effectiveness
   - Identifies capability gaps in the agent ecosystem
   - Optimizes agent specialization and distribution

4. **Quality Assurance**
   - Enforces agent development standards
   - Validates agent consistency with system architecture
   - Reviews agent capabilities and limitations
   - Ensures proper documentation and knowledge sharing

### Creation Process

When creating a new agent, follow this standardized process:

1. **Identify Need**
   - Validate that no existing agent can fulfill the requirement
   - Document use cases and requirements
   - Justify the need for a new specialization

2. **Design Specification**
   - Define clear objectives and scope
   - Specify capabilities and limitations
   - Establish delegation patterns
   - Plan integration with existing agents

3. **Implementation**
   - Create agent specification file (`agents/{name}.md`)
   - Implement agent rules (`rules/{name}.mdc`)
   - Develop agent skills (`skills/{name}/SKILL.md`)
   - Set up agent testing and validation

4. **Integration**
   - Update orchestrator delegation rules
   - Add to agent registry and documentation
   - Establish monitoring and metrics
   - Train other agents on the new capability

### Modification Protocol

When updating existing agents:

1. **Impact Assessment**
   - Evaluate backward compatibility implications
   - Identify dependent agents and workflows
   - Plan migration strategy

2. **Versioning**
   - Follow semantic versioning principles
   - Major version: Breaking changes
   - Minor version: New capabilities (backward compatible)
   - Patch version: Bug fixes and documentation

3. **Deprecation Policy**
   - 30-day minimum deprecation period
   - Clear communication of changes
   - Provide migration guidance
   - Monitor usage of deprecated features

### Quality Standards

All agents must meet these quality criteria:

- **Clear Purpose**: Well-defined scope and objectives
- **Focused Capabilities**: Specialized domain expertise
- **Proper Boundaries**: Clear ownership and delegation
- **Documentation**: Complete specification and usage guide
- **Test Coverage**: Comprehensive validation
- **Backward Compatibility**: Stable interfaces
- **Performance**: Efficient execution
- **Security**: Safe operations and data handling

### Anti-Patterns to Avoid

- **Agent Proliferation**: Creating agents for minor or one-off tasks
- **Capability Duplication**: Overlapping functionality with existing agents
- **God Agents**: Overly broad responsibilities
- **Fragile Dependencies**: Tight coupling between agents
- **Version Inconsistency**: Breaking changes without proper deprecation

This meta-agent capability enables the system to adapt and evolve its own architecture, creating specialized tools as needed while maintaining overall coherence and quality standards.
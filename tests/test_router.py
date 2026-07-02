import pytest
from orchestrator.agent import orchestrator_agent
from orchestrator.prompts import ORCHESTRATOR_SYSTEM_PROMPT

def test_orchestrator_initialization():
    """Verifies that the Orchestrator agent loads and configures subagents correctly."""
    assert orchestrator_agent.name == "Atlas"
    assert orchestrator_agent.instruction == ORCHESTRATOR_SYSTEM_PROMPT
    
    # Check that specialist agents are configured as subagents
    sub_agent_names = [agent.name for agent in orchestrator_agent.sub_agents]
    assert "Scheduler" in sub_agent_names
    assert "Study" in sub_agent_names
    assert "Comms" in sub_agent_names
    assert "Memory" in sub_agent_names

def test_specialist_agent_descriptions():
    """Verifies that specialist agent descriptions exist so that Orchestrator can route properly."""
    for agent in orchestrator_agent.sub_agents:
        assert agent.description is not None
        assert len(agent.description) > 0

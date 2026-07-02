import os
from google.adk.agents import Agent
from google.adk.models.google_llm import Gemini
from google.adk.models.lite_llm import LiteLlm
from orchestrator.prompts import ORCHESTRATOR_SYSTEM_PROMPT
from agents.scheduler import scheduler_agent
from agents.study import study_agent
from agents.comms import comms_agent
from agents.memory import memory_agent

def get_model():
    if os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY"):
        return Gemini(model_id="gemini-2.5-flash")
    elif os.getenv("ANTHROPIC_API_KEY"):
        return LiteLlm(model="anthropic/claude-3-5-sonnet-20241022")
    else:
        return Gemini(model_id="gemini-2.5-flash")

# Define the primary orchestrator chief of staff agent
orchestrator_agent = Agent(
    name="Atlas",
    model=get_model(),
    instruction=ORCHESTRATOR_SYSTEM_PROMPT,
    sub_agents=[scheduler_agent, study_agent, comms_agent, memory_agent]
)

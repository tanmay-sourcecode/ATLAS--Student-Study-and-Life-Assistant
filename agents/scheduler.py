import os
from google.adk.agents import Agent
from google.adk.models.google_llm import Gemini
from google.adk.models.lite_llm import LiteLlm
from orchestrator.prompts import SCHEDULER_SYSTEM_PROMPT
from tools import get_calendar_events, add_calendar_event, get_tasks, add_task, update_task_status

def get_model():
    if os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY"):
        return Gemini(model_id="gemini-2.5-flash")
    elif os.getenv("ANTHROPIC_API_KEY"):
        return LiteLlm(model="anthropic/claude-3-5-sonnet-20241022")
    else:
        return Gemini(model_id="gemini-2.5-flash")

scheduler_agent = Agent(
    name="Scheduler",
    model=get_model(),
    instruction=SCHEDULER_SYSTEM_PROMPT,
    description="Manages student schedule, calendar events, tasks, assignments, deadlines, and study blocks.",
    tools=[get_calendar_events, add_calendar_event, get_tasks, add_task, update_task_status]
)

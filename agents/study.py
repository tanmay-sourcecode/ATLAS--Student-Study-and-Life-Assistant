import os
from google.adk.agents import Agent
from google.adk.models.google_llm import Gemini
from google.adk.models.lite_llm import LiteLlm
from orchestrator.prompts import STUDY_SYSTEM_PROMPT
from rag.ingest import ingest
from rag.retrieve import retrieve

def get_model():
    if os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY"):
        return Gemini(model_id="gemini-2.5-flash")
    elif os.getenv("ANTHROPIC_API_KEY"):
        return LiteLlm(model="anthropic/claude-3-5-sonnet-20241022")
    else:
        return Gemini(model_id="gemini-2.5-flash")

study_agent = Agent(
    name="Study",
    model=get_model(),
    instruction=STUDY_SYSTEM_PROMPT,
    description="Summarizes syllabus/lecture materials, generates study plans, and answers study questions grounded in documents (with citations).",
    tools=[ingest, retrieve]
)

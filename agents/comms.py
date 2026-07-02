import os
from google.adk.agents import Agent
from google.adk.models.google_llm import Gemini
from google.adk.models.lite_llm import LiteLlm
from orchestrator.prompts import COMMS_SYSTEM_PROMPT
from tools import create_email_draft, get_email_drafts, approve_and_send_email

def get_model():
    if os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY"):
        return Gemini(model_id="gemini-2.5-flash")
    elif os.getenv("ANTHROPIC_API_KEY"):
        return LiteLlm(model="anthropic/claude-3-5-sonnet-20241022")
    else:
        return Gemini(model_id="gemini-2.5-flash")

comms_agent = Agent(
    name="Comms",
    model=get_model(),
    instruction=COMMS_SYSTEM_PROMPT,
    description="Drafts respectful academic emails and communications to professors, TAs, or teammates. Requires human-in-the-loop approval.",
    tools=[create_email_draft, get_email_drafts, approve_and_send_email]
)

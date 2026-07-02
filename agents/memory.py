import os
import json
from google.adk.agents import Agent
from google.adk.models.google_llm import Gemini
from google.adk.models.lite_llm import LiteLlm
from orchestrator.prompts import MEMORY_SYSTEM_PROMPT
from security.pii import redact_pii

DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "demo_data")
MEMORY_FILE = os.path.join(DATA_DIR, "memories.json")

def ensure_memory_file_exists():
    if not os.path.exists(DATA_DIR):
        os.makedirs(DATA_DIR)
    if not os.path.exists(MEMORY_FILE):
        default_memories = [
            {"id": "1", "fact": "Prefers study blocks in the morning between 9 AM and 12 PM."},
            {"id": "2", "fact": "Taking CS 3110 (Advanced Programming) and MATH 2940 (Linear Algebra)."}
        ]
        with open(MEMORY_FILE, "w") as f:
            json.dump(default_memories, f, indent=4)

ensure_memory_file_exists()

# ----------------- Memory Tools -----------------

def get_memories() -> str:
    """Retrieves all stored long-term preferences and facts about the student."""
    try:
        ensure_memory_file_exists()
        with open(MEMORY_FILE, "r") as f:
            memories = json.load(f)
        return json.dumps(memories, indent=2)
    except Exception as e:
        return f"Error retrieving memories: {str(e)}"

def add_memory(fact: str) -> str:
    """Stores a new student preference or fact. Automatically redacts PII before saving."""
    try:
        ensure_memory_file_exists()
        # Redact PII first
        clean_fact = redact_pii(fact)
        
        with open(MEMORY_FILE, "r") as f:
            memories = json.load(f)
            
        new_memory = {
            "id": str(len(memories) + 1),
            "fact": clean_fact
        }
        memories.append(new_memory)
        
        with open(MEMORY_FILE, "w") as f:
            json.dump(memories, f, indent=4)
            
        return f"Saved memory (PII-scrubbed): '{clean_fact}'"
    except Exception as e:
        return f"Error adding memory: {str(e)}"

def delete_memory(memory_id: str) -> str:
    """Deletes a specific memory by its ID."""
    try:
        ensure_memory_file_exists()
        with open(MEMORY_FILE, "r") as f:
            memories = json.load(f)
            
        found = False
        new_memories = []
        for m in memories:
            if m["id"] == memory_id:
                found = True
            else:
                new_memories.append(m)
                
        if not found:
            return f"Memory ID {memory_id} not found."
            
        with open(MEMORY_FILE, "w") as f:
            json.dump(new_memories, f, indent=4)
            
        return f"Successfully deleted memory ID {memory_id}."
    except Exception as e:
        return f"Error deleting memory: {str(e)}"

def export_memories() -> str:
    """Exports all stored memories in structured JSON format for user download or review."""
    return get_memories()

# ----------------- Agent Definition -----------------

def get_model():
    if os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY"):
        return Gemini(model_id="gemini-2.5-flash")
    elif os.getenv("ANTHROPIC_API_KEY"):
        return LiteLlm(model="anthropic/claude-3-5-sonnet-20241022")
    else:
        return Gemini(model_id="gemini-2.5-flash")

memory_agent = Agent(
    name="Memory",
    model=get_model(),
    instruction=MEMORY_SYSTEM_PROMPT,
    description="Manages long-term structured facts and habits of the student. Removes sensitive personal details.",
    tools=[get_memories, add_memory, delete_memory, export_memories]
)

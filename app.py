import os
import sys
import asyncio
from dotenv import load_dotenv

# Ensure dotenv is loaded before initializing agents
load_dotenv()

# Check for API keys
if not os.getenv("ANTHROPIC_API_KEY") and not os.getenv("GEMINI_API_KEY"):
    print("⚠️ WARNING: No ANTHROPIC_API_KEY or GEMINI_API_KEY found in environment variables.")
    print("Please set one of these keys in your .env file so the LLM can run.\n")

try:
    from google.adk.runners import InMemoryRunner
    from google.genai import types
except ImportError:
    # Fallback mock runner for standalone pipeline testing if google-adk is not installed
    class InMemoryRunner:
        def __init__(self, agent, app_name=""):
            self.agent = agent
        async def run_async(self, user_id, session_id, new_message):
            # Simple direct prompt call simulation
            print(f"\n[Mock Runner] Processing: {new_message.parts[0].text}\n", file=sys.stderr)
            class MockEvent:
                def __init__(self, text):
                    class Content:
                        def __init__(self, text):
                            class Part:
                                def __init__(self, text):
                                    self.text = text
                            self.parts = [Part(text)]
                    self.content = Content(text)
                def is_final_response(self):
                    return True
            yield MockEvent(f"Mock Response to: '{new_message.parts[0].text}'")

    class TypesMock:
        class Content:
            def __init__(self, parts, role="user"):
                self.parts = parts
        class Part:
            def __init__(self, text):
                self.text = text
    
    # Create mock types
    class types:
        Content = TypesMock.Content
        Part = TypesMock.Part

from orchestrator.agent import orchestrator_agent

BANNER = """
========================================================================
    ___   ______   __       ___    _____
   /   | /_  __/  / /      /   |  / ___/
  / /| |  / /    / /      / /| |  \__ \ 
 / ___ | / /    / /___   / ___ | ___/ / 
/_/  |_|/_/    /_____/  /_/  |_|/____/  
                                        
   Your AI Student Chief of Staff - Multi-Agent Study & Life Assistant
   Built on Google Agent Development Kit (ADK) & Google Antigravity
========================================================================
"""

def print_help():
    print("\n[i] Suggested Scenarios:")
    print("  1. Planning: 'What should I focus on this week?'")
    print("  2. Study:    'Summarize demo_data/sample_syllabus.txt for exam prep'")
    print("  3. Email:    'Draft an email to my professor asking for a 2-day extension'")
    print("  4. Memory:   'Tell me what you know about my study preferences'")
    print("\nCommands:")
    print("  'help'   - Show this instruction list.")
    print("  'exit'   - Exit the application.")
    print("="*72 + "\n")

async def chat_loop():
    print(BANNER)
    print_help()
    
    # Initialize InMemoryRunner
    runner = InMemoryRunner(agent=orchestrator_agent, app_name="atlas-chief-of-staff")
    
    user_id = "student_1"
    
    # Create the session before handling chat turns
    try:
        session = await runner.session_service.create_session(
            app_name="atlas-chief-of-staff",
            user_id=user_id
        )
        session_id = session.id
    except AttributeError:
        # Fallback for the MockRunner
        session_id = "session_1"
    
    while True:
        try:
            query = input("Student > ").strip()
            if not query:
                continue
                
            if query.lower() in ["exit", "quit", "q"]:
                print("\nGoodbye! Stay organized and good luck with your studies!")
                break
                
            if query.lower() == "help":
                print_help()
                continue
                
            print("\nAtlas thinking...", end="", flush=True)
            
            # Construct Content message object
            user_message = types.Content(
                parts=[types.Part(text=query)],
                role="user"
            )
            
            # Print response streaming
            print("\rAtlas: ", end="", flush=True)
            
            async for event in runner.run_async(
                user_id=user_id,
                session_id=session_id,
                new_message=user_message
            ):
                # Print text chunks
                if getattr(event, "content", None) and event.content.parts:
                    for part in event.content.parts:
                        if part.text:
                            print(part.text, end="", flush=True)
            
            print("\n")
            
        except KeyboardInterrupt:
            print("\n\nGoodbye! Stay organized and good luck with your studies!")
            break
        except Exception as e:
            print(f"\n[ERROR] Error encountered: {str(e)}\n")

def main():
    asyncio.run(chat_loop())

if __name__ == "__main__":
    main()

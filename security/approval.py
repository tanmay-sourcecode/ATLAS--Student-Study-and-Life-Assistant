import sys
import asyncio
from typing import Callable, Awaitable

# A global async hook that can be registered by the web server
async_approval_hook: Callable[[str], Awaitable[bool]] | None = None

async def request_approval(action_description: str) -> bool:
    """
    Presents a sensitive action to the student and requests confirmation.
    In web mode, delegates to the registered async approval hook.
    In CLI mode, blocks until approval is granted or denied in terminal.
    """
    if async_approval_hook is not None:
        return await async_approval_hook(action_description)

    print("\n" + "="*50)
    print("🔒 SECURITY WARNING: A sensitive action requires your approval:")
    print(f"👉 Action: {action_description}")
    print("="*50)
    
    try:
        # Run input() in executor to avoid blocking the event loop
        loop = asyncio.get_event_loop()
        user_input = await loop.run_in_executor(
            None, lambda: input("Do you approve this action? (yes/no) [no]: ").strip().lower()
        )
        approved = user_input in ["y", "yes"]
        if approved:
            print("[OK] Action approved by student. Executing...\n")
            return True
        else:
            print("[DENIED] Action denied by student. Cancelling...\n")
            return False
    except (KeyboardInterrupt, EOFError, Exception):
        print("\n[DENIED] Action denied by default.\n")
        return False

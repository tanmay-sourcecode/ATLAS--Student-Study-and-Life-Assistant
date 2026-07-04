import sys

def request_approval(action_description: str) -> bool:
    """
    Presents a sensitive action to the student and requests confirmation in the terminal.
    Blocks execution until approval is granted or denied.
    """
    print("\n" + "="*50)
    print("🔒 SECURITY WARNING: A sensitive action requires your approval:")
    print(f"👉 Action: {action_description}")
    print("="*50)
    
    try:
        user_input = input("Do you approve this action? (yes/no) [no]: ").strip().lower()
        approved = user_input in ["y", "yes"]
        if approved:
            print("[OK] Action approved by student. Executing...\n")
            return True
        else:
            print("[DENIED] Action denied by student. Cancelling...\n")
            return False
    except (KeyboardInterrupt, EOFError):
        print("\n[DENIED] Input interrupted. Action denied by default.\n")
        return False

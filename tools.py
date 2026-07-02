import os
import json
from datetime import datetime, timedelta
from security.approval import request_approval
from security.audit import log_action

DATA_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "demo_data")

# File paths for mock storage
CALENDAR_FILE = os.path.join(DATA_DIR, "calendar.json")
TASKS_FILE = os.path.join(DATA_DIR, "tasks.json")
EMAILS_FILE = os.path.join(DATA_DIR, "emails.json")

def ensure_data_dir_exists():
    if not os.path.exists(DATA_DIR):
        os.makedirs(DATA_DIR)

def initialize_mock_data():
    ensure_data_dir_exists()
    
    # Default Calendar Events
    if not os.path.exists(CALENDAR_FILE):
        now = datetime.now()
        default_calendar = [
            {
                "id": "1",
                "title": "CS 3110: Advanced Programming Lecture",
                "start": (now + timedelta(days=1)).replace(hour=10, minute=0, second=0).isoformat(),
                "end": (now + timedelta(days=1)).replace(hour=11, minute=30, second=0).isoformat(),
                "description": "Weekly lecture on functional programming concepts."
            },
            {
                "id": "2",
                "title": "MATH 2940: Linear Algebra Recitation",
                "start": (now + timedelta(days=2)).replace(hour=14, minute=0, second=0).isoformat(),
                "end": (now + timedelta(days=2)).replace(hour=15, minute=0, second=0).isoformat(),
                "description": "Vector spaces and eigenvalues practice."
            },
            {
                "id": "3",
                "title": "CS 3110: Office Hours",
                "start": (now + timedelta(days=3)).replace(hour=16, minute=0, second=0).isoformat(),
                "end": (now + timedelta(days=3)).replace(hour=17, minute=0, second=0).isoformat(),
                "description": "Consulting with TAs about Assignment 3."
            }
        ]
        with open(CALENDAR_FILE, "w") as f:
            json.dump(default_calendar, f, indent=4)

    # Default Tasks / Assignments
    if not os.path.exists(TASKS_FILE):
        now = datetime.now()
        default_tasks = [
            {
                "id": "1",
                "title": "CS 3110: Assignment 3 (Functional Interpreter)",
                "deadline": (now + timedelta(days=4)).replace(hour=23, minute=59, second=0).isoformat(),
                "priority": "High",
                "status": "Todo",
                "description": "Write a parser and interpreter for a subset of OCaml."
            },
            {
                "id": "2",
                "title": "MATH 2940: Homework 5",
                "deadline": (now + timedelta(days=5)).replace(hour=12, minute=0, second=0).isoformat(),
                "priority": "Medium",
                "status": "Todo",
                "description": "Complete exercises 4.1 to 4.5 in textbook."
            },
            {
                "id": "3",
                "title": "CS 3110: Midterm Prep Quiz",
                "deadline": (now + timedelta(days=2)).replace(hour=23, minute=59, second=0).isoformat(),
                "priority": "High",
                "status": "Completed",
                "description": "Online practice quiz covering first 4 modules."
            }
        ]
        with open(TASKS_FILE, "w") as f:
            json.dump(default_tasks, f, indent=4)

    # Default Emails
    if not os.path.exists(EMAILS_FILE):
        default_emails = []
        with open(EMAILS_FILE, "w") as f:
            json.dump(default_emails, f, indent=4)

# Initialize data immediately when module is loaded
initialize_mock_data()

# ----------------- Calendar Tools -----------------

def get_calendar_events() -> str:
    """Retrieves all scheduled calendar events (classes, exam blocks, recitation, office hours)."""
    log_action("tool_call", "get_calendar_events invoked")
    try:
        with open(CALENDAR_FILE, "r") as f:
            events = json.load(f)
        return json.dumps(events, indent=2)
    except Exception as e:
        return f"Error retrieving calendar events: {str(e)}"

def add_calendar_event(title: str, start_time: str, end_time: str, description: str = "") -> str:
    """Schedules a new calendar event. Required format for start_time and end_time: YYYY-MM-DDTHH:MM:SS"""
    log_action("tool_call", f"add_calendar_event '{title}' requested")
    
    # Gate: Human in the loop approval
    approval_desc = f"Schedule a calendar event: '{title}' from {start_time} to {end_time}"
    if not request_approval(approval_desc):
        log_action("security_gate", f"add_calendar_event '{title}' denied by user")
        return "Error: Action denied by user."
        
    log_action("security_gate", f"add_calendar_event '{title}' approved by user")
    try:
        # Validate datetime format
        datetime.fromisoformat(start_time)
        datetime.fromisoformat(end_time)
        
        with open(CALENDAR_FILE, "r") as f:
            events = json.load(f)
            
        new_event = {
            "id": str(len(events) + 1),
            "title": title,
            "start": start_time,
            "end": end_time,
            "description": description
        }
        events.append(new_event)
        
        with open(CALENDAR_FILE, "w") as f:
            json.dump(events, f, indent=4)
            
        return f"Successfully added event: '{title}' starting at {start_time}."
    except ValueError:
        return "Error: start_time and end_time must be in ISO 8601 format (YYYY-MM-DDTHH:MM:SS)."
    except Exception as e:
        return f"Error adding calendar event: {str(e)}"

# ----------------- Task / Assignment Tools -----------------

def get_tasks() -> str:
    """Retrieves the list of student tasks, assignments, deadlines, priorities and status."""
    log_action("tool_call", "get_tasks invoked")
    try:
        with open(TASKS_FILE, "r") as f:
            tasks = json.load(f)
        return json.dumps(tasks, indent=2)
    except Exception as e:
        return f"Error retrieving tasks: {str(e)}"

def add_task(title: str, deadline: str, priority: str = "Medium", description: str = "") -> str:
    """Adds a new task or assignment with a deadline. Required deadline format: YYYY-MM-DDTHH:MM:SS"""
    log_action("tool_call", f"add_task '{title}' requested")
    
    # Gate: Human in the loop approval
    approval_desc = f"Create a task: '{title}' with deadline {deadline}"
    if not request_approval(approval_desc):
        log_action("security_gate", f"add_task '{title}' denied by user")
        return "Error: Action denied by user."
        
    log_action("security_gate", f"add_task '{title}' approved by user")
    try:
        datetime.fromisoformat(deadline)
        if priority not in ["High", "Medium", "Low"]:
            return "Error: priority must be one of 'High', 'Medium', or 'Low'."
            
        with open(TASKS_FILE, "r") as f:
            tasks = json.load(f)
            
        new_task = {
            "id": str(len(tasks) + 1),
            "title": title,
            "deadline": deadline,
            "priority": priority,
            "status": "Todo",
            "description": description
        }
        tasks.append(new_task)
        
        with open(TASKS_FILE, "w") as f:
            json.dump(tasks, f, indent=4)
            
        return f"Successfully added task: '{title}' with deadline {deadline}."
    except ValueError:
        return "Error: deadline must be in ISO 8601 format (YYYY-MM-DDTHH:MM:SS)."
    except Exception as e:
        return f"Error adding task: {str(e)}"

def update_task_status(task_id: str, status: str) -> str:
    """Updates the status of a specific task. status must be either 'Todo' or 'Completed'."""
    log_action("tool_call", f"update_task_status ID {task_id} to '{status}' requested")
    
    # Gate: Human in the loop approval
    approval_desc = f"Update status of task ID {task_id} to '{status}'"
    if not request_approval(approval_desc):
        log_action("security_gate", f"update_task_status ID {task_id} denied by user")
        return "Error: Action denied by user."
        
    log_action("security_gate", f"update_task_status ID {task_id} approved by user")
    try:
        if status not in ["Todo", "Completed"]:
            return "Error: status must be either 'Todo' or 'Completed'."
            
        with open(TASKS_FILE, "r") as f:
            tasks = json.load(f)
            
        found = False
        for t in tasks:
            if t["id"] == task_id:
                t["status"] = status
                found = True
                break
                
        if not found:
            return f"Error: Task with ID {task_id} not found."
            
        with open(TASKS_FILE, "w") as f:
            json.dump(tasks, f, indent=4)
            
        return f"Successfully updated task ID {task_id} status to '{status}'."
    except Exception as e:
        return f"Error updating task status: {str(e)}"

# ----------------- Comms / Email Tools -----------------

def get_email_drafts() -> str:
    """Retrieves all drafted emails and their statuses (Pending, Approved)."""
    log_action("tool_call", "get_email_drafts invoked")
    try:
        with open(EMAILS_FILE, "r") as f:
            emails = json.load(f)
        return json.dumps(emails, indent=2)
    except Exception as e:
        return f"Error retrieving email drafts: {str(e)}"

def create_email_draft(to_email: str, subject: str, body: str) -> str:
    """Creates a new email draft. All emails require manual approval before being marked as sent."""
    log_action("tool_call", f"create_email_draft to '{to_email}' with subject '{subject}'")
    try:
        with open(EMAILS_FILE, "r") as f:
            emails = json.load(f)
            
        new_draft = {
            "id": str(len(emails) + 1),
            "to": to_email,
            "subject": subject,
            "body": body,
            "status": "Pending Approval",
            "created_at": datetime.now().isoformat()
        }
        emails.append(new_draft)
        
        with open(EMAILS_FILE, "w") as f:
            json.dump(emails, f, indent=4)
            
        return json.dumps({
            "message": "Draft created successfully. Awaiting human-in-the-loop approval.",
            "draft_id": new_draft["id"],
            "recipient": to_email,
            "subject": subject,
            "body": body
        })
    except Exception as e:
        return f"Error creating email draft: {str(e)}"

def approve_and_send_email(draft_id: str) -> str:
    """Approves a pending draft and simulates sending it out."""
    log_action("tool_call", f"approve_and_send_email ID {draft_id} requested")
    
    # Gate: Human in the loop approval
    approval_desc = f"Approve and SEND email draft ID {draft_id}"
    if not request_approval(approval_desc):
        log_action("security_gate", f"approve_and_send_email ID {draft_id} denied by user")
        return "Error: Action denied by user."
        
    log_action("security_gate", f"approve_and_send_email ID {draft_id} approved by user")
    try:
        with open(EMAILS_FILE, "r") as f:
            emails = json.load(f)
            
        found = False
        for email in emails:
            if email["id"] == draft_id:
                if email["status"] == "Sent":
                    return f"Email draft {draft_id} has already been sent."
                email["status"] = "Sent"
                email["sent_at"] = datetime.now().isoformat()
                found = True
                break
                
        if not found:
            return f"Error: Email draft with ID {draft_id} not found."
            
        with open(EMAILS_FILE, "w") as f:
            json.dump(emails, f, indent=4)
            
        return f"Email {draft_id} approved and sent successfully."
    except Exception as e:
        return f"Error sending email: {str(e)}"

# ----------------- File / Document Tools -----------------

def read_document_content(file_path: str) -> str:
    """Reads content from local documents (syllabi, notes) for parsing. Supports absolute and relative paths."""
    log_action("tool_call", f"read_document_content for {file_path}")
    try:
        # Restrict reading outside project boundaries or handle safely
        base_dir = os.path.dirname(os.path.abspath(__file__))
        resolved_path = os.path.abspath(os.path.join(base_dir, file_path))
        
        if not resolved_path.startswith(os.path.abspath(base_dir)):
            return "Error: Access denied. Cannot read files outside the project workspace."
            
        if not os.path.exists(resolved_path):
            return f"Error: File {file_path} not found."
            
        # If it's a PDF, we might use pypdf
        if file_path.lower().endswith(".pdf"):
            try:
                import pypdf
                reader = pypdf.PdfReader(resolved_path)
                text = ""
                for page in reader.pages:
                    text += page.extract_text() + "\n"
                return text
            except ImportError:
                return "Error: pypdf library is required to read PDF files, but it is not installed."
        else:
            with open(resolved_path, "r", encoding="utf-8", errors="ignore") as f:
                return f.read()
    except Exception as e:
        return f"Error reading file {file_path}: {str(e)}"

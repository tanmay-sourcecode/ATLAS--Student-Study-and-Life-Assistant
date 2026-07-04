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
POMODOROS_FILE = os.path.join(DATA_DIR, "pomodoros.json")
STUDY_QA_FILE = os.path.join(DATA_DIR, "study_qa.json")
STUDY_LOG_FILE = os.path.join(DATA_DIR, "study_log.json")

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

def delete_task(task_id: str) -> str:
    """Deletes a specific task. Requires human-in-the-loop approval."""
    log_action("tool_call", f"delete_task ID {task_id} requested")
    
    # Gate: Human in the loop approval
    approval_desc = f"Delete task ID {task_id}"
    if not request_approval(approval_desc):
        log_action("security_gate", f"delete_task ID {task_id} denied by user")
        return "Error: Action denied by user."
        
    log_action("security_gate", f"delete_task ID {task_id} approved by user")
    try:
        with open(TASKS_FILE, "r") as f:
            tasks = json.load(f)
            
        found = False
        new_tasks = []
        for t in tasks:
            if t["id"] == task_id:
                found = True
                task_title = t["title"]
            else:
                new_tasks.append(t)
                
        if not found:
            return f"Error: Task with ID {task_id} not found."
            
        with open(TASKS_FILE, "w") as f:
            json.dump(new_tasks, f, indent=4)
            
        return f"Successfully deleted task ID {task_id} ('{task_title}')."
    except Exception as e:
        return f"Error deleting task: {str(e)}"

def edit_task(task_id: str, title: str = None, deadline: str = None, priority: str = None, description: str = None) -> str:
    """Edits individual fields of an existing task. Requires human-in-the-loop approval."""
    log_action("tool_call", f"edit_task ID {task_id} requested")
    
    # Construct update description
    updates = []
    if title is not None: updates.append(f"title='{title}'")
    if deadline is not None: updates.append(f"deadline='{deadline}'")
    if priority is not None: updates.append(f"priority='{priority}'")
    if description is not None: updates.append(f"description='{description}'")
    
    if not updates:
        return "Error: No updates specified."
        
    approval_desc = f"Edit task ID {task_id}: {', '.join(updates)}"
    if not request_approval(approval_desc):
        log_action("security_gate", f"edit_task ID {task_id} denied by user")
        return "Error: Action denied by user."
        
    log_action("security_gate", f"edit_task ID {task_id} approved by user")
    try:
        if deadline is not None:
            datetime.fromisoformat(deadline)
            
        if priority is not None and priority not in ["High", "Medium", "Low"]:
            return "Error: priority must be one of 'High', 'Medium', or 'Low'."
            
        with open(TASKS_FILE, "r") as f:
            tasks = json.load(f)
            
        found = False
        for t in tasks:
            if t["id"] == task_id:
                if title is not None: t["title"] = title
                if deadline is not None: t["deadline"] = deadline
                if priority is not None: t["priority"] = priority
                if description is not None: t["description"] = description
                found = True
                break
                
        if not found:
            return f"Error: Task with ID {task_id} not found."
            
        with open(TASKS_FILE, "w") as f:
            json.dump(tasks, f, indent=4)
            
        return f"Successfully updated task ID {task_id}."
    except ValueError:
        return "Error: deadline must be in ISO 8601 format (YYYY-MM-DDTHH:MM:SS)."
    except Exception as e:
        return f"Error editing task: {str(e)}"

def get_task_reminders() -> str:
    """Retrieves all incomplete tasks, categorizing them by urgency (Overdue, Urgent within 24h, Upcoming within 48h)."""
    log_action("tool_call", "get_task_reminders invoked")
    try:
        with open(TASKS_FILE, "r") as f:
            tasks = json.load(f)
            
        now = datetime.now()
        overdue = []
        urgent = []
        upcoming = []
        
        for t in tasks:
            if t["status"] == "Completed":
                continue
                
            try:
                due_dt = datetime.fromisoformat(t["deadline"])
                if due_dt < now:
                    overdue.append(t)
                elif due_dt <= now + timedelta(hours=24):
                    urgent.append(t)
                elif due_dt <= now + timedelta(hours=48):
                    upcoming.append(t)
            except ValueError:
                # Fallback if deadline is not standard format
                upcoming.append(t)
                
        reminders = {
            "overdue": overdue,
            "urgent": urgent,
            "upcoming": upcoming
        }
        return json.dumps(reminders, indent=2)
    except Exception as e:
        return f"Error getting task reminders: {str(e)}"

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

def ensure_pomodoros_file_exists():
    ensure_data_dir_exists()
    if not os.path.exists(POMODOROS_FILE):
        with open(POMODOROS_FILE, "w") as f:
            json.dump([], f)

def ensure_study_qa_file_exists():
    ensure_data_dir_exists()
    if not os.path.exists(STUDY_QA_FILE):
        with open(STUDY_QA_FILE, "w") as f:
            json.dump({}, f)

# ----------------- Pomodoro Tools -----------------

def log_pomodoro_session(task_id: str, duration_minutes: int = 25) -> str:
    """Logs a completed Pomodoro study focus session for a specific task. Updates the task's completed pomodoros count and duration."""
    log_action("tool_call", f"log_pomodoro_session for task ID {task_id} with duration {duration_minutes}m")
    try:
        ensure_pomodoros_file_exists()
        
        # 1. Update task stats in tasks.json if the task exists
        task_title = "Unknown Task"
        if os.path.exists(TASKS_FILE):
            with open(TASKS_FILE, "r") as f:
                tasks = json.load(f)
            for t in tasks:
                if t["id"] == task_id:
                    task_title = t["title"]
                    t["completed_pomodoros"] = t.get("completed_pomodoros", 0) + 1
                    t["total_focus_time"] = t.get("total_focus_time", 0) + duration_minutes
                    break
            with open(TASKS_FILE, "w") as f:
                json.dump(tasks, f, indent=4)
        
        # 2. Log to pomodoros.json
        with open(POMODOROS_FILE, "r") as f:
            history = json.load(f)
            
        new_session = {
            "id": str(len(history) + 1),
            "task_id": task_id,
            "task_title": task_title,
            "duration_minutes": duration_minutes,
            "completed_at": datetime.now().isoformat()
        }
        history.append(new_session)
        
        with open(POMODOROS_FILE, "w") as f:
            json.dump(history, f, indent=4)
            
        return f"Successfully logged Pomodoro session for '{task_title}' (Task ID: {task_id}). Completed cycles: {new_session['id']}."
    except Exception as e:
        return f"Error logging Pomodoro session: {str(e)}"

def get_pomodoro_history() -> str:
    """Retrieves all logged Pomodoro focus sessions and overall statistics."""
    log_action("tool_call", "get_pomodoro_history invoked")
    try:
        ensure_pomodoros_file_exists()
        with open(POMODOROS_FILE, "r") as f:
            history = json.load(f)
            
        total_time = sum(s["duration_minutes"] for s in history)
        stats = {
            "total_completed_sessions": len(history),
            "total_focus_minutes": total_time,
            "sessions": history
        }
        return json.dumps(stats, indent=2)
    except Exception as e:
        return f"Error retrieving Pomodoro history: {str(e)}"

# ----------------- Q&A / Study Quiz Tools -----------------

def save_qa_pairs(subject: str, qa_list: list) -> str:
    """Saves generated active-recall Q&A pairs (questions and answers) for a specific subject/course. qa_list must be a list of dicts: [{'question': '...', 'answer': '...'}]"""
    log_action("tool_call", f"save_qa_pairs for subject '{subject}'")
    try:
        ensure_study_qa_file_exists()
        with open(STUDY_QA_FILE, "r") as f:
            data = json.load(f)
            
        # Ensure list structure is correct
        cleaned_list = []
        for item in qa_list:
            if isinstance(item, dict) and "question" in item and "answer" in item:
                cleaned_list.append({
                    "question": item["question"],
                    "answer": item["answer"]
                })
                
        data[subject] = cleaned_list
        
        with open(STUDY_QA_FILE, "w") as f:
            json.dump(data, f, indent=4)
            
        return f"Successfully saved {len(cleaned_list)} active-recall Q&A pairs for '{subject}'."
    except Exception as e:
        return f"Error saving Q&A pairs: {str(e)}"

def get_qa_pairs(subject: str) -> str:
    """Retrieves all saved active-recall Q&A pairs for a specific subject/course."""
    log_action("tool_call", f"get_qa_pairs for subject '{subject}'")
    try:
        ensure_study_qa_file_exists()
        with open(STUDY_QA_FILE, "r") as f:
            data = json.load(f)
        
        pairs = data.get(subject, [])
        return json.dumps(pairs, indent=2)
    except Exception as e:
        return f"Error retrieving Q&A pairs: {str(e)}"

# ----------------- Smart Revision Reminder Tools -----------------

def ensure_study_log_file_exists():
    ensure_data_dir_exists()
    if not os.path.exists(STUDY_LOG_FILE):
        with open(STUDY_LOG_FILE, "w") as f:
            json.dump([], f)

def log_study_topic(subject: str, topic: str, summary: str) -> str:
    """Logs that a topic has been studied, with its micro-summary. Schedules first review in 2 days."""
    log_action("tool_call", f"log_study_topic for subject '{subject}', topic '{topic}'")
    try:
        ensure_study_log_file_exists()
        with open(STUDY_LOG_FILE, "r") as f:
            log_entries = json.load(f)
            
        # Check if topic already logged for this subject
        for entry in log_entries:
            if entry["subject"].lower() == subject.lower() and entry["topic"].lower() == topic.lower():
                return f"Topic '{topic}' is already logged in study log for subject '{subject}'."
                
        now = datetime.now()
        next_due = now + timedelta(days=2)
        
        new_entry = {
            "id": str(len(log_entries) + 1),
            "subject": subject,
            "topic": topic,
            "summary": summary,
            "first_studied": now.isoformat(),
            "last_reviewed": now.isoformat(),
            "review_count": 1,
            "next_review_due": next_due.isoformat()
        }
        log_entries.append(new_entry)
        
        with open(STUDY_LOG_FILE, "w") as f:
            json.dump(log_entries, f, indent=4)
            
        return f"Successfully logged study topic '{topic}' for '{subject}'. First review scheduled in 2 days."
    except Exception as e:
        return f"Error logging study topic: {str(e)}"

def get_revision_queue() -> str:
    """Retrieves all study topics that are due for spaced-repetition review, sorted by urgency (most overdue first)."""
    log_action("tool_call", "get_revision_queue invoked")
    try:
        ensure_study_log_file_exists()
        with open(STUDY_LOG_FILE, "r") as f:
            log_entries = json.load(f)
            
        now = datetime.now()
        queue = []
        for entry in log_entries:
            due_dt = datetime.fromisoformat(entry["next_review_due"])
            if due_dt <= now:
                # Add human readable time overdue
                overdue_duration = now - due_dt
                entry["days_overdue"] = overdue_duration.days
                queue.append(entry)
                
        # Sort queue: most overdue first (which means smallest next_review_due)
        queue.sort(key=lambda x: x["next_review_due"])
        return json.dumps(queue, indent=2)
    except Exception as e:
        return f"Error retrieving revision queue: {str(e)}"

def mark_topic_reviewed(topic_id: str) -> str:
    """Marks a topic as reviewed, incrementing its review count and rescheduling the next review based on spaced repetition intervals."""
    log_action("tool_call", f"mark_topic_reviewed for ID {topic_id}")
    try:
        ensure_study_log_file_exists()
        with open(STUDY_LOG_FILE, "r") as f:
            log_entries = json.load(f)
            
        found = False
        intervals = [2, 5, 10, 17, 24] # Spaced repetition intervals in days
        
        for entry in log_entries:
            if entry["id"] == topic_id:
                now = datetime.now()
                entry["last_reviewed"] = now.isoformat()
                entry["review_count"] = entry.get("review_count", 1) + 1
                
                count = entry["review_count"]
                # Intervals mapping:
                # count=2 -> 5 days from now
                # count=3 -> 10 days from now
                # count=4 -> 17 days from now
                # count=5 -> 24 days from now
                # count>=6 -> 30 days from now
                if count <= len(intervals):
                    days = intervals[count - 1] # intervals[1] = 5, etc.
                else:
                    days = 30
                    
                next_due = now + timedelta(days=days)
                entry["next_review_due"] = next_due.isoformat()
                found = True
                topic_title = entry["topic"]
                subject = entry["subject"]
                break
                
        if not found:
            return f"Error: Topic ID '{topic_id}' not found in study log."
            
        with open(STUDY_LOG_FILE, "w") as f:
            json.dump(log_entries, f, indent=4)
            
        return f"Successfully marked '{topic_title}' ({subject}) as reviewed. Next review scheduled in {days} days."
    except Exception as e:
        return f"Error marking topic reviewed: {str(e)}"

def get_new_topics_suggestions(subject: str) -> str:
    """Finds topics related to the subject that are mentioned in demo_data files but not yet present in the study log."""
    log_action("tool_call", f"get_new_topics_suggestions for subject '{subject}'")
    try:
        ensure_study_log_file_exists()
        with open(STUDY_LOG_FILE, "r") as f:
            log_entries = json.load(f)
            
        studied = {entry["topic"].lower() for entry in log_entries if entry["subject"].lower() == subject.lower()}
        
        suggested_topics = []
        import re
        
        # 1. Look in sample_notes.txt
        notes_path = os.path.join(DATA_DIR, "sample_notes.txt")
        if os.path.exists(notes_path):
            with open(notes_path, "r", encoding="utf-8", errors="ignore") as f:
                notes_content = f.read()
            for line in notes_content.splitlines():
                # Extract numbered key concepts (e.g. 1. First-Class Functions: ...)
                match = re.match(r"^\d+\.\s+([^:]+):", line.strip())
                if match:
                    suggested_topics.append(match.group(1).strip())
                elif line.strip().startswith("- "):
                    # Clean up bullet points
                    text = line.strip()[2:].strip()
                    if "difference between" in text.lower():
                        suggested_topics.append("Tail Recursion vs Normal Recursion")
                    elif "lexical scope" in text.lower():
                        suggested_topics.append("Lexical Scope vs Dynamic Scope")
                    elif "map, filter" in text.lower():
                        suggested_topics.append("Map, Filter, and Fold")
                    else:
                        suggested_topics.append(text)
                        
        # 2. Look in sample_syllabus.txt
        syllabus_path = os.path.join(DATA_DIR, "sample_syllabus.txt")
        if os.path.exists(syllabus_path):
            with open(syllabus_path, "r", encoding="utf-8", errors="ignore") as f:
                syllabus_content = f.read()
            for line in syllabus_content.splitlines():
                if "It covers" in line:
                    parts = line.replace("It covers", "").replace("and", ",").split(",")
                    for part in parts:
                        cleaned = part.strip().strip(".")
                        if cleaned:
                            suggested_topics.append(cleaned.capitalize())
                            
        # 3. Look in sample_assignments.json
        assigns_path = os.path.join(DATA_DIR, "sample_assignments.json")
        if os.path.exists(assigns_path):
            with open(assigns_path, "r") as f:
                assigns = json.load(f)
            for a in assigns:
                if a.get("course", "").lower() == subject.lower():
                    title = a.get("title", "")
                    if ":" in title:
                        title = title.split(":", 1)[1].strip()
                    suggested_topics.append(title)
                    
        # Deduplicate and filter out already studied topics
        unique_suggestions = []
        for topic in suggested_topics:
            if topic.lower() not in studied and topic.lower() not in [t.lower() for t in unique_suggestions]:
                unique_suggestions.append(topic)
                
        return json.dumps(unique_suggestions, indent=2)
    except Exception as e:
        return f"Error getting new topic suggestions: {str(e)}"

# ----------------- Skill Instruction Tool -----------------

def get_skill_instructions(skill_name: str) -> str:
    """Retrieves the detailed instructions of a student assistant skill dynamically. Exposes instructions on demand (progressive disclosure)."""
    log_action("tool_call", f"get_skill_instructions for skill '{skill_name}'")
    try:
        from skills_runtime import load_skill
        skill = load_skill(skill_name)
        if not skill or not skill.get("instructions"):
            return f"Skill '{skill_name}' instructions could not be found."
        return f"--- Skill '{skill_name}' Instructions ---\n{skill['instructions']}"
    except Exception as e:
        return f"Error loading skill instructions: {str(e)}"

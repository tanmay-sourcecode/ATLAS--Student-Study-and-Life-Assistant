import os
import json
from datetime import datetime, timedelta
import pytest
from unittest.mock import patch
from tools import (
    delete_task,
    edit_task,
    get_task_reminders,
    get_tasks,
    add_task,
    TASKS_FILE
)

def test_task_reminder_system():
    # Setup clean tasks file
    if os.path.exists(TASKS_FILE):
        os.remove(TASKS_FILE)
        
    with open(TASKS_FILE, "w") as f:
        json.dump([], f)
        
    now = datetime.now()
    
    # Overdue task
    overdue_task = {
        "id": "1",
        "title": "Overdue Assignment",
        "deadline": (now - timedelta(hours=2)).isoformat(),
        "priority": "High",
        "status": "Todo",
        "description": "This is overdue"
    }
    # Urgent task (within 24 hours)
    urgent_task = {
        "id": "2",
        "title": "Urgent Assignment",
        "deadline": (now + timedelta(hours=5)).isoformat(),
        "priority": "Medium",
        "status": "Todo",
        "description": "Due soon"
    }
    # Upcoming task (within 48 hours)
    upcoming_task = {
        "id": "3",
        "title": "Upcoming Assignment",
        "deadline": (now + timedelta(hours=35)).isoformat(),
        "priority": "Low",
        "status": "Todo",
        "description": "Due later"
    }
    # Completed task
    completed_task = {
        "id": "4",
        "title": "Completed Assignment",
        "deadline": (now - timedelta(hours=5)).isoformat(),
        "priority": "High",
        "status": "Completed",
        "description": "Already done"
    }
    
    test_tasks = [overdue_task, urgent_task, upcoming_task, completed_task]
    with open(TASKS_FILE, "w") as f:
        json.dump(test_tasks, f, indent=4)
        
    # 1. Test reminders retrieval and categorization
    reminders_str = get_task_reminders()
    reminders = json.loads(reminders_str)
    
    assert len(reminders["overdue"]) == 1
    assert reminders["overdue"][0]["id"] == "1"
    
    assert len(reminders["urgent"]) == 1
    assert reminders["urgent"][0]["id"] == "2"
    
    assert len(reminders["upcoming"]) == 1
    assert reminders["upcoming"][0]["id"] == "3"
    
    # Completed tasks should not show up
    all_reminder_ids = [t["id"] for group in reminders.values() for t in group]
    assert "4" not in all_reminder_ids
    
    # 2. Test edit_task (Approval Denied)
    with patch('builtins.input', return_value='no'):
        res = edit_task("2", title="New Title")
        assert "Error: Action denied by user." in res
        
        # Verify no change occurred
        tasks_str = get_tasks()
        tasks = json.loads(tasks_str)
        t = [x for x in tasks if x["id"] == "2"][0]
        assert t["title"] == "Urgent Assignment"
        
    # 3. Test edit_task (Approval Approved)
    with patch('builtins.input', return_value='yes'):
        res = edit_task("2", title="Updated Urgent Title", priority="High")
        assert "Successfully updated task ID 2" in res
        
        # Verify change occurred
        tasks_str = get_tasks()
        tasks = json.loads(tasks_str)
        t = [x for x in tasks if x["id"] == "2"][0]
        assert t["title"] == "Updated Urgent Title"
        assert t["priority"] == "High"
        
    # 4. Test edit_task validations
    with patch('builtins.input', return_value='yes'):
        # Invalid priority
        res = edit_task("2", priority="Urgent")
        assert "Error: priority must be one of" in res
        
        # Invalid deadline format
        res = edit_task("2", deadline="invalid-date")
        assert "Error: deadline must be in ISO 8601 format" in res
        
    # 5. Test delete_task (Approval Denied)
    with patch('builtins.input', return_value='no'):
        res = delete_task("1")
        assert "Error: Action denied by user." in res
        
        # Verify task is still present
        tasks_str = get_tasks()
        tasks = json.loads(tasks_str)
        ids = [x["id"] for x in tasks]
        assert "1" in ids
        
    # 6. Test delete_task (Approval Approved)
    with patch('builtins.input', return_value='yes'):
        res = delete_task("1")
        assert "Successfully deleted task ID 1" in res
        
        # Verify task is removed
        tasks_str = get_tasks()
        tasks = json.loads(tasks_str)
        ids = [x["id"] for x in tasks]
        assert "1" not in ids

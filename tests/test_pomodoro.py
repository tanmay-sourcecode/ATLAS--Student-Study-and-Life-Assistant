import os
import json
import pytest
from tools import log_pomodoro_session, get_pomodoro_history, POMODOROS_FILE, ensure_pomodoros_file_exists

def test_pomodoro_logging_and_history():
    # Remove existing pomodoros.json if it exists to have a clean test
    if os.path.exists(POMODOROS_FILE):
        os.remove(POMODOROS_FILE)
        
    ensure_pomodoros_file_exists()
    
    # Initially history should be empty
    history_str = get_pomodoro_history()
    history = json.loads(history_str)
    assert history["total_completed_sessions"] == 0
    assert history["total_focus_minutes"] == 0
    assert len(history["sessions"]) == 0
    
    # Log a session
    res = log_pomodoro_session(task_id="1", duration_minutes=25)
    assert "Successfully logged" in res
    
    # Verify history updated
    history_str = get_pomodoro_history()
    history = json.loads(history_str)
    assert history["total_completed_sessions"] == 1
    assert history["total_focus_minutes"] == 25
    assert len(history["sessions"]) == 1
    assert history["sessions"][0]["task_id"] == "1"
    assert history["sessions"][0]["duration_minutes"] == 25

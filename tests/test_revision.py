import os
import json
from datetime import datetime, timedelta
import pytest
from tools import (
    log_study_topic,
    get_revision_queue,
    mark_topic_reviewed,
    get_new_topics_suggestions,
    STUDY_LOG_FILE,
    ensure_study_log_file_exists
)

def test_revision_system():
    # Remove existing study_log.json if it exists to have a clean test
    if os.path.exists(STUDY_LOG_FILE):
        os.remove(STUDY_LOG_FILE)
        
    ensure_study_log_file_exists()
    
    # 1. Log a study topic
    res = log_study_topic(
        subject="CS 3110",
        topic="Recursion",
        summary="A function that calls itself to solve smaller subproblems."
    )
    assert "Successfully logged study topic" in res
    
    # Check that it's in the log file
    with open(STUDY_LOG_FILE, "r") as f:
        log_entries = json.load(f)
    assert len(log_entries) == 1
    entry = log_entries[0]
    assert entry["subject"] == "CS 3110"
    assert entry["topic"] == "Recursion"
    assert entry["review_count"] == 1
    
    # Check that first review is scheduled in 2 days
    due_dt = datetime.fromisoformat(entry["next_review_due"])
    now = datetime.now()
    time_diff = due_dt - now
    assert time_diff.days == 1 or time_diff.days == 2  # due to timezone/execution time, should be ~2 days
    
    # 2. Test revision queue when nothing is due yet
    queue_str = get_revision_queue()
    queue = json.loads(queue_str)
    assert len(queue) == 0
    
    # 3. Manually mark the item as due in the past to test queue retrieval
    past_time = datetime.now() - timedelta(hours=1)
    entry["next_review_due"] = past_time.isoformat()
    with open(STUDY_LOG_FILE, "w") as f:
        json.dump([entry], f, indent=4)
        
    queue_str = get_revision_queue()
    queue = json.loads(queue_str)
    assert len(queue) == 1
    assert queue[0]["topic"] == "Recursion"
    
    # 4. Mark topic reviewed and check intervals:
    # First review was count 1 -> next due in 5 days (as count becomes 2)
    res_review = mark_topic_reviewed(entry["id"])
    assert "Successfully marked" in res_review
    assert "scheduled in 5 days" in res_review
    
    with open(STUDY_LOG_FILE, "r") as f:
        log_entries = json.load(f)
    entry = log_entries[0]
    assert entry["review_count"] == 2
    due_dt = datetime.fromisoformat(entry["next_review_due"])
    time_diff = due_dt - datetime.now()
    assert time_diff.days == 4 or time_diff.days == 5
    
    # Second review -> next due in 10 days
    res_review = mark_topic_reviewed(entry["id"])
    assert "scheduled in 10 days" in res_review
    
    with open(STUDY_LOG_FILE, "r") as f:
        log_entries = json.load(f)
    entry = log_entries[0]
    assert entry["review_count"] == 3
    due_dt = datetime.fromisoformat(entry["next_review_due"])
    time_diff = due_dt - datetime.now()
    assert time_diff.days == 9 or time_diff.days == 10
    
    # 5. Check new topic suggestions
    suggestions_str = get_new_topics_suggestions(subject="CS 3110")
    suggestions = json.loads(suggestions_str)
    # Should find key concepts from notes/syllabus like "First-Class Functions", "Immutability", "Tail Recursion"
    # and they should not include "Recursion" if "Recursion" is already studied.
    assert len(suggestions) > 0
    assert "Recursion" not in suggestions
    assert "First-Class Functions" in suggestions or "Tail Recursion" in suggestions or "Immutability" in suggestions

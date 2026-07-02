import os
import pytest
from skills_runtime import load_skill, list_available_skills

def test_load_all_skills():
    """Verifies that all 6 required skills can be loaded and read dynamically."""
    required_skills = [
        "daily_brief",
        "study_plan",
        "assignment_breakdown",
        "email_draft",
        "document_summary",
        "deadline_checkin"
    ]
    
    # Check that skills can be listed
    available = [s["id"] for s in list_available_skills()]
    
    for skill_name in required_skills:
        assert skill_name in available
        
        # Load the skill body
        skill_data = load_skill(skill_name)
        assert skill_data["name"] is not None
        assert skill_data["description"] != "No description provided."
        assert len(skill_data["instructions"]) > 0

def test_load_invalid_skill():
    """Verifies that loading a non-existent skill handles errors gracefully."""
    fallback = load_skill("non_existent_skill_xyz")
    assert fallback["name"] == "non_existent_skill_xyz"
    assert "not found" in fallback["description"]
    assert fallback["instructions"] == ""

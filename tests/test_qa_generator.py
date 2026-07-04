import os
import json
import pytest
from tools import save_qa_pairs, get_qa_pairs, STUDY_QA_FILE, ensure_study_qa_file_exists
from skills_runtime import load_skill

def test_save_and_retrieve_qa_pairs():
    # Remove existing study_qa.json if it exists to have a clean test
    if os.path.exists(STUDY_QA_FILE):
        os.remove(STUDY_QA_FILE)
        
    ensure_study_qa_file_exists()
    
    # Initially empty
    pairs_str = get_qa_pairs(subject="Linear Algebra")
    pairs = json.loads(pairs_str)
    assert len(pairs) == 0
    
    # Save pairs
    qa_list = [
        {"question": "What is an eigenvalue?", "answer": "A scalar lambda associated with a linear transformation."},
        {"question": "What is a vector space?", "answer": "A collection of vectors that satisfies eight axioms."}
    ]
    res = save_qa_pairs(subject="Linear Algebra", qa_list=qa_list)
    assert "Successfully saved" in res
    
    # Retrieve and verify
    pairs_str = get_qa_pairs(subject="Linear Algebra")
    pairs = json.loads(pairs_str)
    assert len(pairs) == 2
    assert pairs[0]["question"] == "What is an eigenvalue?"
    assert pairs[1]["answer"] == "A collection of vectors that satisfies eight axioms."

def test_qa_generator_skill_loading():
    skill_data = load_skill("qa_generator")
    assert skill_data["name"] == "qa_generator"
    assert "active-recall" in skill_data["instructions"]
    assert "quiz" in skill_data["instructions"]
    # Verify the word "flashcard" is not present in the instructions
    assert "flashcard" not in skill_data["instructions"].lower()

import pytest
import asyncio
from unittest.mock import patch
from security.approval import request_approval
import tools

def test_request_approval_yes():
    """Verifies that request_approval returns True when user inputs 'yes'."""
    with patch('builtins.input', return_value='yes'):
        assert asyncio.run(request_approval("Test sensitive action")) is True

def test_request_approval_no():
    """Verifies that request_approval returns False when user inputs 'no'."""
    with patch('builtins.input', return_value='no'):
        assert asyncio.run(request_approval("Test sensitive action")) is False

def test_request_approval_default_no():
    """Verifies that request_approval returns False on empty/default input."""
    with patch('builtins.input', return_value=''):
        assert asyncio.run(request_approval("Test sensitive action")) is False

def test_calendar_event_gated_by_approval():
    """Verifies that add_calendar_event is blocked if approval is denied."""
    with patch('builtins.input', return_value='no'):
        result = asyncio.run(tools.add_calendar_event("CS 3110 Lecture", "2026-07-03T10:00:00", "2026-07-03T11:30:00"))
        assert "Error: Action denied by user." in result

def test_email_sending_gated_by_approval():
    """Verifies that email sending is blocked if approval is denied."""
    with patch('builtins.input', return_value='no'):
        result = asyncio.run(tools.approve_and_send_email("1"))
        assert "Error: Action denied by user." in result

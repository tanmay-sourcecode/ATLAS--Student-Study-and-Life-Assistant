import re

# Regex patterns for common PII
EMAIL_REGEX = re.compile(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b')
PHONE_REGEX = re.compile(r'\b(?:\+?\d{1,3}[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}\b')
STUDENT_ID_REGEX = re.compile(r'\b\d{7,8}\b') # Matches 7 or 8-digit student ID numbers

def redact_pii(text: str) -> str:
    """
    Scrubs sensitive student PII (emails, phone numbers, numeric IDs) from text.
    Replaces matched entities with placeholder tokens.
    """
    if not isinstance(text, str):
        return text
        
    # Redact email addresses
    scrubbed = EMAIL_REGEX.sub("[REDACTED EMAIL]", text)
    
    # Redact phone numbers
    scrubbed = PHONE_REGEX.sub("[REDACTED PHONE]", scrubbed)
    
    # Redact student IDs
    scrubbed = STUDENT_ID_REGEX.sub("[REDACTED STUDENT ID]", scrubbed)
    
    return scrubbed

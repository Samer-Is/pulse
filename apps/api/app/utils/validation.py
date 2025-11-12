"""Input validation utilities."""

import re
from typing import Optional


def sanitize_string(value: str, max_length: int = 1000) -> str:
    """
    Sanitize string input.
    
    Args:
        value: Input string
        max_length: Maximum allowed length
        
    Returns:
        Sanitized string
    """
    if not value:
        return ""
    
    # Remove null bytes
    value = value.replace("\x00", "")
    
    # Trim to max length
    value = value[:max_length]
    
    # Strip leading/trailing whitespace
    value = value.strip()
    
    return value


def validate_email(email: str) -> bool:
    """
    Validate email format.
    
    Args:
        email: Email address
        
    Returns:
        True if valid
    """
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return bool(re.match(pattern, email))


def validate_url(url: str) -> bool:
    """
    Validate URL format.
    
    Args:
        url: URL string
        
    Returns:
        True if valid
    """
    pattern = r'^https?:\/\/(www\.)?[-a-zA-Z0-9@:%._\+~#=]{1,256}\.[a-zA-Z0-9()]{1,6}\b([-a-zA-Z0-9()@:%_\+.~#?&//=]*)$'
    return bool(re.match(pattern, url))


def sanitize_filename(filename: str) -> str:
    """
    Sanitize filename to prevent path traversal.
    
    Args:
        filename: Input filename
        
    Returns:
        Sanitized filename
    """
    # Remove path separators and special characters
    filename = re.sub(r'[^\w\s.-]', '', filename)
    
    # Remove any .. sequences
    filename = filename.replace("..", "")
    
    # Limit length
    filename = filename[:255]
    
    return filename


def validate_json_field(value: str, max_length: int = 10000) -> bool:
    """
    Validate JSON field length.
    
    Args:
        value: JSON string
        max_length: Maximum allowed length
        
    Returns:
        True if valid
    """
    return len(value) <= max_length


def sanitize_prompt(prompt: str, max_length: int = 5000) -> str:
    """
    Sanitize AI prompt input.
    
    Args:
        prompt: User prompt
        max_length: Maximum allowed length
        
    Returns:
        Sanitized prompt
    """
    # Remove null bytes
    prompt = prompt.replace("\x00", "")
    
    # Trim to max length
    prompt = prompt[:max_length]
    
    # Remove excessive whitespace
    prompt = " ".join(prompt.split())
    
    return prompt


def validate_pagination(page: int, per_page: int, max_per_page: int = 100) -> tuple[int, int]:
    """
    Validate and sanitize pagination parameters.
    
    Args:
        page: Page number
        per_page: Items per page
        max_per_page: Maximum items per page
        
    Returns:
        Validated (page, per_page) tuple
    """
    page = max(1, page)  # Minimum page is 1
    per_page = max(1, min(per_page, max_per_page))  # Clamp to range
    
    return page, per_page


def validate_id(id_value: str) -> bool:
    """
    Validate UUID format for IDs.
    
    Args:
        id_value: ID string
        
    Returns:
        True if valid UUID format
    """
    pattern = r'^[a-f0-9]{8}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{12}$'
    return bool(re.match(pattern, id_value.lower()))


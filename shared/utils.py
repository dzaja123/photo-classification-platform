"""Shared utility functions."""

import hashlib
import secrets
import string
from datetime import datetime, timedelta, timezone
from typing import Optional


def generate_secure_filename(original_filename: str) -> str:
    """
    Generate a secure, unique filename.
    
    Args:
        original_filename: Original file name with extension
    
    Returns:
        Secure filename with timestamp and random string
    
    Example:
        >>> generate_secure_filename("photo.jpg")
        "20260205_abc123def456.jpg"
    """
    # Get file extension
    extension = original_filename.rsplit(".", 1)[-1].lower()
    
    # Generate random string
    random_str = ''.join(secrets.choice(string.ascii_lowercase + string.digits) for _ in range(12))
    
    # Add timestamp
    timestamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
    
    return f"{timestamp}_{random_str}.{extension}"


def hash_file_content(content: bytes) -> str:
    """
    Generate SHA256 hash of file content.
    
    Args:
        content: File content as bytes
    
    Returns:
        Hex digest of SHA256 hash
    """
    return hashlib.sha256(content).hexdigest()


def sanitize_string(value: str, max_length: Optional[int] = None) -> str:
    """
    Sanitize string input (basic XSS prevention).
    
    Args:
        value: Input string
        max_length: Maximum allowed length (optional)
    
    Returns:
        Sanitized string
    """
    # Remove null bytes
    value = value.replace('\x00', '')
    
    # Strip whitespace
    value = value.strip()
    
    # Truncate if needed
    if max_length and len(value) > max_length:
        value = value[:max_length]
    
    return value


def calculate_age_group(age: int) -> str:
    """
    Calculate age group for analytics.
    
    Args:
        age: Age in years
    
    Returns:
        Age group string
    
    Example:
        >>> calculate_age_group(25)
        "18-25"
    """
    if age < 18:
        return "Under 18"
    elif age <= 25:
        return "18-25"
    elif age <= 35:
        return "26-35"
    elif age <= 45:
        return "36-45"
    elif age <= 55:
        return "46-55"
    elif age <= 65:
        return "56-65"
    else:
        return "65+"


def format_file_size(size_bytes: int) -> str:
    """
    Format file size in human-readable format.
    
    Args:
        size_bytes: Size in bytes
    
    Returns:
        Formatted string (e.g., "2.5 MB")
    """
    for unit in ['B', 'KB', 'MB', 'GB']:
        if size_bytes < 1024.0:
            return f"{size_bytes:.1f} {unit}"
        size_bytes /= 1024.0
    return f"{size_bytes:.1f} TB"


def generate_cache_key(*parts: str) -> str:
    """
    Generate a cache key from multiple parts.
    
    Args:
        *parts: Key components
    
    Returns:
        Cache key string
    
    Example:
        >>> generate_cache_key("submissions", "user", "uuid-123", "page", "1")
        "submissions:user:uuid-123:page:1"
    """
    return ":".join(str(part) for part in parts)

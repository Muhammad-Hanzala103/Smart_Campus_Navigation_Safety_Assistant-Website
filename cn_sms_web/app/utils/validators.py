"""
Input Validation Utilities
Provides validation functions for API input data.
"""
import re
from typing import Tuple, Optional


def validate_email(email: str) -> Tuple[bool, Optional[str]]:
    """
    Validate email format.
    
    Returns:
        (is_valid, error_message)
    """
    if not email:
        return False, "Email is required"
    
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    if not re.match(pattern, email):
        return False, "Invalid email format"
    
    if len(email) > 120:
        return False, "Email must be less than 120 characters"
    
    return True, None


def validate_password(password: str) -> Tuple[bool, Optional[str]]:
    """
    Validate password strength.
    
    Requirements:
    - Minimum 6 characters
    - At least one letter and one number (for production)
    
    Returns:
        (is_valid, error_message)
    """
    if not password:
        return False, "Password is required"
    
    if len(password) < 6:
        return False, "Password must be at least 6 characters"
    
    if len(password) > 128:
        return False, "Password must be less than 128 characters"
    
    return True, None


def validate_name(name: str) -> Tuple[bool, Optional[str]]:
    """
    Validate user name.
    
    Returns:
        (is_valid, error_message)
    """
    if not name:
        return False, "Name is required"
    
    if len(name) < 2:
        return False, "Name must be at least 2 characters"
    
    if len(name) > 100:
        return False, "Name must be less than 100 characters"
    
    return True, None


def validate_incident_data(data: dict) -> Tuple[bool, Optional[str]]:
    """
    Validate incident creation data.
    
    Returns:
        (is_valid, error_message)
    """
    if not data.get('description'):
        return False, "Description is required"
    
    if len(data.get('description', '')) > 2000:
        return False, "Description must be less than 2000 characters"
    
    return True, None


def allowed_file(filename: str, allowed_extensions: set) -> bool:
    """Check if file extension is allowed."""
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in allowed_extensions

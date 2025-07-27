"""Utility functions."""

import re
from typing import Any, Dict, List, Optional


def validate_email(email: str) -> bool:
    """Validate email format."""
    pattern = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
    return bool(re.match(pattern, email))


def validate_password(password: str) -> tuple[bool, List[str]]:
    """Validate password complexity.

    Returns:
        tuple: (is_valid, list_of_errors)
    """
    errors = []

    if len(password) < 8:
        errors.append("Password must be at least 8 characters long")

    if not re.search(r"[A-Z]", password):
        errors.append("Password must contain at least one uppercase letter")

    if not re.search(r"[a-z]", password):
        errors.append("Password must contain at least one lowercase letter")

    if not re.search(r"\d", password):
        errors.append("Password must contain at least one number")

    return len(errors) == 0, errors


def validate_username(username: str) -> tuple[bool, Optional[str]]:
    """Validate username format.

    Returns:
        tuple: (is_valid, error_message)
    """
    if len(username) < 3:
        return False, "Username must be at least 3 characters long"

    if len(username) > 50:
        return False, "Username must be at most 50 characters long"

    if not re.match(r"^[a-zA-Z0-9_-]+$", username):
        return (
            False,
            "Username can only contain letters, numbers, underscores, and hyphens",
        )

    return True, None


def clean_dict(
    data: Dict[str, Any], exclude_none: bool = True, exclude_empty: bool = False
) -> Dict[str, Any]:
    """Clean dictionary by removing None or empty values."""
    cleaned = {}

    for key, value in data.items():
        if exclude_none and value is None:
            continue

        if exclude_empty and not value:
            continue

        cleaned[key] = value

    return cleaned


def get_client_ip(request: Any) -> str:
    """Get client IP address from request."""
    # Check for X-Forwarded-For header (behind proxy)
    forwarded_for = request.headers.get("X-Forwarded-For")
    if forwarded_for:
        # Get the first IP in the chain
        return str(forwarded_for.split(",")[0].strip())

    # Check for X-Real-IP header
    real_ip = request.headers.get("X-Real-IP")
    if real_ip:
        return str(real_ip)

    # Fall back to direct connection
    return str(request.client.host) if request.client else "unknown"


def get_user_agent(request: Any) -> Optional[str]:
    """Get user agent from request."""
    user_agent = request.headers.get("User-Agent")
    return str(user_agent) if user_agent is not None else None


def mask_email(email: str) -> str:
    """Mask email address for privacy."""
    if "@" not in email:
        return email

    local, domain = email.split("@", 1)

    if len(local) <= 1:
        return f"{local}*@{domain}"
    elif len(local) == 2:
        return f"{local[0]}*@{domain}"
    elif len(local) <= 4:
        return f"{local[0]}*{local[-1]}@{domain}"
    else:
        # Show first 2 and last 2 characters with asterisks in between
        masked_length = len(local) - 4
        return f"{local[:2]}{'*' * masked_length}{local[-2:]}@{domain}"


def paginate_query(
    query: Any,
    page: int = 1,
    per_page: int = 20,
    max_per_page: int = 100,
) -> tuple[Any, Dict[str, Any]]:
    """Apply pagination to a query.

    Returns:
        tuple: (paginated_query, pagination_info)
    """
    # Validate inputs
    page = max(1, page)
    per_page = min(max(1, per_page), max_per_page)

    # Calculate offset
    offset = (page - 1) * per_page

    # Apply pagination
    paginated = query.limit(per_page).offset(offset)

    # Pagination info
    pagination_info = {
        "page": page,
        "per_page": per_page,
        "offset": offset,
    }

    return paginated, pagination_info


def generate_slug(text: str) -> str:
    """Generate URL-friendly slug from text."""
    # Convert to lowercase
    slug = text.lower()

    # Replace spaces and special characters with hyphens
    slug = re.sub(r"[^a-z0-9]+", "-", slug)

    # Remove leading/trailing hyphens
    slug = slug.strip("-")

    # Replace multiple hyphens with single hyphen
    slug = re.sub(r"-+", "-", slug)

    return slug

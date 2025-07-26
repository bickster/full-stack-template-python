"""Unit tests for utility functions."""

import pytest

from app.core.utils import (
    clean_dict,
    generate_slug,
    mask_email,
    paginate_query,
    validate_email,
    validate_password,
    validate_username,
)


class TestValidation:
    """Test validation functions."""

    def test_validate_email_valid(self):
        """Test valid email addresses."""
        valid_emails = [
            "test@example.com",
            "user.name@example.com",
            "user+tag@example.co.uk",
            "123@example.com",
        ]
        for email in valid_emails:
            assert validate_email(email) is True

    def test_validate_email_invalid(self):
        """Test invalid email addresses."""
        invalid_emails = [
            "invalid",
            "@example.com",
            "user@",
            "user @example.com",
            "user@example",
            "",
        ]
        for email in invalid_emails:
            assert validate_email(email) is False

    def test_validate_password_valid(self):
        """Test valid passwords."""
        valid, errors = validate_password("ValidPass123")
        assert valid is True
        assert errors == []

    def test_validate_password_invalid(self):
        """Test invalid passwords."""
        test_cases = [
            ("short", ["Password must be at least 8 characters long"]),
            ("alllowercase", [
                "Password must be at least 8 characters long",
                "Password must contain at least one uppercase letter",
                "Password must contain at least one number",
            ]),
            ("ALLUPPERCASE", [
                "Password must be at least 8 characters long",
                "Password must contain at least one lowercase letter",
                "Password must contain at least one number",
            ]),
            ("NoNumbers!", [
                "Password must contain at least one number",
            ]),
        ]
        
        for password, expected_errors in test_cases:
            valid, errors = validate_password(password)
            assert valid is False
            assert set(errors) == set(expected_errors)

    def test_validate_username_valid(self):
        """Test valid usernames."""
        valid_usernames = [
            "user123",
            "test_user",
            "user-name",
            "User_123",
        ]
        for username in valid_usernames:
            valid, error = validate_username(username)
            assert valid is True
            assert error is None

    def test_validate_username_invalid(self):
        """Test invalid usernames."""
        test_cases = [
            ("ab", "Username must be at least 3 characters long"),
            ("a" * 51, "Username must be at most 50 characters long"),
            ("user@name", "Username can only contain letters, numbers, underscores, and hyphens"),
            ("user name", "Username can only contain letters, numbers, underscores, and hyphens"),
        ]
        
        for username, expected_error in test_cases:
            valid, error = validate_username(username)
            assert valid is False
            assert error == expected_error


class TestUtilityFunctions:
    """Test utility functions."""

    def test_clean_dict_exclude_none(self):
        """Test cleaning dict by excluding None values."""
        data = {"a": 1, "b": None, "c": "test", "d": None}
        result = clean_dict(data, exclude_none=True)
        assert result == {"a": 1, "c": "test"}

    def test_clean_dict_exclude_empty(self):
        """Test cleaning dict by excluding empty values."""
        data = {"a": 1, "b": "", "c": [], "d": "test", "e": 0}
        result = clean_dict(data, exclude_none=False, exclude_empty=True)
        assert result == {"a": 1, "d": "test"}

    def test_mask_email(self):
        """Test email masking."""
        test_cases = [
            ("test@example.com", "te**st@example.com"),
            ("a@example.com", "a*@example.com"),
            ("ab@example.com", "a*@example.com"),
            ("abc@example.com", "a*c@example.com"),
            ("longusername@example.com", "lo*********me@example.com"),
        ]
        
        for email, expected in test_cases:
            assert mask_email(email) == expected

    def test_mask_email_invalid(self):
        """Test masking invalid email."""
        assert mask_email("notanemail") == "notanemail"

    def test_generate_slug(self):
        """Test slug generation."""
        test_cases = [
            ("Hello World", "hello-world"),
            ("Test  Multiple   Spaces", "test-multiple-spaces"),
            ("Special!@#$%Characters", "special-characters"),
            ("Numbers123Test", "numbers123test"),
            ("--Leading-Trailing--", "leading-trailing"),
        ]
        
        for text, expected in test_cases:
            assert generate_slug(text) == expected


class TestPagination:
    """Test pagination function."""

    class MockQuery:
        """Mock query object for testing."""
        
        def __init__(self):
            self.limit_value = None
            self.offset_value = None
        
        def limit(self, value):
            self.limit_value = value
            return self
        
        def offset(self, value):
            self.offset_value = value
            return self

    def test_paginate_query_defaults(self):
        """Test pagination with default values."""
        query = self.MockQuery()
        result, info = paginate_query(query)
        
        assert query.limit_value == 20
        assert query.offset_value == 0
        assert info == {"page": 1, "per_page": 20, "offset": 0}

    def test_paginate_query_custom_values(self):
        """Test pagination with custom values."""
        query = self.MockQuery()
        result, info = paginate_query(query, page=3, per_page=50)
        
        assert query.limit_value == 50
        assert query.offset_value == 100
        assert info == {"page": 3, "per_page": 50, "offset": 100}

    def test_paginate_query_max_per_page(self):
        """Test pagination respects max per page."""
        query = self.MockQuery()
        result, info = paginate_query(query, page=1, per_page=200)
        
        assert query.limit_value == 100  # Max is 100
        assert query.offset_value == 0
        assert info == {"page": 1, "per_page": 100, "offset": 0}

    def test_paginate_query_negative_values(self):
        """Test pagination handles negative values."""
        query = self.MockQuery()
        result, info = paginate_query(query, page=-1, per_page=-10)
        
        assert query.limit_value == 1  # Min is 1
        assert query.offset_value == 0
        assert info == {"page": 1, "per_page": 1, "offset": 0}
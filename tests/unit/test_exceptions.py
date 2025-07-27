"""Unit tests for custom exceptions."""

from starlette.status import (
    HTTP_401_UNAUTHORIZED,
    HTTP_404_NOT_FOUND,
)

from app.core.exceptions import (
    AppException,
    AuthenticationError,
    AuthorizationError,
    ConflictError,
    DatabaseError,
    NotFoundError,
    RateLimitError,
    TokenError,
    ValidationError,
)


class TestAppException:
    """Test AppException base class."""

    def test_app_exception_creation(self):
        """Test creating an app exception."""
        exc = AppException(message="Test error", code="TEST_ERROR")
        assert exc.message == "Test error"
        assert exc.code == "TEST_ERROR"
        assert exc.status_code == 500

    def test_app_exception_with_custom_status(self):
        """Test app exception with custom status code."""
        exc = AppException(
            message="Custom error",
            code="CUSTOM_ERROR",
            status_code=HTTP_401_UNAUTHORIZED,
        )
        assert exc.status_code == HTTP_401_UNAUTHORIZED

    def test_app_exception_with_details(self):
        """Test app exception with details."""
        details = {"field": "error details"}
        exc = AppException(
            message="Error with details",
            code="DETAILED_ERROR",
            details=details,
        )
        assert exc.details == details


class TestSpecificExceptions:
    """Test specific exception classes."""

    def test_authentication_error(self):
        """Test AuthenticationError exception."""
        exc = AuthenticationError("Invalid credentials")
        assert exc.message == "Invalid credentials"
        assert exc.code == "AUTH_ERROR"
        assert exc.status_code == 401

    def test_authorization_error(self):
        """Test AuthorizationError exception."""
        exc = AuthorizationError("Insufficient permissions")
        assert exc.message == "Insufficient permissions"
        assert exc.code == "FORBIDDEN"
        assert exc.status_code == 403

    def test_not_found_error(self):
        """Test NotFoundError exception."""
        exc = NotFoundError("Resource not found")
        assert exc.message == "Resource not found"
        assert exc.code == "NOT_FOUND"
        assert exc.status_code == HTTP_404_NOT_FOUND

    def test_conflict_error(self):
        """Test ConflictError exception."""
        exc = ConflictError("Resource already exists")
        assert exc.message == "Resource already exists"
        assert exc.code == "CONFLICT"
        assert exc.status_code == 409

    def test_validation_error(self):
        """Test ValidationError exception."""
        exc = ValidationError("Invalid input")
        assert exc.message == "Invalid input"
        assert exc.code == "VALIDATION_ERROR"
        assert exc.status_code == 400

    def test_rate_limit_error(self):
        """Test RateLimitError exception."""
        exc = RateLimitError("Rate limit exceeded")
        assert exc.message == "Rate limit exceeded"
        assert exc.code == "RATE_LIMIT_EXCEEDED"
        assert exc.status_code == 429

    def test_exception_with_default_message(self):
        """Test exception with default message."""
        exc = NotFoundError()
        assert exc.message == "Resource not found"
        assert exc.code == "NOT_FOUND"

    def test_exception_str_representation(self):
        """Test string representation of exceptions."""
        exc = ValidationError("Test validation error")
        assert str(exc) == "Test validation error"

    def test_token_error(self):
        """Test TokenError exception."""
        exc = TokenError("Invalid token")
        assert exc.message == "Invalid token"
        assert exc.code == "TOKEN_ERROR"
        assert exc.status_code == 401

    def test_database_error(self):
        """Test DatabaseError exception."""
        exc = DatabaseError("Connection failed")
        assert exc.message == "Connection failed"
        assert exc.code == "DATABASE_ERROR"
        assert exc.status_code == 500

    def test_exception_defaults(self):
        """Test exceptions with default messages."""
        auth_exc = AuthenticationError()
        assert auth_exc.message == "Authentication failed"

        not_found_exc = NotFoundError()
        assert not_found_exc.message == "Resource not found"

        conflict_exc = ConflictError()
        assert conflict_exc.message == "Resource conflict"

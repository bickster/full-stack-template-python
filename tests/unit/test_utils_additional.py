"""Additional unit tests for utils module."""

from unittest.mock import Mock

from app.core.utils import get_client_ip, get_user_agent


class TestRequestUtils:
    """Test request utility functions."""

    def test_get_client_ip_from_forwarded_header(self):
        """Test getting client IP from X-Forwarded-For header."""
        mock_request = Mock()
        mock_request.headers = {"X-Forwarded-For": "192.168.1.1, 10.0.0.1"}
        mock_request.client = None

        ip = get_client_ip(mock_request)
        assert ip == "192.168.1.1"

    def test_get_client_ip_from_real_ip_header(self):
        """Test getting client IP from X-Real-IP header."""
        mock_request = Mock()
        mock_request.headers = {"X-Real-IP": "192.168.1.2"}
        mock_request.client = None

        ip = get_client_ip(mock_request)
        assert ip == "192.168.1.2"

    def test_get_client_ip_from_direct_connection(self):
        """Test getting client IP from direct connection."""
        mock_request = Mock()
        mock_request.headers = {}
        mock_request.client = Mock(host="192.168.1.3")

        ip = get_client_ip(mock_request)
        assert ip == "192.168.1.3"

    def test_get_client_ip_no_client(self):
        """Test getting client IP when no client info available."""
        mock_request = Mock()
        mock_request.headers = {}
        mock_request.client = None

        ip = get_client_ip(mock_request)
        assert ip == "unknown"

    def test_get_user_agent_present(self):
        """Test getting user agent when present."""
        mock_request = Mock()
        mock_request.headers = {"User-Agent": "Mozilla/5.0 Test Browser"}

        agent = get_user_agent(mock_request)
        assert agent == "Mozilla/5.0 Test Browser"

    def test_get_user_agent_missing(self):
        """Test getting user agent when missing."""
        mock_request = Mock()
        mock_request.headers = {}

        agent = get_user_agent(mock_request)
        assert agent is None

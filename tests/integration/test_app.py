"""Integration tests for main app endpoints."""

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
class TestAppEndpoints:
    """Test main application endpoints."""

    async def test_root_endpoint(self, client: AsyncClient):
        """Test root endpoint."""
        response = await client.get("/")

        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert "FullStack App" in data["message"]

    async def test_health_check(self, client: AsyncClient):
        """Test health check endpoint."""
        response = await client.get("/health")

        assert response.status_code == 200
        data = response.json()
        assert data["status"] in ["healthy", "unhealthy"]
        assert "database" in data
        assert "version" in data

    async def test_metrics_endpoint(self, client: AsyncClient):
        """Test Prometheus metrics endpoint."""
        response = await client.get("/metrics")

        assert response.status_code == 200
        # Check for Prometheus format
        assert "# HELP" in response.text
        assert "# TYPE" in response.text

    async def test_404_endpoint(self, client: AsyncClient):
        """Test non-existent endpoint."""
        response = await client.get("/api/v1/nonexistent")

        assert response.status_code == 404
        data = response.json()
        assert "error" in data
        assert data["code"] == "HTTP_404"

    async def test_cors_headers(self, client: AsyncClient):
        """Test CORS headers are present."""
        response = await client.options(
            "/api/v1/auth/login",
            headers={"Origin": "http://localhost:3000"},
        )

        # CORS headers should be present
        assert "access-control-allow-origin" in response.headers
        assert "access-control-allow-methods" in response.headers

    async def test_security_headers(self, client: AsyncClient):
        """Test security headers are present."""
        response = await client.get("/")

        # Security headers
        assert response.headers.get("x-content-type-options") == "nosniff"
        assert response.headers.get("x-frame-options") == "DENY"
        assert response.headers.get("x-xss-protection") == "1; mode=block"
        assert "strict-transport-security" in response.headers
        # Server header should be removed
        assert "server" not in response.headers

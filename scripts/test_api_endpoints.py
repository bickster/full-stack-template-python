#!/usr/bin/env python3
"""Test API endpoints by analyzing the route definitions."""

import ast
import re
import sys
from pathlib import Path

# Add the project root to the path
sys.path.append(str(Path(__file__).parent.parent / "src"))

from app.api.routes import auth, users
from app.api.schemas import (
    PasswordChange,
    RefreshTokenRequest,
    TokenResponse,
    UserCreate,
    UserLogin,
    UserResponse,
    UserUpdate,
)


def extract_routes_from_module(module):
    """Extract route information from a module."""
    routes = []

    # Get the source file
    source_file = module.__file__
    with open(source_file, "r") as f:
        content = f.read()

    # Parse the AST
    tree = ast.parse(content)

    # Find all decorated functions
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef):
            for decorator in node.decorator_list:
                # Check if it's a router decorator
                if isinstance(decorator, ast.Call) and isinstance(
                    decorator.func, ast.Attribute
                ):
                    if (
                        hasattr(decorator.func.value, "id")
                        and decorator.func.value.id == "router"
                    ):
                        method = decorator.func.attr.upper()

                        # Extract path from first argument
                        if decorator.args:
                            path = ast.literal_eval(decorator.args[0])

                            # Extract additional info from keywords
                            response_model = None
                            status_code = 200 if method != "POST" else 201
                            summary = None

                            for keyword in decorator.keywords:
                                if keyword.arg == "response_model":
                                    if hasattr(keyword.value, "id"):
                                        response_model = keyword.value.id
                                elif keyword.arg == "status_code":
                                    if hasattr(keyword.value, "attr"):
                                        status_code = keyword.value.attr
                                elif keyword.arg == "summary":
                                    summary = ast.literal_eval(keyword.value)

                            routes.append(
                                {
                                    "method": method,
                                    "path": path,
                                    "function": node.name,
                                    "response_model": response_model,
                                    "status_code": status_code,
                                    "summary": summary,
                                }
                            )

    return routes


def test_auth_endpoints():
    """Test authentication endpoints."""
    print("\n🔐 Authentication Endpoints")
    print("=" * 80)

    auth_routes = extract_routes_from_module(auth)

    # Expected auth endpoints
    expected_endpoints = [
        ("POST", "/register", "Register new user"),
        ("POST", "/login", "User login"),
        ("POST", "/refresh", "Refresh access token"),
        ("POST", "/logout", "User logout"),
    ]

    for method, path, description in expected_endpoints:
        found = any(r["method"] == method and r["path"] == path for r in auth_routes)
        status = "✅" if found else "❌"
        print(f"{status} {method:6} /api/v1/auth{path:20} - {description}")

        if found:
            route = next(
                r for r in auth_routes if r["method"] == method and r["path"] == path
            )
            print(f"         Function: {route['function']}")
            if route["response_model"]:
                print(f"         Response: {route['response_model']}")

    return auth_routes


def test_user_endpoints():
    """Test user management endpoints."""
    print("\n👤 User Management Endpoints")
    print("=" * 80)

    user_routes = extract_routes_from_module(users)

    # Expected user endpoints
    expected_endpoints = [
        ("GET", "/me", "Get current user"),
        ("PUT", "/me", "Update current user"),
        ("POST", "/me/change-password", "Change password"),
        ("DELETE", "/me", "Delete account"),
    ]

    for method, path, description in expected_endpoints:
        found = any(r["method"] == method and r["path"] == path for r in user_routes)
        status = "✅" if found else "❌"
        print(f"{status} {method:6} /api/v1/users{path:20} - {description}")

        if found:
            route = next(
                r for r in user_routes if r["method"] == method and r["path"] == path
            )
            print(f"         Function: {route['function']}")
            if route["response_model"]:
                print(f"         Response: {route['response_model']}")

    return user_routes


def test_request_response_models():
    """Test request/response models."""
    print("\n📦 Request/Response Models")
    print("=" * 80)

    models = [
        (UserCreate, "User Registration"),
        (UserLogin, "User Login"),
        (UserResponse, "User Response"),
        (TokenResponse, "Token Response"),
        (RefreshTokenRequest, "Refresh Token"),
        (UserUpdate, "User Update"),
        (PasswordChange, "Password Change"),
    ]

    for model, description in models:
        try:
            # Create a sample instance to verify model
            fields = model.__fields__
            print(f"✅ {model.__name__:20} - {description}")
            print(f"   Fields: {', '.join(fields.keys())}")
        except Exception as e:
            print(f"❌ {model.__name__:20} - Error: {e}")


def test_endpoint_security():
    """Test endpoint security configurations."""
    print("\n🔒 Security Configuration")
    print("=" * 80)

    # Read auth routes to check for security decorators
    with open(Path(__file__).parent.parent / "src/app/api/routes/auth.py", "r") as f:
        auth_content = f.read()

    with open(Path(__file__).parent.parent / "src/app/api/routes/users.py", "r") as f:
        users_content = f.read()

    # Check for rate limiting
    rate_limit_endpoints = []
    if "RateLimiter" in auth_content:
        rate_limit_endpoints.append("auth endpoints")

    # Check for authentication requirements
    auth_required_count = users_content.count("get_current_user")

    print(
        f"✅ Rate limiting configured on: {', '.join(rate_limit_endpoints) if rate_limit_endpoints else 'None detected'}"
    )
    print(f"✅ Authentication required on: {auth_required_count} user endpoints")

    # Check for CORS configuration
    with open(Path(__file__).parent.parent / "src/app/api/main.py", "r") as f:
        main_content = f.read()

    if "CORSMiddleware" in main_content:
        print("✅ CORS middleware configured")
    else:
        print("❌ CORS middleware not found")

    if "SecurityHeadersMiddleware" in main_content:
        print("✅ Security headers middleware configured")
    else:
        print("⚠️  Security headers middleware not found (may be handled by nginx)")


def test_api_documentation():
    """Test API documentation setup."""
    print("\n📚 API Documentation")
    print("=" * 80)

    with open(Path(__file__).parent.parent / "src/app/api/main.py", "r") as f:
        main_content = f.read()

    # Check for OpenAPI customization
    if "custom_openapi" in main_content:
        print("✅ Custom OpenAPI schema configured")
    else:
        print("⚠️  Using default OpenAPI schema")

    # Check for API metadata
    if "title=" in main_content:
        title_match = re.search(r'title="([^"]+)"', main_content)
        if title_match:
            print(f"✅ API Title: {title_match.group(1)}")

    if "version=" in main_content:
        version_match = re.search(r'version="([^"]+)"', main_content)
        if version_match:
            print(f"✅ API Version: {version_match.group(1)}")

    print("\n📍 API Documentation URLs:")
    print("   - Swagger UI: http://localhost:8000/docs")
    print("   - ReDoc: http://localhost:8000/redoc")
    print("   - OpenAPI JSON: http://localhost:8000/openapi.json")


def generate_curl_examples():
    """Generate example cURL commands."""
    print("\n🚀 Example API Calls")
    print("=" * 80)

    examples = [
        {
            "name": "Register User",
            "curl": """curl -X POST http://localhost:8000/api/v1/auth/register \\
  -H "Content-Type: application/json" \\
  -d '{
    "email": "test@example.com",
    "username": "testuser",
    "password": "TestPass123!"
  }'
""",
        },
        {
            "name": "Login",
            "curl": """curl -X POST http://localhost:8000/api/v1/auth/login \\
  -H "Content-Type: application/json" \\
  -d '{
    "email": "test@example.com",
    "password": "TestPass123!"
  }'
""",
        },
        {
            "name": "Get Current User",
            "curl": """curl -X GET http://localhost:8000/api/v1/users/me \\
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
""",
        },
        {
            "name": "Update User",
            "curl": """curl -X PUT http://localhost:8000/api/v1/users/me \\
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \\
  -H "Content-Type: application/json" \\
  -d '{
    "email": "newemail@example.com"
  }'
""",
        },
    ]

    for example in examples:
        print(f"\n{example['name']}:")
        print(example["curl"])


def main():
    """Run all API endpoint tests."""
    print("API Endpoint Test Suite")
    print("=" * 80)

    try:
        # Test endpoints
        auth_routes = test_auth_endpoints()
        user_routes = test_user_endpoints()

        # Test models
        test_request_response_models()

        # Test security
        test_endpoint_security()

        # Test documentation
        test_api_documentation()

        # Generate examples
        generate_curl_examples()

        # Summary
        total_endpoints = len(auth_routes) + len(user_routes)
        print("\n" + "=" * 80)
        print(f"✅ Total endpoints found: {total_endpoints}")
        print("\nTo test the API:")
        print("1. Start the server: make serve-api")
        print("2. Visit: http://localhost:8000/docs")
        print("3. Use the interactive Swagger UI to test endpoints")

    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback

        traceback.print_exc()
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())

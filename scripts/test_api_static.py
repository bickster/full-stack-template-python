#!/usr/bin/env python3
"""Test API endpoints by static analysis of route files."""

import re
from pathlib import Path
from typing import List, Dict, Tuple


def parse_route_file(file_path: Path) -> List[Dict[str, str]]:
    """Parse a route file to extract endpoint information."""
    endpoints = []
    
    with open(file_path, 'r') as f:
        content = f.read()
    
    # Pattern to match route decorators
    # Matches: @router.get("/path", ...)
    route_pattern = r'@router\.(get|post|put|delete|patch)\s*\(\s*["\']([^"\']+)["\']'
    
    # Pattern to match function definitions
    func_pattern = r'async def (\w+)\s*\('
    
    # Find all routes
    route_matches = list(re.finditer(route_pattern, content))
    
    for i, match in enumerate(route_matches):
        method = match.group(1).upper()
        path = match.group(2)
        
        # Find the function name after this decorator
        start_pos = match.end()
        func_match = re.search(func_pattern, content[start_pos:])
        
        if func_match:
            func_name = func_match.group(1)
            
            # Extract additional metadata from the decorator line
            decorator_end = content.find('\n', match.start())
            decorator_text = content[match.start():decorator_end]
            
            # Extract response_model
            response_model = None
            model_match = re.search(r'response_model=(\w+)', decorator_text)
            if model_match:
                response_model = model_match.group(1)
            
            # Extract summary
            summary = None
            summary_match = re.search(r'summary=["\']([^"\']+)["\']', decorator_text)
            if summary_match:
                summary = summary_match.group(1)
            
            # Check if it requires authentication
            func_end = content.find('\n):', start_pos)
            func_signature = content[start_pos:func_end] if func_end > 0 else content[start_pos:start_pos+200]
            requires_auth = 'current_user' in func_signature or 'get_current_user' in func_signature
            
            endpoints.append({
                'method': method,
                'path': path,
                'function': func_name,
                'response_model': response_model,
                'summary': summary,
                'requires_auth': requires_auth
            })
    
    return endpoints


def test_auth_routes():
    """Test authentication routes."""
    print("\n🔐 Authentication Endpoints (/api/v1/auth)")
    print("=" * 80)
    
    auth_file = Path(__file__).parent.parent / "src/app/api/routes/auth.py"
    endpoints = parse_route_file(auth_file)
    
    expected = [
        ('POST', '/register', 'User registration'),
        ('POST', '/login', 'User login'),
        ('POST', '/refresh', 'Token refresh'),
        ('POST', '/logout', 'User logout'),
    ]
    
    for method, path, desc in expected:
        found = False
        for ep in endpoints:
            if ep['method'] == method and ep['path'] == path:
                found = True
                auth_str = "🔓" if not ep['requires_auth'] else "🔒"
                print(f"✅ {auth_str} {method:6} {path:20} - {desc}")
                print(f"     Function: {ep['function']}")
                if ep['response_model']:
                    print(f"     Response: {ep['response_model']}")
                break
        
        if not found:
            print(f"❌ {method:6} {path:20} - {desc} [NOT FOUND]")
    
    return endpoints


def test_user_routes():
    """Test user management routes."""
    print("\n👤 User Management Endpoints (/api/v1/users)")
    print("=" * 80)
    
    users_file = Path(__file__).parent.parent / "src/app/api/routes/users.py"
    endpoints = parse_route_file(users_file)
    
    expected = [
        ('GET', '/me', 'Get current user'),
        ('PUT', '/me', 'Update user profile'),
        ('POST', '/me/change-password', 'Change password'),
        ('DELETE', '/me', 'Delete account'),
    ]
    
    for method, path, desc in expected:
        found = False
        for ep in endpoints:
            if ep['method'] == method and ep['path'] == path:
                found = True
                auth_str = "🔓" if not ep['requires_auth'] else "🔒"
                print(f"✅ {auth_str} {method:6} {path:20} - {desc}")
                print(f"     Function: {ep['function']}")
                if ep['response_model']:
                    print(f"     Response: {ep['response_model']}")
                break
        
        if not found:
            print(f"❌ {method:6} {path:20} - {desc} [NOT FOUND]")
    
    return endpoints


def analyze_schemas():
    """Analyze Pydantic schemas."""
    print("\n📦 Request/Response Schemas")
    print("=" * 80)
    
    schemas_file = Path(__file__).parent.parent / "src/app/api/schemas.py"
    
    with open(schemas_file, 'r') as f:
        content = f.read()
    
    # Extract class definitions
    class_pattern = r'class (\w+).*?:'
    classes = re.findall(class_pattern, content)
    
    # Categorize schemas
    request_schemas = [c for c in classes if 'Request' in c or 'Create' in c or 'Update' in c or 'Login' in c or 'Change' in c]
    response_schemas = [c for c in classes if 'Response' in c]
    base_schemas = [c for c in classes if c not in request_schemas and c not in response_schemas]
    
    print("Request Schemas:")
    for schema in sorted(request_schemas):
        print(f"  ✅ {schema}")
    
    print("\nResponse Schemas:")
    for schema in sorted(response_schemas):
        print(f"  ✅ {schema}")
    
    if base_schemas:
        print("\nBase/Other Schemas:")
        for schema in sorted(base_schemas):
            print(f"  ✅ {schema}")


def analyze_dependencies():
    """Analyze API dependencies and middleware."""
    print("\n🔧 Dependencies & Middleware")
    print("=" * 80)
    
    deps_file = Path(__file__).parent.parent / "src/app/api/dependencies.py"
    main_file = Path(__file__).parent.parent / "src/app/api/main.py"
    
    # Check dependencies
    with open(deps_file, 'r') as f:
        deps_content = f.read()
    
    deps_found = []
    if 'get_current_user' in deps_content:
        deps_found.append("Authentication (get_current_user)")
    if 'get_current_active_user' in deps_content:
        deps_found.append("Active user check")
    if 'RateLimiter' in deps_content:
        deps_found.append("Rate limiting")
    if 'get_db' in deps_content:
        deps_found.append("Database session")
    
    print("Dependencies:")
    for dep in deps_found:
        print(f"  ✅ {dep}")
    
    # Check middleware
    with open(main_file, 'r') as f:
        main_content = f.read()
    
    middleware_found = []
    if 'CORSMiddleware' in main_content:
        middleware_found.append("CORS")
    if 'TrustedHostMiddleware' in main_content:
        middleware_found.append("Trusted Host")
    if 'SecurityHeadersMiddleware' in main_content:
        middleware_found.append("Security Headers")
    if 'RequestValidationError' in main_content:
        middleware_found.append("Validation Error Handler")
    
    print("\nMiddleware:")
    for mw in middleware_found:
        print(f"  ✅ {mw}")


def generate_api_test_plan():
    """Generate a test plan for manual API testing."""
    print("\n📋 Manual API Test Plan")
    print("=" * 80)
    
    test_scenarios = [
        {
            'name': '1. User Registration Flow',
            'steps': [
                'POST /api/v1/auth/register with valid data',
                'Verify 201 response with user data',
                'Try duplicate email (should fail)',
                'Try weak password (should fail)',
                'Try invalid email format (should fail)'
            ]
        },
        {
            'name': '2. Authentication Flow',
            'steps': [
                'POST /api/v1/auth/login with valid credentials',
                'Verify token response (access_token, refresh_token)',
                'Use access_token in Authorization header',
                'GET /api/v1/users/me to verify auth works',
                'Try invalid credentials (should fail)'
            ]
        },
        {
            'name': '3. Token Refresh Flow',
            'steps': [
                'Wait for access token to expire (or use short expiry)',
                'POST /api/v1/auth/refresh with refresh_token',
                'Verify new access_token is issued',
                'Old access_token should be invalid',
                'Try with invalid refresh_token (should fail)'
            ]
        },
        {
            'name': '4. User Profile Management',
            'steps': [
                'GET /api/v1/users/me (verify current data)',
                'PUT /api/v1/users/me with updated email',
                'POST /api/v1/users/me/change-password',
                'Verify login works with new password',
                'Try unauthorized access (should fail)'
            ]
        },
        {
            'name': '5. Security Testing',
            'steps': [
                'Test rate limiting on login endpoint',
                'Verify CORS headers in responses',
                'Check security headers (X-Frame-Options, etc)',
                'Test SQL injection on login',
                'Test XSS in user inputs'
            ]
        }
    ]
    
    for scenario in test_scenarios:
        print(f"\n{scenario['name']}:")
        for step in scenario['steps']:
            print(f"  □ {step}")


def generate_postman_collection():
    """Generate a basic Postman collection structure."""
    print("\n📮 Postman Collection Template")
    print("=" * 80)
    
    collection = {
        "info": {
            "name": "Full-Stack Template API",
            "schema": "https://schema.getpostman.com/json/collection/v2.1.0/collection.json"
        },
        "auth": {
            "type": "bearer",
            "bearer": [{"key": "token", "value": "{{access_token}}", "type": "string"}]
        },
        "variable": [
            {"key": "base_url", "value": "http://localhost:8000"},
            {"key": "access_token", "value": ""},
            {"key": "refresh_token", "value": ""}
        ]
    }
    
    print("Create a Postman collection with:")
    print(f"  - Base URL: {{base_url}}")
    print(f"  - Auth: Bearer Token ({{access_token}})")
    print(f"  - Variables: access_token, refresh_token")
    print("\nOr import the OpenAPI spec directly:")
    print("  1. Start the API server")
    print("  2. In Postman: Import > Link > http://localhost:8000/openapi.json")


def main():
    """Run all API tests."""
    print("API Endpoint Static Analysis")
    print("=" * 80)
    print("Analyzing API routes without running the server...")
    
    try:
        # Test routes
        auth_endpoints = test_auth_routes()
        user_endpoints = test_user_routes()
        
        # Analyze schemas
        analyze_schemas()
        
        # Analyze dependencies
        analyze_dependencies()
        
        # Generate test plan
        generate_api_test_plan()
        
        # Generate Postman info
        generate_postman_collection()
        
        # Summary
        total_endpoints = len(auth_endpoints) + len(user_endpoints)
        auth_required = sum(1 for ep in auth_endpoints + user_endpoints if ep['requires_auth'])
        
        print("\n" + "=" * 80)
        print("📊 Summary:")
        print(f"  - Total endpoints: {total_endpoints}")
        print(f"  - Public endpoints: {total_endpoints - auth_required}")
        print(f"  - Protected endpoints: {auth_required}")
        print("\n🚀 Next Steps:")
        print("  1. Start PostgreSQL: docker-compose up -d db")
        print("  2. Run migrations: make migrate")
        print("  3. Start API: make serve-api")
        print("  4. Test endpoints: http://localhost:8000/docs")
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    return 0


if __name__ == "__main__":
    import sys
    sys.exit(main())
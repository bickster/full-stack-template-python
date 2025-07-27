#!/usr/bin/env python3
"""Validate Docker configurations for the full-stack template."""

import os
import sys
import yaml
import re
from pathlib import Path


def check_dockerfile(dockerfile_path: Path, service_name: str) -> list[str]:
    """Check Dockerfile for best practices."""
    issues = []
    
    if not dockerfile_path.exists():
        return [f"Dockerfile not found: {dockerfile_path}"]
    
    content = dockerfile_path.read_text()
    lines = content.splitlines()
    
    # Check for multi-stage build
    if content.count("FROM") < 2:
        issues.append(f"{service_name}: Not using multi-stage build (recommended for smaller images)")
    
    # Check for non-root user
    if "USER" not in content:
        issues.append(f"{service_name}: Running as root (security risk)")
    
    # Check for HEALTHCHECK
    if "HEALTHCHECK" not in content:
        issues.append(f"{service_name}: No HEALTHCHECK defined")
    
    # Check for proper COPY with chown
    if service_name == "API" and "--chown=" not in content:
        issues.append(f"{service_name}: COPY without --chown may create permission issues")
    
    # Check for security updates
    if "apt-get upgrade" not in content and "apk upgrade" not in content:
        issues.append(f"{service_name}: Not applying security updates")
    
    # Check for cache cleanup
    if "apt-get" in content and "rm -rf /var/lib/apt/lists/*" not in content:
        issues.append(f"{service_name}: Not cleaning apt cache")
    
    return issues


def check_docker_compose(compose_path: Path) -> list[str]:
    """Check docker-compose.yml for best practices."""
    issues = []
    
    if not compose_path.exists():
        return ["docker-compose.yml not found"]
    
    with open(compose_path, 'r') as f:
        compose = yaml.safe_load(f)
    
    services = compose.get('services', {})
    
    # Check database service
    if 'db' in services:
        db = services['db']
        
        # Check for persistent volume
        if 'volumes' not in db:
            issues.append("Database: No persistent volume configured")
        
        # Check for healthcheck
        if 'healthcheck' not in db:
            issues.append("Database: No healthcheck configured")
        
        # Check environment variables
        env = db.get('environment', {})
        if 'POSTGRES_PASSWORD' in env and env['POSTGRES_PASSWORD'] == 'password':
            issues.append("Database: Using default password (security risk)")
    
    # Check API service
    if 'api' in services:
        api = services['api']
        
        # Check depends_on with condition
        depends = api.get('depends_on', {})
        if isinstance(depends, dict) and 'db' in depends:
            if 'condition' not in depends['db']:
                issues.append("API: Not waiting for database health")
        
        # Check environment variables
        env = api.get('environment', {})
        if 'DATABASE_URL' not in env:
            issues.append("API: DATABASE_URL not configured")
        
        if 'SECRET_KEY' in env and 'change-this' in str(env['SECRET_KEY']):
            issues.append("API: Using default SECRET_KEY (security risk)")
    
    # Check frontend service
    if 'frontend' in services:
        frontend = services['frontend']
        
        # Check API URL configuration
        env = frontend.get('environment', {})
        if 'VITE_API_URL' not in env:
            issues.append("Frontend: VITE_API_URL not configured")
    
    # Check for network configuration
    if 'networks' not in compose:
        issues.append("No custom network defined (using default bridge)")
    
    return issues


def check_nginx_config(nginx_path: Path) -> list[str]:
    """Check nginx configuration."""
    issues = []
    
    if not nginx_path.exists():
        return ["nginx.conf not found"]
    
    content = nginx_path.read_text()
    
    # Check for security headers
    security_headers = [
        'X-Frame-Options',
        'X-Content-Type-Options',
        'X-XSS-Protection',
        'Strict-Transport-Security'
    ]
    
    for header in security_headers:
        if header not in content:
            issues.append(f"Nginx: Missing security header {header}")
    
    # Check for rate limiting
    if 'limit_req' not in content:
        issues.append("Nginx: No rate limiting configured")
    
    # Check for gzip compression
    if 'gzip on' not in content:
        issues.append("Nginx: Gzip compression not enabled")
    
    # Check for SSL configuration
    if 'ssl_protocols' not in content:
        issues.append("Nginx: No SSL configuration (needed for production)")
    
    return issues


def check_requirements() -> list[str]:
    """Check if required files exist."""
    issues = []
    
    required_files = [
        'requirements.txt',
        'ui/package.json',
        '.dockerignore',
        '.env.example'
    ]
    
    for file in required_files:
        if not Path(file).exists():
            issues.append(f"Missing required file: {file}")
    
    return issues


def validate_env_example() -> list[str]:
    """Check .env.example for required variables."""
    issues = []
    
    env_path = Path('.env.example')
    if not env_path.exists():
        return ["Missing .env.example file"]
    
    content = env_path.read_text()
    required_vars = [
        'DATABASE_URL',
        'SECRET_KEY',
        'POSTGRES_USER',
        'POSTGRES_PASSWORD',
        'POSTGRES_DB'
    ]
    
    for var in required_vars:
        if var not in content:
            issues.append(f"Missing environment variable in .env.example: {var}")
    
    return issues


def check_dockerignore() -> list[str]:
    """Check .dockerignore file."""
    issues = []
    
    dockerignore_path = Path('.dockerignore')
    if not dockerignore_path.exists():
        return [".dockerignore file missing (will copy unnecessary files)"]
    
    content = dockerignore_path.read_text()
    recommended_ignores = [
        '__pycache__',
        '*.pyc',
        '.env',
        '.git',
        'node_modules',
        'dist',
        'coverage',
        '.pytest_cache',
        'venv'
    ]
    
    missing = []
    for ignore in recommended_ignores:
        if ignore not in content:
            missing.append(ignore)
    
    if missing:
        issues.append(f".dockerignore: Consider adding {', '.join(missing)}")
    
    return issues


def main():
    """Run all Docker validation checks."""
    print("Docker Configuration Validation")
    print("=" * 80)
    
    all_issues = []
    
    # Check Dockerfiles
    print("\n📋 Checking Dockerfiles...")
    api_issues = check_dockerfile(Path('docker/Dockerfile'), 'API')
    frontend_issues = check_dockerfile(Path('docker/Dockerfile.frontend'), 'Frontend')
    all_issues.extend(api_issues)
    all_issues.extend(frontend_issues)
    
    # Check docker-compose
    print("\n📋 Checking docker-compose.yml...")
    compose_issues = check_docker_compose(Path('docker-compose.yml'))
    all_issues.extend(compose_issues)
    
    # Check nginx config
    print("\n📋 Checking nginx configuration...")
    nginx_issues = check_nginx_config(Path('docker/nginx.conf'))
    all_issues.extend(nginx_issues)
    
    # Check requirements
    print("\n📋 Checking required files...")
    req_issues = check_requirements()
    all_issues.extend(req_issues)
    
    # Check environment variables
    print("\n📋 Checking environment variables...")
    env_issues = validate_env_example()
    all_issues.extend(env_issues)
    
    # Check dockerignore
    print("\n📋 Checking .dockerignore...")
    ignore_issues = check_dockerignore()
    all_issues.extend(ignore_issues)
    
    # Report results
    print("\n" + "=" * 80)
    if all_issues:
        print("❌ Found issues:\n")
        for issue in all_issues:
            print(f"  - {issue}")
        
        print(f"\nTotal issues: {len(all_issues)}")
        
        # Categorize by severity
        security_issues = [i for i in all_issues if 'security' in i.lower() or 'root' in i or 'password' in i]
        if security_issues:
            print(f"\n⚠️  Security issues: {len(security_issues)}")
            
    else:
        print("✅ All Docker configurations look good!")
        
    print("\n📦 Docker Build Commands:")
    print("  docker-compose build       # Build all services")
    print("  docker-compose up -d       # Start all services")
    print("  docker-compose logs -f     # View logs")
    print("  docker-compose down        # Stop all services")
    
    return 0 if not all_issues else 1


if __name__ == "__main__":
    sys.exit(main())
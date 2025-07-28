#!/bin/bash

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to print colored output
print_success() { echo -e "${GREEN}✓ $1${NC}"; }
print_error() { echo -e "${RED}✗ $1${NC}"; }
print_info() { echo -e "${YELLOW}ℹ $1${NC}"; }

echo "🏥 Health Check"
echo "==============="
echo ""

# Check Docker containers
print_info "Checking Docker containers..."
if docker-compose ps | grep -q "fullstack_db.*Up"; then
    print_success "Database container is running"
else
    print_error "Database container is not running"
fi

# Check database connection
print_info "Checking database connection..."
if docker-compose exec -T db pg_isready -U postgres > /dev/null 2>&1; then
    print_success "Database is accepting connections"
else
    print_error "Database is not accepting connections"
fi

# Check backend API
print_info "Checking backend API..."
if curl -s http://localhost:8000/health > /dev/null 2>&1; then
    HEALTH=$(curl -s http://localhost:8000/health | python3 -c "import sys, json; print(json.load(sys.stdin)['status'])")
    if [ "$HEALTH" = "healthy" ]; then
        print_success "Backend API is healthy"
    else
        print_error "Backend API is unhealthy"
    fi
else
    print_error "Backend API is not running"
fi

# Check frontend
print_info "Checking frontend..."
if curl -s http://localhost:3000 > /dev/null 2>&1; then
    print_success "Frontend is running"
else
    print_error "Frontend is not running"
fi

# Check Redis (if configured)
if [ ! -z "$REDIS_URL" ]; then
    print_info "Checking Redis..."
    if docker-compose ps | grep -q "redis.*Up"; then
        print_success "Redis is running"
    else
        print_error "Redis is not running"
    fi
fi

echo ""
echo "Health check complete!"

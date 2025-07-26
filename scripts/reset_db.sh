#!/bin/bash
set -e

echo "⚠️  Database Reset Script"
echo "========================"
echo ""
echo "This will completely reset your database!"
echo "All data will be lost."
echo ""

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to print colored output
print_success() { echo -e "${GREEN}✓ $1${NC}"; }
print_error() { echo -e "${RED}✗ $1${NC}"; }
print_info() { echo -e "${YELLOW}ℹ $1${NC}"; }

# Confirmation prompt
read -p "Are you sure you want to continue? (yes/no): " -r
echo
if [[ ! $REPLY =~ ^[Yy][Ee][Ss]$ ]]; then
    print_info "Database reset cancelled."
    exit 0
fi

# Check if virtual environment is activated
if [ -z "$VIRTUAL_ENV" ]; then
    print_info "Activating virtual environment..."
    source venv/bin/activate
fi

# Stop any running servers
print_info "Stopping any running servers..."
pkill -f "uvicorn" || true
pkill -f "npm run dev" || true

# Drop and recreate database using Docker
print_info "Resetting database..."
docker-compose exec -T db psql -U postgres << EOF
DROP DATABASE IF EXISTS fullstack_db;
CREATE DATABASE fullstack_db;
EOF
print_success "Database recreated"

# Run migrations
print_info "Running database migrations..."
alembic upgrade head
print_success "Migrations completed"

# Initialize database with default data
print_info "Initializing database with default data..."
python scripts/setup_db.py
print_success "Database initialized"

echo ""
echo "✅ Database reset complete!"
echo ""
echo "Default superuser credentials:"
echo "Email: admin@example.com"
echo "Password: admin123"
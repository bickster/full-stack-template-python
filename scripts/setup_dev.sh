#!/bin/bash
set -e

echo "🚀 Setting up Full-Stack App Development Environment"
echo "=================================================="

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to print colored output
print_success() { echo -e "${GREEN}✓ $1${NC}"; }
print_error() { echo -e "${RED}✗ $1${NC}"; }
print_info() { echo -e "${YELLOW}ℹ $1${NC}"; }

# Check if Python 3.11+ is installed
print_info "Checking Python version..."
if ! python3 --version | grep -E "3\.(11|12)" > /dev/null; then
    print_error "Python 3.11+ is required. Please install it first."
    exit 1
fi
print_success "Python $(python3 --version) found"

# Check if Node.js 20+ is installed
print_info "Checking Node.js version..."
if ! node --version | grep -E "v(2[0-9]|[3-9][0-9])" > /dev/null; then
    print_error "Node.js 20+ is required. Please install it first."
    exit 1
fi
print_success "Node.js $(node --version) found"

# Check if Docker is installed
print_info "Checking Docker..."
if ! command -v docker &> /dev/null; then
    print_error "Docker is not installed. Please install Docker first."
    exit 1
fi
print_success "Docker found"

# Check if Docker Compose is installed
print_info "Checking Docker Compose..."
if ! command -v docker-compose &> /dev/null && ! docker compose version &> /dev/null; then
    print_error "Docker Compose is not installed. Please install it first."
    exit 1
fi
print_success "Docker Compose found"

# Create .env file if it doesn't exist
if [ ! -f .env ]; then
    print_info "Creating .env file..."
    cp .env.example .env
    print_success ".env file created (please update with your values)"
else
    print_info ".env file already exists"
fi

# Create UI .env file if it doesn't exist
if [ ! -f ui/.env ]; then
    print_info "Creating ui/.env file..."
    cp ui/.env.example ui/.env
    print_success "ui/.env file created"
else
    print_info "ui/.env file already exists"
fi

# Set up Python virtual environment
print_info "Setting up Python virtual environment..."
if [ ! -d "venv" ]; then
    python3 -m venv venv
    print_success "Virtual environment created"
else
    print_info "Virtual environment already exists"
fi

# Activate virtual environment
source venv/bin/activate

# Upgrade pip
print_info "Upgrading pip..."
pip install --upgrade pip > /dev/null 2>&1
print_success "pip upgraded"

# Install Python dependencies
print_info "Installing Python dependencies..."
pip install -r requirements-dev.txt
print_success "Python dependencies installed"

# Install pre-commit hooks
print_info "Installing pre-commit hooks..."
pre-commit install
print_success "Pre-commit hooks installed"

# Install Node.js dependencies
print_info "Installing Node.js dependencies..."
cd ui && npm install
cd ..
print_success "Node.js dependencies installed"

# Start Docker containers
print_info "Starting Docker containers..."
docker-compose up -d db
print_success "Database container started"

# Wait for database to be ready
print_info "Waiting for database to be ready..."
sleep 5

# Run database migrations
print_info "Running database migrations..."
alembic upgrade head
print_success "Database migrations completed"

# Initialize database
print_info "Initializing database..."
python scripts/setup_db.py
print_success "Database initialized"

echo ""
echo "🎉 Development environment setup complete!"
echo ""
echo "Next steps:"
echo "1. Activate the virtual environment: source venv/bin/activate"
echo "2. Start the backend server: make serve-api"
echo "3. Start the frontend server: make serve-frontend"
echo "4. Visit http://localhost:3000"
echo ""
echo "Default superuser credentials:"
echo "Email: admin@example.com"
echo "Password: admin123"
echo ""
echo "Run 'make help' to see all available commands"

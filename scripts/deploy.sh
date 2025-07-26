#!/bin/bash
set -e

# Production Deployment Script

echo "🚀 Production Deployment Script"
echo "=============================="
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

# Check if production environment file exists
if [ ! -f .env.production ]; then
    print_error ".env.production file not found!"
    exit 1
fi

# Load environment
export $(cat .env.production | grep -v '^#' | xargs)

# Deployment steps
print_info "Starting deployment process..."

# 1. Pull latest code
print_info "Pulling latest code..."
git pull origin main
print_success "Code updated"

# 2. Build images
print_info "Building Docker images..."
docker-compose -f docker-compose.production.yml build
print_success "Images built"

# 3. Run database migrations
print_info "Running database migrations..."
docker-compose -f docker-compose.production.yml run --rm api alembic upgrade head
print_success "Migrations completed"

# 4. Stop old containers
print_info "Stopping old containers..."
docker-compose -f docker-compose.production.yml down
print_success "Old containers stopped"

# 5. Start new containers
print_info "Starting new containers..."
docker-compose -f docker-compose.production.yml up -d
print_success "New containers started"

# 6. Wait for services to be healthy
print_info "Waiting for services to be healthy..."
sleep 10

# 7. Health check
print_info "Running health checks..."
if curl -f http://localhost/health > /dev/null 2>&1; then
    print_success "Application is healthy"
else
    print_error "Health check failed!"
    print_info "Check logs with: docker-compose -f docker-compose.production.yml logs"
    exit 1
fi

# 8. Clean up old images
print_info "Cleaning up old Docker images..."
docker image prune -f
print_success "Cleanup completed"

echo ""
echo "✅ Deployment completed successfully!"
echo ""
echo "Next steps:"
echo "1. Verify application at https://$DOMAIN"
echo "2. Check logs: docker-compose -f docker-compose.production.yml logs -f"
echo "3. Monitor metrics at https://$DOMAIN/metrics"
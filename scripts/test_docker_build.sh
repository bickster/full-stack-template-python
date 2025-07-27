#!/bin/bash

echo "Docker Build Test Script"
echo "======================="
echo ""

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check if Docker is installed (would fail in this environment)
if ! command -v docker &> /dev/null; then
    echo -e "${YELLOW}Docker is not available in this environment${NC}"
    echo "This script validates the configuration files only"
    echo ""
fi

# Validate Dockerfile syntax
echo "Checking Dockerfile syntax..."
for dockerfile in docker/Dockerfile docker/Dockerfile.frontend; do
    if [ -f "$dockerfile" ]; then
        # Check for basic Dockerfile syntax
        if grep -q "^FROM" "$dockerfile" && grep -q "^CMD\|^ENTRYPOINT" "$dockerfile"; then
            echo -e "${GREEN}✓${NC} $dockerfile has valid structure"
        else
            echo -e "${RED}✗${NC} $dockerfile missing FROM or CMD/ENTRYPOINT"
        fi
    else
        echo -e "${RED}✗${NC} $dockerfile not found"
    fi
done

echo ""
echo "Checking docker-compose.yml..."
if [ -f "docker-compose.yml" ]; then
    # Use Python to validate YAML
    python3 -c "import yaml; yaml.safe_load(open('docker-compose.yml'))" 2>/dev/null
    if [ $? -eq 0 ]; then
        echo -e "${GREEN}✓${NC} docker-compose.yml is valid YAML"
        
        # Check for required services
        for service in db api frontend nginx; do
            if grep -q "^  $service:" docker-compose.yml; then
                echo -e "${GREEN}✓${NC} Service '$service' is defined"
            else
                echo -e "${RED}✗${NC} Service '$service' is missing"
            fi
        done
    else
        echo -e "${RED}✗${NC} docker-compose.yml has invalid YAML syntax"
    fi
else
    echo -e "${RED}✗${NC} docker-compose.yml not found"
fi

echo ""
echo "Build commands (when Docker is available):"
echo "  docker-compose build --no-cache    # Build all images"
echo "  docker-compose up -d               # Start services"
echo "  docker-compose ps                  # Check status"
echo "  docker-compose logs -f api         # View API logs"
echo ""
echo "To test locally with Docker:"
echo "  1. Install Docker Desktop"
echo "  2. Run: docker-compose up --build"
echo "  3. Access: http://localhost:3000 (frontend)"
echo "  4. Access: http://localhost:8000/docs (API)"
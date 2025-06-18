#!/bin/bash
set -e

# Development startup script for Outline single container

echo "Starting Outline development environment..."

# Check if we're in the right directory
if [ ! -f "package.json" ]; then
    echo "Error: package.json not found. Please run this script from the Outline project root."
    exit 1
fi

# Build the development container
echo "Building development container..."
docker-compose -f docker-compose.single.yml build

# Start the services
echo "Starting services..."
docker-compose -f docker-compose.single.yml up -d

# Wait a moment for services to start
sleep 5

# Install dependencies if node_modules doesn't exist or is empty
echo "Checking dependencies..."
if ! docker exec outline-dev test -d "/opt/outline/node_modules/.bin" 2>/dev/null; then
    echo "Installing dependencies..."
    docker exec outline-dev yarn install
fi

# Run database migrations
echo "Running database migrations..."
docker exec outline-dev yarn db:migrate

echo ""
echo "Development environment is ready!"
echo ""
echo "Access points:"
echo "  - Outline Dev Server: http://localhost:3000"
echo "  - Nginx Proxy: http://localhost"
echo "  - VNC Web Client: http://localhost:6080/vnc.html"
echo "  - PostgreSQL: localhost:5432 (user: outline, password: outline_password)"
echo "  - Redis: localhost:6379"
echo ""
echo "Development commands:"
echo "  - View logs: docker-compose -f docker-compose.single.yml logs -f"
echo "  - Shell access: docker exec -it outline-dev bash"
echo "  - Restart Outline: docker exec outline-dev dinitctl restart outline"
echo "  - Install packages: docker exec outline-dev yarn add <package>"
echo "  - Run tests: docker exec outline-dev yarn test"
echo "  - Run linting: docker exec outline-dev yarn lint"
echo ""
echo "The source code is mounted from the current directory."
echo "Changes to the code will trigger automatic rebuilds."
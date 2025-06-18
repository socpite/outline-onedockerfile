#!/bin/bash
set -e

# Agent startup script for Outline container

echo "Starting Outline agent development environment..."

# Build the agent container
echo "Building agent container..."
docker-compose -f docker-compose.single.yml build

# Start the services
echo "Starting services..."
docker-compose -f docker-compose.single.yml up -d

# Wait for services to start
echo "Waiting for services to initialize..."
sleep 10

# Run database migrations
echo "Running database migrations..."
docker exec outline-agent yarn db:migrate

# Build the application initially
echo "Building Outline application..."
docker exec outline-agent agent-rebuild

echo ""
echo "Agent development environment is ready!"
echo ""
echo "Access points:"
echo "  - Outline Application: http://localhost:3000"
echo "  - VNC Web Client: http://localhost:6080/vnc.html (password: outline)"
echo "  - Direct VNC: localhost:5900"
echo ""
echo "Agent commands (run inside container):"
echo "  - agent-screenshot    # Take screenshot"
echo "  - agent-rebuild       # Rebuild application"
echo "  - agent-restart       # Restart Outline service"
echo "  - agent-status        # Show service status"
echo "  - agent-logs          # Show recent logs"
echo "  - agent-test          # Run tests"
echo ""
echo "Container access:"
echo "  - Shell: docker exec -it outline-agent bash"
echo "  - Logs: docker-compose -f docker-compose.single.yml logs -f"
echo ""
echo "Source code location: /opt/outline"
echo "Screenshots location: /home/outline/screenshots"
echo ""
echo "The agent can:"
echo "  1. Edit files in /opt/outline"
echo "  2. Run 'agent-rebuild' to build changes"
echo "  3. Run 'agent-restart' to restart the service"
echo "  4. Run 'agent-screenshot' to capture the GUI"
echo "  5. Use xdotool for GUI automation"
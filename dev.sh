#!/bin/bash
# Agent helper script for Outline

CONTAINER_NAME="outline-agent"

case "$1" in
    "start")
        echo "Starting agent environment..."
        ./agent-start.sh
        ;;
    "stop")
        echo "Stopping agent environment..."
        docker-compose -f docker-compose.single.yml down
        ;;
    "restart")
        echo "Restarting agent environment..."
        docker-compose -f docker-compose.single.yml restart
        ;;
    "logs")
        echo "Showing logs..."
        docker-compose -f docker-compose.single.yml logs -f
        ;;
    "shell")
        echo "Opening shell in container..."
        docker exec -it $CONTAINER_NAME bash
        ;;
    "screenshot")
        echo "Taking screenshot..."
        docker exec $CONTAINER_NAME agent-screenshot
        echo "Screenshot saved to screenshots volume"
        ;;
    "rebuild")
        echo "Rebuilding application..."
        docker exec $CONTAINER_NAME agent-rebuild
        ;;
    "restart-outline")
        echo "Restarting Outline service..."
        docker exec $CONTAINER_NAME agent-restart
        ;;
    "status")
        echo "Checking status..."
        docker exec $CONTAINER_NAME agent-status
        ;;
    "outline-logs")
        echo "Showing Outline service logs..."
        docker exec $CONTAINER_NAME agent-logs
        ;;
    "db-shell")
        echo "Opening PostgreSQL shell..."
        docker exec -it $CONTAINER_NAME sudo -u postgres psql -d outline
        ;;
    "redis-cli")
        echo "Opening Redis CLI..."
        docker exec -it $CONTAINER_NAME redis-cli
        ;;
    "test")
        echo "Running tests..."
        docker exec $CONTAINER_NAME agent-test
        ;;
    "edit")
        if [ -z "$2" ]; then
            echo "Usage: $0 edit <filename>"
            echo "Example: $0 edit app/components/Button.tsx"
            exit 1
        fi
        echo "Opening file for editing: $2"
        docker exec -it $CONTAINER_NAME nano "/opt/outline/$2"
        ;;
    "find")
        if [ -z "$2" ]; then
            echo "Usage: $0 find <pattern>"
            echo "Example: $0 find '*.tsx'"
            exit 1
        fi
        echo "Finding files matching: $2"
        docker exec $CONTAINER_NAME find /opt/outline -name "$2" -type f
        ;;
    "grep")
        if [ -z "$2" ]; then
            echo "Usage: $0 grep <pattern> [path]"
            echo "Example: $0 grep 'Button' app/"
            exit 1
        fi
        path=${3:-"/opt/outline"}
        echo "Searching for: $2 in $path"
        docker exec $CONTAINER_NAME grep -r "$2" "$path"
        ;;
    "tree")
        path=${2:-"/opt/outline"}
        echo "Directory tree for: $path"
        docker exec $CONTAINER_NAME tree -L 3 "$path"
        ;;
    "vnc")
        echo "VNC access information:"
        echo "  Web VNC: http://localhost:6080/vnc.html"
        echo "  Direct VNC: localhost:5900 (password: outline)"
        echo "  Screenshot: ./dev.sh screenshot"
        ;;
    "copy-screenshots")
        echo "Copying screenshots from container..."
        docker cp $CONTAINER_NAME:/home/outline/screenshots ./screenshots
        echo "Screenshots copied to ./screenshots/"
        ;;
    *)
        echo "Outline Agent Development Helper"
        echo ""
        echo "Usage: $0 <command>"
        echo ""
        echo "Environment commands:"
        echo "  start          Start the agent environment"
        echo "  stop           Stop the agent environment"
        echo "  restart        Restart the agent environment"
        echo "  logs           Show all service logs"
        echo "  shell          Open bash shell in container"
        echo ""
        echo "Development commands:"
        echo "  rebuild        Rebuild the application"
        echo "  restart-outline Restart only the Outline service"
        echo "  test           Run tests"
        echo "  status         Show service status"
        echo "  outline-logs   Show Outline service logs"
        echo ""
        echo "File operations:"
        echo "  edit <file>    Edit a file with nano"
        echo "  find <pattern> Find files matching pattern"
        echo "  grep <pattern> [path] Search for text in files"
        echo "  tree [path]    Show directory tree"
        echo ""
        echo "Database commands:"
        echo "  db-shell       Open PostgreSQL shell"
        echo "  redis-cli      Open Redis CLI"
        echo ""
        echo "Agent commands:"
        echo "  screenshot     Take a screenshot"
        echo "  copy-screenshots Copy screenshots to host"
        echo "  vnc            Show VNC access information"
        echo ""
        echo "Example workflow:"
        echo "  $0 start                    # Start environment"
        echo "  $0 edit app/components/Button.tsx  # Edit a file"
        echo "  $0 rebuild                  # Rebuild application"
        echo "  $0 screenshot               # Take screenshot"
        ;;
esac
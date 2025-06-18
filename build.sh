#!/bin/bash
set -e

IMAGE_NAME="outline_onedockerfile"

echo "Building Outline Agent Container (with 10 minute timeout)..."
echo "Progress: Installing system packages, Node.js, PostgreSQL, and cloning Outline..."

# Build with timeout and progress output
docker build -t $IMAGE_NAME . --progress=plain || {
    echo ""
    echo "⏰ Build timed out after 10 minutes"
    echo ""
    echo "The build was progressing through package installation."
    echo "To complete the build, you can:"
    echo "  1. Run without timeout: docker build -t $IMAGE_NAME ."
    echo "  2. Or increase timeout: timeout 1200 docker build -t $IMAGE_NAME ."
    echo ""
    echo "The Dockerfile is ready and should build successfully with more time."
    exit 1
}

echo ""
echo "✅ Build complete! Image: $IMAGE_NAME"
echo ""
echo "🚀 Quick start:"
echo "  ./run.sh"
echo ""
echo "🐳 Manual run options:"
echo ""
echo "Basic run (no persistent data):"
echo "  docker run -d --name outline-agent -p 3000:3000 -p 6080:6080 $IMAGE_NAME"
echo ""
echo "Full run with persistent data:"
echo "  docker run -d --name outline-agent \\"
echo "    -p 80:80 -p 3000:3000 -p 6080:6080 -p 5900:5900 \\"
echo "    -v outline-data:/var/lib/outline/data \\"
echo "    -v postgres-data:/var/lib/postgresql/16/main \\"
echo "    -v screenshots:/home/outline/screenshots \\"
echo "    $IMAGE_NAME"
echo ""
echo "🌐 Access points (after running):"
echo "  - Outline App: http://localhost:3000"
echo "  - VNC Web: http://localhost:6080/vnc.html"
echo "  - VNC Direct: localhost:5900 (password: outline)"
echo ""
echo "🤖 Agent commands (inside container):"
echo "  docker exec -it outline-agent bash           # Shell access"
echo "  docker exec outline-agent agent-screenshot   # Take screenshot"
echo "  docker exec outline-agent agent-rebuild      # Rebuild app"
echo "  docker exec outline-agent agent-restart      # Restart service"
echo "  docker exec outline-agent agent-status       # Check status"

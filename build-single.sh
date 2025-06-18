#!/bin/bash
set -e

# Build script for Outline single container

echo "Building Outline single container with PostgreSQL, Redis, and X11/VNC..."

# Build the container
docker build -f Dockerfile.single -t outline-single:latest .

echo "Build complete!"
echo ""
echo "To run the container:"
echo "  docker run -d --name outline-single -p 80:80 -p 6080:6080 -v outline-data:/var/lib/outline/data outline-single:latest"
echo ""
echo "Access points:"
echo "  - Outline Web UI: http://localhost"
echo "  - VNC Web Client: http://localhost:6080/vnc.html"
echo "  - Direct VNC: localhost:5900 (password: outline)"
echo ""
echo "To view logs:"
echo "  docker logs outline-single"
echo ""
echo "To access container shell:"
echo "  docker exec -it outline-single bash"
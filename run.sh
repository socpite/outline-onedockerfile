#!/bin/bash

IMAGE_NAME="outline_onedockerfile"
CONTAINER_NAME="outline-agent"

# Check if container already exists
if docker ps -a --format 'table {{.Names}}' | grep -q "^${CONTAINER_NAME}$"; then
    echo "Container $CONTAINER_NAME already exists."
    echo "Starting existing container..."
    docker start $CONTAINER_NAME
else
    echo "Creating and starting new container..."
    docker run -d --name $CONTAINER_NAME \
        -p 80:80 \
        -p 3000:3000 \
        -p 6080:6080 \
        -p 5900:5900 \
        -p 5432:5432 \
        -p 6379:6379 \
        -v outline-data:/var/lib/outline/data \
        -v postgres-data:/var/lib/postgresql/16/main \
        -v screenshots:/home/outline/screenshots \
        $IMAGE_NAME
fi

echo ""
echo "Container is starting..."
echo "Waiting for services to initialize (this may take a minute)..."
sleep 10

echo ""
echo "Container is ready!"
echo ""
echo "Access points:"
echo "  - Outline App: http://localhost:3000"
echo "  - VNC Web Client: http://localhost:6080/vnc.html"
echo "  - VNC Direct: localhost:5900 (password: outline)"
echo ""
echo "Agent commands:"
echo "  docker exec -it $CONTAINER_NAME bash                 # Shell access"
echo "  docker exec $CONTAINER_NAME agent-screenshot         # Take screenshot"
echo "  docker exec $CONTAINER_NAME agent-rebuild            # Rebuild app"
echo "  docker exec $CONTAINER_NAME agent-restart            # Restart service"
echo "  docker exec $CONTAINER_NAME agent-status             # Check status"
echo "  docker exec $CONTAINER_NAME agent-logs               # View logs"
echo ""
echo "View logs:"
echo "  docker logs -f $CONTAINER_NAME"
echo ""
echo "Stop container:"
echo "  docker stop $CONTAINER_NAME"
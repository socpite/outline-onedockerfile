# Outline Agent Development Container

This container provides a complete development environment for AI agents to work with the Outline codebase, including GUI access via VNC and screenshot capabilities.

## Quick Start for Agents

```bash
# Start the environment
./agent-start.sh

# Access the container
docker exec -it outline-agent bash

# Inside the container, agents can:
agent-screenshot          # Take a screenshot
agent-rebuild            # Rebuild the application
agent-restart            # Restart the service
agent-status             # Check service status
```

## Agent Capabilities

### 1. Code Editing
The Outline source code is located at `/opt/outline` inside the container:

```bash
# Navigate to source
cd /opt/outline

# Edit files
nano app/components/Button.tsx
vim server/routes/auth.ts

# View file structure
tree -L 3 .
find . -name "*.tsx" | head -10
```

### 2. Building and Testing
```bash
# Rebuild application after changes
agent-rebuild

# Restart the service to see changes
agent-restart

# Run tests
agent-test

# Check if everything is working
agent-status
```

### 3. Visual Feedback
```bash
# Take a screenshot of the current GUI state
agent-screenshot

# Screenshots are saved to:
# - /home/outline/screenshots/latest.png (latest)
# - /home/outline/screenshots/screenshot-YYYYMMDD-HHMMSS.png (timestamped)
```

### 4. GUI Automation
The container includes `xdotool` for GUI automation:

```bash
# Click at coordinates
DISPLAY=:1 xdotool mousemove 100 200 click 1

# Type text
DISPLAY=:1 xdotool type "Hello World"

# Press keys
DISPLAY=:1 xdotool key ctrl+s

# Get window information
DISPLAY=:1 xdotool search --name "firefox"
```

### 5. Database Operations
```bash
# Connect to PostgreSQL
sudo -u postgres psql -d outline

# Check database status
pg_isready -h localhost -p 5432

# Run migrations
yarn db:migrate
```

## Development Workflow for Agents

### 1. Explore the Codebase
```bash
# Find React components
find /opt/outline -name "*.tsx" -path "*/components/*"

# Find API routes
find /opt/outline -name "*.ts" -path "*/routes/*"

# Search for specific functionality
grep -r "authentication" /opt/outline/server/
grep -r "Button" /opt/outline/app/components/
```

### 2. Make Changes
```bash
# Edit a component
nano /opt/outline/app/components/Button.tsx

# Edit server code
nano /opt/outline/server/routes/auth.ts

# Add new files
touch /opt/outline/app/components/NewComponent.tsx
```

### 3. Test Changes
```bash
# Rebuild the application
agent-rebuild

# Restart the service
agent-restart

# Take a screenshot to see the result
agent-screenshot

# Check logs for errors
agent-logs
```

### 4. Verify Results
```bash
# Check service status
agent-status

# View the application in browser (via VNC)
# Open Firefox in the VNC session and navigate to http://localhost:3000

# Take screenshots to document changes
agent-screenshot
```

## File Structure

Key directories in `/opt/outline`:

```
/opt/outline/
├── app/                 # Frontend React application
│   ├── components/      # React components
│   ├── scenes/         # Page components
│   ├── stores/         # MobX stores
│   └── utils/          # Utility functions
├── server/             # Backend Node.js application
│   ├── routes/         # API routes
│   ├── models/         # Database models
│   ├── services/       # Business logic
│   └── utils/          # Server utilities
├── shared/             # Shared code between frontend/backend
├── public/             # Static assets
└── build/              # Built application (after yarn build)
```

## Environment Details

### Services Running
- **Outline**: http://localhost:3000 (development server)
- **PostgreSQL**: localhost:5432 (user: outline, password: outline_password)
- **Redis**: localhost:6379
- **VNC**: localhost:5900 (password: outline)
- **Web VNC**: http://localhost:6080/vnc.html

### Agent Helper Commands
- `agent-screenshot` - Take screenshot
- `agent-rebuild` - Build application
- `agent-restart` - Restart Outline service
- `agent-status` - Show service status
- `agent-logs` - Show recent logs
- `agent-test` - Run tests
- `agent-dev-server` - Start dev server manually

### GUI Tools Available
- **Firefox** - Web browser for testing
- **VS Code** - Code editor (run `code` in terminal)
- **Terminal** - XFCE terminal
- **File Manager** - Thunar file manager

## External Access (from host)

```bash
# Helper script commands
./dev.sh screenshot      # Take screenshot
./dev.sh rebuild         # Rebuild application
./dev.sh shell          # Access container shell
./dev.sh edit <file>    # Edit file with nano
./dev.sh find "*.tsx"   # Find files
./dev.sh grep "Button"  # Search in files

# Copy screenshots to host
./dev.sh copy-screenshots
```

## Tips for Agents

1. **Always take screenshots** after making changes to see visual results
2. **Use agent-rebuild** after editing code to compile changes
3. **Use agent-restart** to restart the service and see changes
4. **Check agent-logs** if something isn't working
5. **Use the VNC session** to interact with the browser and test the UI
6. **Screenshots are saved** with timestamps for tracking progress

The environment is designed to give agents complete control over the development process while providing visual feedback through screenshots and GUI access.
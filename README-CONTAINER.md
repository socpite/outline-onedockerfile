# Outline Agent Container - Single Dockerfile

A complete development environment for AI agents to work with Outline, including PostgreSQL, Redis, and X11/VNC GUI access - all in a single Docker container.

## Quick Start

### Build and Run
```bash
# Build the container
./build.sh

# Run the container (with persistent data)
./run.sh

# Or run manually
docker run -d --name outline-agent \
  -p 80:80 -p 3000:3000 -p 6080:6080 -p 5900:5900 \
  -v outline-data:/var/lib/outline/data \
  -v postgres-data:/var/lib/postgresql/16/main \
  -v screenshots:/home/outline/screenshots \
  outline_onedockerfile
```

### Simple Docker Run
```bash
# Minimal run (no persistent data)
docker run -d -p 3000:3000 -p 6080:6080 outline_onedockerfile

# With all ports exposed
docker run -d \
  -p 80:80 \
  -p 3000:3000 \
  -p 6080:6080 \
  -p 5900:5900 \
  -p 5432:5432 \
  -p 6379:6379 \
  outline_onedockerfile
```

## What's Included

### Services
- **Outline Wiki** - Full development environment with hot reloading
- **PostgreSQL 16** - Database with automatic setup
- **Redis** - Caching and session storage
- **Nginx** - Reverse proxy
- **X11/VNC** - Desktop environment with XFCE4
- **NoVNC** - Web-based VNC client

### Development Tools
- **Node.js 20** with Yarn
- **VS Code** - Available in VNC session
- **Firefox** - For testing the web interface
- **Git** - Source control
- **Agent Tools** - xdotool, scrot, imagemagick for automation

### Agent Helper Commands
- `agent-screenshot` - Take screenshots
- `agent-rebuild` - Build the application
- `agent-restart` - Restart Outline service
- `agent-status` - Check all service statuses
- `agent-logs` - View recent logs
- `agent-test` - Run test suite

## Access Points

After running the container:

- **Outline Application**: http://localhost:3000
- **VNC Web Client**: http://localhost:6080/vnc.html
- **Direct VNC**: localhost:5900 (password: `outline`)
- **PostgreSQL**: localhost:5432 (user: `outline`, password: `outline_password`)
- **Redis**: localhost:6379

## Agent Development Workflow

### 1. Access the Container
```bash
docker exec -it outline-agent bash
```

### 2. Explore the Codebase
```bash
cd /opt/outline

# Find React components
find . -name "*.tsx" -path "*/components/*"

# Search for specific code
grep -r "Button" app/components/

# View file structure
tree -L 3 .
```

### 3. Make Changes
```bash
# Edit a component
nano app/components/Button.tsx

# Edit server code
nano server/routes/auth.ts
```

### 4. Build and Test
```bash
# Rebuild the application
agent-rebuild

# Restart the service
agent-restart

# Take a screenshot to see changes
agent-screenshot

# Check if everything is working
agent-status
```

### 5. Visual Testing
- Open VNC web client: http://localhost:6080/vnc.html
- Open Firefox in the VNC session
- Navigate to http://localhost:3000
- Test the changes visually

## File Locations

### Source Code
- **Outline Source**: `/opt/outline`
- **Components**: `/opt/outline/app/components/`
- **Server Code**: `/opt/outline/server/`
- **Shared Code**: `/opt/outline/shared/`

### Data and Logs
- **Application Data**: `/var/lib/outline/data`
- **Screenshots**: `/home/outline/screenshots/`
- **Service Logs**: `/var/log/dinit/`
- **Database Data**: `/var/lib/postgresql/16/main`

## Container Management

### View Logs
```bash
# All container logs
docker logs -f outline-agent

# Specific service logs
docker exec outline-agent agent-logs

# Real-time Outline logs
docker exec outline-agent tail -f /var/log/dinit/outline.log
```

### Service Management
```bash
# Check service status
docker exec outline-agent agent-status

# Restart specific service
docker exec outline-agent dinitctl restart outline

# List all services
docker exec outline-agent dinitctl list
```

### Screenshots
```bash
# Take a screenshot
docker exec outline-agent agent-screenshot

# Copy screenshots to host
docker cp outline-agent:/home/outline/screenshots ./screenshots
```

## Environment Variables

The container uses these default environment variables (can be overridden):

```bash
NODE_ENV=development
DATABASE_URL=postgres://outline:outline_password@localhost:5432/outline
REDIS_URL=redis://localhost:6379
URL=http://localhost:3000
SECRET_KEY=development-secret-key-not-for-production
UTILS_SECRET=development-utils-secret-not-for-production
```

Override with `-e` flags:
```bash
docker run -d \
  -e SECRET_KEY=your-secret-key \
  -e URL=http://your-domain.com \
  -p 3000:3000 -p 6080:6080 \
  outline_onedockerfile
```

## Persistent Data

Use volumes to persist data across container restarts:

```bash
docker run -d \
  -v outline-data:/var/lib/outline/data \
  -v postgres-data:/var/lib/postgresql/16/main \
  -v screenshots:/home/outline/screenshots \
  outline_onedockerfile
```

## Troubleshooting

### Container Won't Start
```bash
# Run in interactive mode to see errors
docker run -it outline_onedockerfile

# Check container logs
docker logs outline-agent
```

### Services Not Working
```bash
# Check service status
docker exec outline-agent agent-status

# View service logs
docker exec outline-agent agent-logs

# Restart all services
docker restart outline-agent
```

### Database Issues
```bash
# Check PostgreSQL
docker exec outline-agent sudo -u postgres pg_isready

# Connect to database
docker exec -it outline-agent sudo -u postgres psql -d outline

# Reset database (WARNING: destroys data)
docker exec outline-agent sudo -u postgres dropdb outline
docker exec outline-agent sudo -u postgres createdb outline
docker exec outline-agent yarn db:migrate
```

## Security Notes

This container is designed for development and agent use. For production:

- Change default passwords
- Use proper SSL/TLS termination
- Restrict network access
- Use secrets management for sensitive data
- Remove development tools and VNC access

## Architecture

The container uses `dinit` as the init system to manage multiple services:

```
dinit (PID 1)
├── PostgreSQL (with auto-initialization)
├── Redis
├── Xvfb (X11 virtual framebuffer)
├── XFCE4 (desktop environment)
├── x11vnc (VNC server)
├── websockify (VNC to WebSocket bridge)
├── Nginx (reverse proxy)
└── Outline (Node.js development server)
```

All services start automatically and have proper dependency management.
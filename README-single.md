# Outline Development Container Setup

This setup runs Outline, PostgreSQL, Redis, and X11/VNC in a single Docker container using `dinit` as the init system, optimized for development.

## Architecture

- **Init System**: `dinit` manages all services with proper dependencies
- **Database**: PostgreSQL 16 with automatic initialization
- **Cache**: Redis server
- **Web Server**: Nginx reverse proxy + direct dev server access
- **Desktop**: XFCE4 desktop environment accessible via VNC
- **VNC Access**: x11vnc + websockify for browser-based access
- **Development**: Source code mounted, hot reloading, debug tools

## Quick Start

### Development Setup (Recommended)

```bash
# Start development environment
./dev-start.sh

# Or use the helper script
./dev.sh start
```

### Manual Setup

```bash
# Build and start
docker-compose -f docker-compose.single.yml up -d

# Install dependencies
docker exec outline-dev yarn install

# Run migrations
docker exec outline-dev yarn db:migrate
```

## Access Points

- **Outline Dev Server**: http://localhost:3000 (direct, with hot reload)
- **Nginx Proxy**: http://localhost (proxied)
- **VNC Web Client**: http://localhost:6080/vnc.html
- **Direct VNC**: localhost:5900 (password: `outline`)
- **PostgreSQL**: localhost:5432 (user: `outline`, password: `outline_password`)
- **Redis**: localhost:6379

## Development Helper Script

Use `./dev.sh <command>` for common tasks:

### Environment Management
- `./dev.sh start` - Start development environment
- `./dev.sh stop` - Stop environment
- `./dev.sh restart` - Restart environment
- `./dev.sh logs` - View all logs
- `./dev.sh shell` - Open container shell

### Development Tasks
- `./dev.sh install [package]` - Install dependencies or add package
- `./dev.sh test` - Run tests
- `./dev.sh lint` - Run linter
- `./dev.sh build` - Build application

### Database Operations
- `./dev.sh db-shell` - PostgreSQL shell
- `./dev.sh migrate` - Run migrations
- `./dev.sh reset-db` - Reset database (⚠️ destroys data)

### Service Management
- `./dev.sh services` - Check service status
- `./dev.sh restart-outline` - Restart only Outline service
- `./dev.sh outline-logs` - View Outline logs

## Development Features

### Source Code Mounting
- Source code is mounted from host to `/opt/outline`
- Changes trigger automatic rebuilds via `yarn dev:watch`
- No need to rebuild container for code changes

### Hot Reloading
- Frontend changes reload automatically
- Backend changes restart the server automatically
- Database schema changes require manual migration

### Debugging
- Development environment with debug logging
- Direct access to all services for debugging
- VS Code can be run in the VNC desktop environment

### Database Development
- PostgreSQL accessible on host port 5432
- Use external tools like pgAdmin, DBeaver, etc.
- Database data persists in Docker volume

### Package Management
- Install packages with `./dev.sh install <package>`
- Node modules cached in Docker volume for faster installs
- Yarn lock file changes require container restart

## Development Workflow

1. **Start Environment**:
   ```bash
   ./dev.sh start
   ```

2. **Make Code Changes**:
   - Edit files in your host editor
   - Changes are automatically reflected in container

3. **Database Changes**:
   ```bash
   ./dev.sh migrate  # Run new migrations
   ```

4. **Add Dependencies**:
   ```bash
   ./dev.sh install lodash  # Add new package
   ```

5. **Test Changes**:
   ```bash
   ./dev.sh test     # Run tests
   ./dev.sh lint     # Check code style
   ```

6. **Debug Issues**:
   ```bash
   ./dev.sh logs           # View all logs
   ./dev.sh outline-logs   # View Outline logs only
   ./dev.sh shell          # Access container shell
   ```

## Logs

Service logs are available in `/var/log/dinit/`:

```bash
# View all logs
docker exec outline-single tail -f /var/log/dinit/*.log

# View specific service
docker exec outline-single tail -f /var/log/dinit/outline.log
```

## Troubleshooting

### Check service status

```bash
docker exec outline-single dinitctl list
```

### Restart a service

```bash
docker exec outline-single dinitctl restart outline
```

### Database issues

```bash
# Check PostgreSQL status
docker exec outline-single sudo -u postgres pg_isready

# Connect to database
docker exec -it outline-single sudo -u postgres psql -d outline
```

### VNC issues

```bash
# Check X server
docker exec outline-single ps aux | grep Xvfb

# Check VNC server
docker exec outline-single ps aux | grep x11vnc
```

## Security Notes

- Change default passwords in production
- Use proper SSL/TLS termination
- Restrict network access as needed
- Consider using secrets management for sensitive data

## Customization

### Adding services

1. Create service file in `/etc/dinit.d/`
2. Add dependencies as needed
3. Link to `/etc/dinit.d/boot.d/` if it should start with boot

### Modifying Outline configuration

Edit `/etc/dinit.d/outline.env` or override via environment variables.

### Desktop applications

Install additional applications in the Dockerfile and they'll be available in the XFCE desktop via VNC.
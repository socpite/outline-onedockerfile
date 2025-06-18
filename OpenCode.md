# Outline Development Guide

## Build/Test Commands
- **Install**: `yarn install --frozen-lockfile`
- **Build**: `yarn build` (cleans, builds frontend with Vite, i18n, then server)
- **Dev**: `yarn dev:watch` (concurrent backend + frontend development)
- **Lint**: `yarn lint` (ESLint for app/server/shared/plugins)
- **Test all**: `yarn test`
- **Test single project**: `yarn test:server`, `yarn test:app`, `yarn test:shared`
- **Test single file**: `yarn test path/to/file.test.ts`
- **Database**: `yarn db:migrate`, `yarn db:create`, `yarn db:reset`

## Code Style Guidelines
- **TypeScript**: Strict mode enabled, use explicit types, avoid `any`
- **Imports**: External packages → `@shared/*` → `@server/*` → `~/` (app) → relative imports
- **Naming**: `camelCase` variables/functions, `PascalCase` components/classes, `UPPER_CASE` constants
- **React**: Functional components with hooks, TypeScript interfaces for props, no React import needed
- **Error handling**: Use `@typescript-eslint/no-floating-promises`, await all promises
- **Formatting**: Prettier with 80 char width, trailing commas, no console.log (use Logger)
- **Database**: Sequelize with TypeScript decorators, models in `server/models/`
- **Testing**: Jest with separate configs for server/app/shared, use `@faker-js/faker` for test data

## VNC Desktop Environment

### Quick Start (Automatic Setup)
1. **Build container**: `docker build -f Dockerfile.single.minimal -t outline_onedockerfile .`
2. **Run container**: `docker run -d --name outline-single -p 80:80 -p 6080:6080 outline_onedockerfile`
3. **Wait for setup**: Container automatically sets up PostgreSQL, Redis, and Outline environment
4. **Check status**: `docker exec outline-single outline-status`
5. **Access VNC**: Open http://localhost:6080/vnc.html in browser

### Automatic Setup Features
- **PostgreSQL**: Automatically initialized with Outline database and user
- **Redis**: Started and configured
- **Environment**: All variables configured and saved to `/tmp/outline-env.sh`
- **VNC Desktop**: Ready immediately with minimal XFCE
- **Status Check**: Use `outline-status` command to verify everything is ready

### Development Workflow (Ready on Startup)
1. **Access VNC**: http://localhost:6080/vnc.html
2. **Open terminal in /home/ubuntu/outline**:
   - **Option 1**: Right-click desktop → Applications → Terminal Emulator
   - **Option 2**: Run `outline-terminal` command (opens in correct directory)
3. **Start development**: `yarn dev:watch`
4. **Access Outline**: http://localhost:3000 (in host browser)

### Essential Commands (All Work Out of the Box)
```bash
# Basic workflow - everything is pre-configured:
cd /home/ubuntu/outline
yarn dev:watch                    # Start development server

# Optional commands (if needed):
yarn install --frozen-lockfile    # Reinstall dependencies
yarn build                        # Rebuild application
yarn db:create                    # Create new databases
yarn db:migrate                   # Run database migrations
```

### What's Pre-configured
- ✅ **Dependencies**: 1300+ packages installed with `yarn install --frozen-lockfile`
- ✅ **Database**: PostgreSQL with `outline` database and user configured
- ✅ **Environment**: All variables set in `/home/ubuntu/outline/.env`
- ✅ **Build system**: Vite and build tools ready
- ✅ **Permissions**: User can create databases and run all commands

### Terminal Configuration
- **Default directory**: `/home/ubuntu/outline` (automatically set)
- **Environment**: Environment variables in `/home/ubuntu/outline/.env`
- **Custom launcher**: `outline-terminal` command available
- **Working directory**: All terminals open in `/home/ubuntu/outline` by default

### Lightweight Configuration
- **Minimal XFCE**: Only window manager (xfwm4), panel, and desktop
- **No auto-start apps**: Clean desktop on startup
- **Essential packages only**: Removed Firefox, ImageMagick, file managers, and XFCE plugins
- **Package count**: ~450 packages (down from 800+)
- **Core components**: VNC, PostgreSQL, Redis, Nginx, Node.js, XFCE terminal

### VNC Access
- **Web VNC**: http://localhost:6080/vnc.html
- **NoVNC**: http://localhost:6080/
- **Direct VNC**: localhost:5900 (for VNC clients)

### XFCE Desktop Components
- **Window Manager**: xfwm4 (window decorations, compositing)
- **Panel**: xfce4-panel (minimal taskbar)
- **Desktop**: xfdesktop (wallpaper and desktop)
- **Terminal**: xfce4-terminal (only when manually opened)

### Manual Application Launch
Right-click on desktop or use panel to launch:
- **Terminal**: `xfce4-terminal`
- **File Manager**: Not installed (use terminal)
- **Browser**: Not installed (use host browser for http://localhost:3000)

### Status and Troubleshooting

#### Check Container Status
```bash
# Check if everything is ready
docker exec outline-single outline-status

# Check specific services
docker exec outline-single ps aux | grep -E "(postgres|redis|nginx)"

# Check logs
docker logs outline-single
```

#### Troubleshooting VNC Black Screen
If VNC shows black screen:

1. **Check services**: `docker exec outline-single outline-status`
2. **Manual XFCE start**: `docker exec -u outline outline-single /usr/local/bin/start-xfce4-manual`
3. **Check X server**: `docker exec outline-single bash -c "DISPLAY=:1 xdpyinfo | head -5"`
4. **Restart container**: `docker restart outline-single`

### Key Files and Commands
- **Status check**: `/usr/local/bin/outline-status`
- **Environment**: `/home/ubuntu/outline/.env` (auto-created)
- **XFCE startup**: `/usr/local/bin/start-xfce4-manual`
- **PostgreSQL setup**: `/usr/local/bin/setup_postgres.sh`
- **Complete setup**: `/usr/local/bin/setup-outline-dev`
- **Dinit services**: `/etc/dinit.d/`

### Container Startup Process
1. **Dinit starts**: Initializes all services
2. **PostgreSQL**: Auto-initialized and configured
3. **Redis**: Started automatically
4. **VNC/XFCE**: Desktop environment ready
5. **Outline Setup**: Database and environment configured
6. **Ready**: All services running, ready for development

No manual setup required - everything is ready after `docker run`!

## Code Style Guidelines
- **TypeScript**: Strict mode enabled, use explicit types, avoid `any`
- **Imports**: External packages → `@shared/*` → `@server/*` → `~/` (app) → relative imports
- **Naming**: `camelCase` variables/functions, `PascalCase` components/classes, `UPPER_CASE` constants
- **React**: Functional components with hooks, TypeScript interfaces for props, no React import needed
- **Error handling**: Use `@typescript-eslint/no-floating-promises`, await all promises
- **Formatting**: Prettier with 80 char width, trailing commas, no console.log (use Logger)
- **Database**: Sequelize with TypeScript decorators, models in `server/models/`
- **Testing**: Jest with separate configs for server/app/shared, use `@faker-js/faker` for test data

## Container Development (Single Dockerfile)
- **Build**: `docker build -f Dockerfile.single -t outline-single .`
- **Run**: `docker run -d -p 6080:6080 -p 80:80 outline-single`
- **VNC Access**: http://localhost:6080/vnc.html (XFCE desktop with terminal)
- **Services**: dinit manages PostgreSQL, Redis, Outline, X11/VNC, Nginx in one container

## VNC Desktop Development Setup

### Fixed XFCE Desktop Environment
The container now includes a fully functional XFCE desktop accessible via VNC:
- **Window Manager**: xfwm4 with proper compositing
- **Panel**: xfce4-panel with system tray and controls
- **Desktop**: xfdesktop with file manager integration
- **Terminal**: xfce4-terminal for development work
- **Browser**: Firefox ESR for testing Outline

### VNC Access & Troubleshooting
- **Web VNC**: http://localhost:6080/vnc.html (noVNC web client)
- **Direct VNC**: localhost:5900 (for VNC clients)
- **XFCE Issues**: If desktop breaks, restart with `/usr/local/bin/start-xfce4-fixed`
- **Services**: Use `dinitctl list` to check service status

### Development Environment Setup
Use the automated setup script in the VNC terminal:
```bash
# Run the complete setup script
/tmp/setup-outline-dev.sh

# Load environment variables
source /tmp/outline-env.sh

# Start development server
cd /opt/outline
yarn dev:watch
```

### Manual Database Setup (if needed)
```bash
# Initialize PostgreSQL
sudo -u postgres /usr/lib/postgresql/15/bin/initdb -D /var/lib/postgresql/main

# Start PostgreSQL
sudo -u postgres /usr/lib/postgresql/15/bin/postgres -D /var/lib/postgresql/main &

# Create database and user
sudo -u postgres createdb outline
sudo -u postgres psql -c "CREATE USER outline WITH PASSWORD 'outline_password';"
sudo -u postgres psql -c "GRANT ALL PRIVILEGES ON DATABASE outline TO outline;"

# Set environment and migrate
export DATABASE_URL="postgres://outline:outline_password@localhost:5432/outline"
yarn db:migrate
```

### Architecture Improvements Made
1. **Replaced Fluxbox with XFCE**: Better user experience with proper desktop environment
2. **Fixed VNC Integration**: Proper dbus session management and X11 forwarding
3. **Automated Setup**: Single script handles PostgreSQL, Redis, and database initialization
4. **Clean Service Management**: dinit services properly configured with dependencies
5. **Development Ready**: Environment variables, database, and services auto-configured

### Development Workflow
1. Access VNC desktop at http://localhost:6080/vnc.html
2. Open terminal (xfce4-terminal)
3. Run setup script: `/tmp/setup-outline-dev.sh`
4. Start development: `yarn dev:watch`
5. Access Outline at http://localhost:3000 in Firefox
6. Edit code in `/opt/outline` with hot reloading enabled
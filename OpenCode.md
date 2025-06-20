# Outline Development Guide

## Build/Test Commands
- **Install**: `yarn install --frozen-lockfile`
- **Build**: `yarn build` (cleans, builds frontend with Vite, i18n, then server)
- **Dev**: `yarn dev:watch` (concurrent backend + frontend development)
- **Lint**: `yarn lint` (ESLint for app/server/shared/plugins)
- **Test all**: `yarn test`
- **Test single project**: `yarn test:server`, `yarn test:app`, `yarn test:shared`
- **Test single file**: `yarn test path/to/file.test.ts`
- **Database**: `yarn db:migrate`, `yarn db:create --env=production-ssl-disabled`, `yarn db:reset`

## Code Style Guidelines
- **TypeScript**: Strict mode enabled, use explicit types, avoid `any`
- **Imports**: External packages → `@shared/*` → `@server/*` → `~/` (app) → relative imports
- **Naming**: `camelCase` variables/functions, `PascalCase` components/classes, `UPPER_CASE` constants
- **React**: Functional components with hooks, TypeScript interfaces for props, no React import needed
- **Error handling**: Use `@typescript-eslint/no-floating-promises`, await all promises
- **Formatting**: Prettier with 80 char width, trailing commas, no console.log (use Logger)
- **Database**: Sequelize with TypeScript decorators, models in `server/models/`
- **Testing**: Jest with separate configs for server/app/shared, use `@faker-js/faker` for test data

## Production Container Setup

### Quick Start (Zero Configuration)
1. **Build container**: `docker build -f Dockerfile.single.minimal -t outline-production .`
2. **Run container**: `docker run -d --name outline -p 3000:3000 -p 6080:6080 outline-production`
3. **Access Outline**: http://localhost:3000 (production-ready instance)
4. **Access Desktop**: http://localhost:6080/vnc.html (for administration)

### Production Features
- ✅ **Zero Configuration**: Everything pre-configured and ready to use
- ✅ **Production Environment**: NODE_ENV=production, optimized settings
- ✅ **Auto-Generated Secrets**: Secure SECRET_KEY and UTILS_SECRET created automatically
- ✅ **Built Application**: `yarn build` completed during Docker build
- ✅ **Database Ready**: PostgreSQL initialized with `yarn db:create --env=production-ssl-disabled`
- ✅ **Email Authentication**: Local SMTP server for development/testing
- ✅ **File Storage**: Local file storage configured
- ✅ **Redis Cache**: Redis server configured and running
- ✅ **Desktop Environment**: XFCE desktop for administration via VNC

### Email Authentication Setup
The container includes a local SMTP server that captures login emails:

```bash
# Watch for login emails (shows login links in console)
watch-emails

# Fix Redis issues if they occur
fix-redis
```

**Login Process:**
1. Enter any email address in the login form
2. Check the application logs for the login link (SMTP server removed)
3. Copy and paste the login link in your browser
4. You're logged in!

## CLI Tools for Backup/Migration

### Simple Export/Import (Recommended)
```bash
# Export entire workspace to folder
outline export /tmp/my-backup

# Import workspace from folder
outline import /tmp/my-backup

# Force import (overwrite existing data)
outline import /tmp/my-backup --force
```

### Advanced Export/Import Options
```bash
# Export with advanced options (includes markdown files)
outline export-full -d /tmp/backup --format both --verbose

# Export without file attachments or markdown
outline export-full -d /tmp/backup --no-files --no-markdown

# Export clean markdown without metadata headers
outline export-full -d /tmp/backup --clean-markdown

# Import with advanced options  
outline import-full -d /tmp/backup --dry-run --verbose

# Export via API (requires API token)
outline api-export -t your-api-token -o /tmp/downloads
```

### Export Formats
- **JSON**: Structured data for importing into another Outline instance
- **SQL**: Complete PostgreSQL database dump
- **Files**: File attachments and uploads
- **Markdown (Standard)**: Individual markdown files with YAML frontmatter metadata
- **Markdown (Clean)**: Pure markdown content without metadata headers

### Export Contents
The `export-full` command now creates:
- `workspace.json` - Complete workspace data
- `files/` - All file attachments
- `markdown/` - All documents as `.md` files organized by collection
  - **Standard mode**: Includes YAML frontmatter with title, dates, collection, ID
  - **Clean mode** (`--clean-markdown`): Pure markdown content only
- `export_metadata.json` - Export metadata
- `README.md` - Export documentation

### Import Process
The import automatically:
1. **Runs database migrations** to ensure schema exists
2. **Creates backup** of existing data before import
3. **Imports JSON data** with proper error handling and array field support
4. **Copies file attachments** if present
5. **Fixes database consistency** issues after import
6. **Sets up user permissions** for imported collections

### Array Field Support
The import now properly handles PostgreSQL array fields:
- **UUID arrays** (like `collaboratorIds`) are converted with proper casting: `ARRAY['uuid1','uuid2']::uuid[]`
- **JSON arrays** are preserved as JSON strings for non-UUID fields
- **Automatic detection** based on field names ending in 'Id' or 'Ids'

### Use Cases
- **Automated Backups**: Schedule daily exports with cron
- **Migration**: Move between Outline instances
- **Development**: Export production data to development environment
- **Disaster Recovery**: Complete workspace restore

## Container Architecture

### Services (Managed by dinit)
- **PostgreSQL**: Database server with outline database pre-created
- **Redis**: Cache server with proper configuration (fixes MISCONF errors)
- **Outline**: Node.js application server (production build)
- **SMTP**: Local email server for authentication (captures login links)
- **Nginx**: Reverse proxy (optional)
- **XFCE**: Desktop environment accessible via VNC
- **VNC**: Remote desktop access on port 6080

### Database Configuration
- **Environment**: `production-ssl-disabled` (no SSL required for local PostgreSQL)
- **Initialization**: Uses `yarn db:create --env=production-ssl-disabled` instead of manual createdb
- **User**: `outline` with password `outline_password`
- **Database**: `outline` with full permissions

### File Structure
```
/home/ubuntu/outline/          # Outline application (built)
├── .env.production           # Production environment variables
├── build/                    # Built application
└── node_modules/            # Dependencies

/var/lib/outline/data/        # File uploads and attachments
/var/lib/postgresql/15/main/  # PostgreSQL data
/var/lib/redis/              # Redis data
/etc/redis/redis.conf        # Redis configuration
```

### Environment Variables (Auto-configured)
```bash
NODE_ENV=production
DATABASE_URL=postgres://outline:outline@localhost:5432/outline
REDIS_URL=redis://localhost:6379
SECRET_KEY=<auto-generated-32-byte-hex>
UTILS_SECRET=<auto-generated-32-byte-hex>
URL=http://localhost:3000
ENABLED_PLUGINS=email
SMTP_HOST=127.0.0.1
SMTP_PORT=1025
# ... and more
```

## Development Workflow

### VNC Desktop Access
- **Web VNC**: http://localhost:6080/vnc.html
- **Direct VNC**: localhost:5900 (for VNC clients)
- **Desktop**: Full XFCE environment with terminal access

### Development Commands (in VNC terminal)
```bash
cd /home/ubuntu/outline

# Start development server
yarn dev:watch

# Run tests
yarn test

# Database operations
yarn db:migrate
yarn db:reset

# Build application
yarn build
```

### Troubleshooting

#### Redis Issues
```bash
# Fix Redis configuration and permissions
fix-redis

# Check Redis status
redis-cli ping
```

#### Email Login Issues
```bash
# Watch for login emails
watch-emails
```

#### Database Issues
```bash
# Check database connection
psql $DATABASE_URL -c "SELECT 1;"

# Recreate database
yarn db:create --env=production-ssl-disabled
yarn db:migrate
```

#### Service Status
```bash
# Check all services
dinitctl list

# Restart specific service
dinitctl restart outline
```

## Key Improvements Made

### Database Setup
- **Standardized**: Uses `yarn db:create --env=production-ssl-disabled` for consistency
- **Production Environment**: All NODE_ENV settings changed to production
- **SSL Disabled**: Uses `production-ssl-disabled` environment for local PostgreSQL

### Redis Configuration
- **Fixed MISCONF Errors**: Proper redis.conf with `stop-writes-on-bgsave-error no`
- **Proper Permissions**: Redis user owns data and log directories
- **Persistent Storage**: Configured for proper data persistence

### Email Authentication
- **Local SMTP Server**: Captures emails and shows login links in console
- **No External Dependencies**: Works without real email service
- **Development Friendly**: Perfect for testing and development

### CLI Tools
- **Simple Interface**: `outline export/import <directory>` for basic operations
- **Advanced Options**: Full-featured bash scripts for complex scenarios
- **Multiple Formats**: JSON, SQL, Markdown, HTML export formats
- **Folder-based**: Organized export structure with metadata and documentation

### Production Ready
- **Zero Configuration**: Everything works out of the box
- **Auto-generated Secrets**: Secure random keys generated during build
- **Built Application**: Production build completed during Docker build
- **Optimized Settings**: Production environment variables and configurations

The container is now a complete, production-ready Outline instance that can be deployed anywhere with zero configuration required!
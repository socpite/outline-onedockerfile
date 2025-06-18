# Outline CLI Tools

Command-line tools for exporting and importing Outline workspaces without using the web interface.

## Overview

The Outline CLI provides three main commands:

1. **`export`** - Direct database export (fastest, requires database access)
2. **`api-export`** - Export via Outline's API (like the web UI, requires API token)
3. **`import`** - Import workspace data from exported folders

## Installation

The CLI tools are included in the Outline container. Make them available globally:

```bash
# Inside the container
ln -s /usr/local/bin/outline-cli /usr/local/bin/outline
```

## Quick Start

### Export Workspace (Database Method)
```bash
# Export everything to a folder
outline export -d /tmp/my-backup

# Export with verbose output
outline export -d /tmp/my-backup --verbose

# Export database only (skip files)
outline export -d /tmp/my-backup --no-files

# Export in SQL format
outline export -d /tmp/my-backup --format sql
```

### Export Workspace (API Method)
```bash
# Get API token first from Settings > API Keys in web UI
outline api-export -t your-api-token -o /tmp/downloads

# Export specific collection
outline api-export -t your-api-token -c collection-id -f markdown

# Export without waiting for completion
outline api-export -t your-api-token --no-wait
```

### Import Workspace
```bash
# Import from exported folder
outline import -d /tmp/my-backup

# Force import (overwrite existing data)
outline import -d /tmp/my-backup --force

# Dry run (see what would be imported)
outline import -d /tmp/my-backup --dry-run

# Import database only (skip files)
outline import -d /tmp/my-backup --skip-files
```

## Export Methods Comparison

| Feature | Database Export | API Export |
|---------|----------------|------------|
| **Speed** | Very Fast | Slower |
| **Requirements** | Database access | API token |
| **Formats** | JSON, SQL, Both | JSON, Markdown, HTML |
| **Scope** | Full workspace | Full workspace or collection |
| **Files** | Direct copy | Processed by Outline |
| **Use Case** | Server backups | User downloads |

## Export Formats

### Database Export Formats

- **JSON** - Structured data for importing into another Outline instance
- **SQL** - Complete PostgreSQL database dump
- **Both** - Creates both JSON and SQL files

### API Export Formats

- **JSON** - Structured data (same as database export)
- **Markdown** - ZIP file with Markdown documents and images
- **HTML** - ZIP file with HTML documents and images

## Export Folder Structure

When you export, you get a folder with this structure:

```
my-backup/
├── README.md                 # Documentation
├── export_metadata.json      # Export information
├── database.sql              # Database dump (if SQL format)
├── workspace.json            # Structured data (if JSON format)
└── files/                    # File attachments
    ├── uploads/
    ├── avatars/
    └── ...
```

## Environment Variables

### Required for Database Operations
```bash
DATABASE_URL=postgres://outline:password@localhost:5432/outline
```

### Optional
```bash
OUTLINE_API_URL=http://localhost:3000  # For API exports
```

## API Token Setup

To use `api-export`, you need an API token:

1. Go to **Settings → API Keys** in Outline web UI
2. Click **"New API Key"**
3. Copy the token
4. Use with `-t` option: `outline api-export -t your-token`

## Advanced Usage

### Automated Backups

Create a daily backup script:

```bash
#!/bin/bash
# daily-backup.sh

BACKUP_DIR="/backups/outline-$(date +%Y%m%d)"
outline export -d "$BACKUP_DIR" --format both

# Keep only last 7 days
find /backups -name "outline-*" -type d -mtime +7 -exec rm -rf {} \;
```

### Migration Between Instances

```bash
# On source instance
outline export -d /tmp/migration --format json

# Copy to target instance
scp -r /tmp/migration target-server:/tmp/

# On target instance
outline import -d /tmp/migration --force
```

### Selective Import

```bash
# Import only database (no files)
outline import -d /tmp/backup --skip-files

# Import only files (no database)
outline import -d /tmp/backup --skip-database
```

## Troubleshooting

### Common Issues

**"Cannot connect to database"**
```bash
# Check DATABASE_URL
echo $DATABASE_URL

# Test connection
psql $DATABASE_URL -c "SELECT 1;"
```

**"API token invalid"**
```bash
# Test API token
curl -H "Authorization: Bearer your-token" \
     http://localhost:3000/api/auth.info
```

**"Permission denied on files"**
```bash
# Fix file permissions
sudo chown -R ubuntu:ubuntu /var/lib/outline/data
```

### Verbose Mode

Add `-v` or `--verbose` to any command for detailed output:

```bash
outline export -d /tmp/backup --verbose
outline import -d /tmp/backup --verbose --dry-run
```

### Backup Verification

```bash
# Check export contents
outline export -d /tmp/test --dry-run

# Verify import without changes
outline import -d /tmp/test --dry-run
```

## Security Notes

- **Database exports contain sensitive data** - encrypt backups
- **API tokens have full access** - store securely
- **File exports include uploads** - may contain private files
- **SQL dumps include passwords** - handle carefully

## Performance Tips

- Use `--no-files` for faster database-only exports
- Use `--format sql` for fastest exports
- Run exports during low-usage periods
- Consider compression for large exports:

```bash
outline export -d /tmp/backup
tar czf backup.tar.gz -C /tmp backup/
```

## Integration Examples

### Docker Compose Backup

```yaml
version: '3'
services:
  outline-backup:
    image: outline-production
    volumes:
      - ./backups:/backups
    command: outline export -d /backups/$(date +%Y%m%d)
    environment:
      - DATABASE_URL=postgres://...
```

### Kubernetes CronJob

```yaml
apiVersion: batch/v1
kind: CronJob
metadata:
  name: outline-backup
spec:
  schedule: "0 2 * * *"  # Daily at 2 AM
  jobTemplate:
    spec:
      template:
        spec:
          containers:
          - name: backup
            image: outline-production
            command: ["outline", "export", "-d", "/backup"]
            volumeMounts:
            - name: backup-storage
              mountPath: /backup
```

## Support

For issues with the CLI tools:

1. Check the verbose output: `outline <command> --verbose`
2. Verify environment variables
3. Test database/API connectivity
4. Check file permissions

The CLI tools are designed to work alongside Outline's web interface, providing automation and backup capabilities for system administrators.
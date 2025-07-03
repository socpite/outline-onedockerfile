# Outline Import Scripts - Rewritten Version

## Overview

The Outline import scripts have been completely rewritten to address critical issues with foreign key handling, encoding problems, and syntax errors. This document explains the improvements and how to use the new scripts.

## Issues Fixed

### Original Problems
1. **Foreign Key Issues**: Poor handling of references, orphaned records deleted instead of fixed
2. **Encoding Problems**: Basic string escaping, no UTF-8 validation, JSON encoding failures
3. **Syntax Errors**: Mixed bash/Python causing escaping issues, inconsistent error handling
4. **No Transaction Support**: Database left inconsistent if import fails partway
5. **Inefficient Operations**: Individual INSERTs instead of batch operations
6. **Complex Structure**: Overly complex bash script with embedded Python
7. **Data Structure Mismatch**: Scripts expected nested data format but exports use flat structure

### Improvements Made
- ✅ **Proper Foreign Key Resolution**: Smart handling of missing references
- ✅ **UTF-8 Encoding Support**: Proper encoding validation and error handling
- ✅ **Separated Concerns**: Clean separation of bash orchestration and Python data processing
- ✅ **Batch Operations**: Efficient database operations with proper error handling
- ✅ **Transaction Safety**: Better error recovery and consistency
- ✅ **Comprehensive Logging**: Detailed progress reporting and error diagnostics
- ✅ **Data Structure Fix**: Correctly handles flat export format (teams, users at root level)
- ✅ **Default Collection Creation**: Automatically creates collections for orphaned documents
- ✅ **Content Generation**: Creates proper ProseMirror content structure from text

## Available Scripts

### Simple Import Scripts
- `outline-import-simple` - Original Node.js version (legacy)
- `outline-import-simple-v2.js` - **NEW** Improved Node.js version with better error handling

### Full-Featured Import Scripts  
- `outline-import` - Original bash version with embedded Python (legacy)
- `outline-import-v2` - **NEW** Clean bash version using separate Python script
- `outline-import-new.py` - **NEW** Robust Python script for database operations

### CLI Wrapper
- `outline-cli` - Updated to include new import options

## Usage

### Quick Start (Recommended)

Use the improved simple import for most cases:
```bash
# Import with the new improved simple script
outline-cli import-v2 /path/to/backup --force

# Or directly
./scripts/outline-import-simple-v2.js /path/to/backup --force --verbose
```

### Advanced Import (Full Features)

Use the new full-featured import for complex scenarios:
```bash
# Import with the new improved full script
outline-cli import-full-v2 -d /path/to/backup --force --verbose

# Or directly
./scripts/outline-import-v2 -d /path/to/backup --force --verbose --dry-run
```

### Python Script Directly

For maximum control, use the Python script directly:
```bash
python3 scripts/outline-import-new.py /path/to/backup/workspace.json "$DATABASE_URL" --force --verbose
```

## Command Options

### Simple Import (`outline-import-simple-v2.js`)
```
Usage: outline-import-simple-v2 <import-directory> [--force] [--verbose]

Options:
  --force      Overwrite existing data
  --verbose    Show detailed logging
```

### Full Import (`outline-import-v2`)
```
Usage: outline-import-v2 [OPTIONS]

Options:
  -d, --dir DIR         Import directory (required)
  -f, --force          Force import (overwrite existing data)
  --skip-files         Skip file attachments import
  --skip-database      Skip database import
  --dry-run            Show what would be imported without doing it
  --no-backup          Skip database backup
  -v, --verbose        Verbose output
  -h, --help           Show help
```

### Python Import (`outline-import-new.py`)
```
Usage: outline-import-new.py json_file database_url [OPTIONS]

Options:
  --force              Clear existing data before import
  --verbose            Show detailed logging
  --no-backup          Skip database backup
```

## Data Handling Improvements

### Foreign Key Resolution
- **Documents without collections**: Automatically assigned to first available collection
- **Orphaned records**: Cleaned up after import instead of causing failures
- **Missing references**: Smart handling with fallback strategies

### Encoding Fixes
- **UTF-8 Validation**: All text properly validated and sanitized
- **JSON Handling**: Proper encoding of complex data structures
- **Character Replacement**: Invalid characters safely replaced instead of causing failures

### Content Handling
- **Missing Document Content**: Generated from text field or created as empty
- **Array Fields**: Proper initialization of NULL arrays (collaboratorIds, membershipIds, etc.)
- **Timestamps**: Automatic generation of missing createdAt/updatedAt fields

## Error Handling

### Graceful Degradation
- Individual record failures don't stop the entire import
- Detailed logging of what succeeded and what failed
- Rollback capabilities where possible

### Validation
- Pre-import checks for data integrity
- Database connection validation
- Required dependency verification

### Recovery
- Automatic backup creation before destructive operations
- Detailed error messages with actionable suggestions
- Progress tracking for large imports

## Performance Improvements

### Batch Operations
- Efficient bulk inserts instead of individual queries
- Proper use of ON CONFLICT for upserts
- Reduced database round-trips

### Memory Management
- Streaming processing for large datasets
- Proper resource cleanup
- Connection pooling where applicable

## Migration from Old Scripts

### For Simple Imports
```bash
# Old way
./scripts/outline-import-simple /path/to/backup --force

# New way (recommended)
./scripts/outline-import-simple-v2.js /path/to/backup --force --verbose
```

### For Full Imports
```bash
# Old way
./scripts/outline-import -d /path/to/backup --force --verbose

# New way (recommended)  
./scripts/outline-import-v2 -d /path/to/backup --force --verbose
```

### Via CLI
```bash
# Old commands still work
outline-cli import /path/to/backup --force
outline-cli import-full -d /path/to/backup --force

# New improved commands
outline-cli import-v2 /path/to/backup --force
outline-cli import-full-v2 -d /path/to/backup --force
```

## Dependencies

### Required
- `python3` - For Python-based import processing
- `psql` - PostgreSQL client for database operations
- `psycopg2` - Python PostgreSQL adapter
- `node` - For Node.js based simple import
- `jq` - JSON processing (for metadata handling)

### Installation
```bash
# Python dependencies
pip3 install psycopg2-binary

# System dependencies (Ubuntu/Debian)
apt-get update
apt-get install -y postgresql-client jq python3-pip

# Or via package manager of choice
```

## Troubleshooting

### Common Issues

**"psycopg2 not found"**
```bash
pip3 install psycopg2-binary
```

**"Permission denied" errors**
```bash
chmod +x scripts/outline-import-v2
chmod +x scripts/outline-import-simple-v2.js  
chmod +x scripts/outline-import-new.py
```

**"Database connection failed"**
- Verify `DATABASE_URL` environment variable is set
- Check database is running and accessible
- Ensure credentials are correct

**"No valid records after fixing"**
- Check the source JSON file format
- Verify data structure matches expected schema
- Use `--verbose` flag for detailed debugging

### Getting Help

1. Use `--help` flag with any script for usage information
2. Use `--verbose` flag for detailed debugging output
3. Use `--dry-run` flag to see what would happen without making changes
4. Check the logs for specific error messages and suggestions

## Examples

### Basic Import
```bash
# Simple import with progress
outline-cli import-v2 /tmp/my-backup --force --verbose
```

### Advanced Import with Options
```bash
# Full import with dry run first
outline-cli import-full-v2 -d /tmp/my-backup --dry-run --verbose

# Then actual import
outline-cli import-full-v2 -d /tmp/my-backup --force --verbose
```

### Database Only (Skip Files)
```bash
outline-cli import-full-v2 -d /tmp/my-backup --skip-files --force
```

### Files Only (Skip Database)
```bash
outline-cli import-full-v2 -d /tmp/my-backup --skip-database --force
```

This rewritten import system provides a much more robust, reliable, and maintainable solution for importing Outline data. 
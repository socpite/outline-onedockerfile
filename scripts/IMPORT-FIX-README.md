# Outline Import Fix - Database Schema & Encoding Issues

## Problem Summary

The `outline-cli import-full-v2` command was failing with two critical issues:

1. **Missing Database Schema**: `relation "teams" does not exist`
2. **Character Encoding Problems**: `'ascii' codec can't encode character '\u2014'`

These issues caused the import to fail completely, resulting in 0 imported records despite appearing to complete successfully.

## Root Causes

### 1. Database Schema Not Initialized
- The database was missing the required tables (teams, users, collections, documents, etc.)
- Outline requires database migrations to be run first to create the schema
- The import script was trying to insert data into non-existent tables

### 2. UTF-8 Encoding Issues
- The Python script was not properly configured for UTF-8 encoding
- Unicode characters (em-dashes, emojis, special punctuation) caused encoding failures
- Database connection lacked proper encoding configuration

### 3. Transaction Handling Problems
- When one record failed, the entire transaction was aborted
- Subsequent operations failed with "current transaction is aborted" errors
- No proper rollback or error recovery mechanism

## Solutions Implemented

### 1. Fixed Database Schema Initialization
- **Updated `outline-import-new.py`** to automatically run database migrations
- Added `ensure_database_schema()` method that runs `yarn db:migrate`
- Created **`outline-import-migrate-db`** helper script for manual migration
- Added table existence checks and proper error handling

### 2. Fixed UTF-8 Encoding Issues
- Updated database connection with `client_encoding=UTF8` parameter
- Improved `sanitize_value()` method to handle UTF-8 strings properly
- Added proper Unicode character validation and cleaning
- Set `ensure_ascii=False` for JSON serialization

### 3. Improved Transaction Handling
- Added per-table transaction management with proper commit/rollback
- Individual record failures no longer abort the entire import
- Added success/failure counting and detailed error reporting
- Improved error messages with actionable guidance

### 4. Enhanced Error Messages and Guidance
- Updated error messages to explain common issues
- Added troubleshooting guidance in CLI help
- Created helper scripts for common fixes
- Improved logging with success rates and detailed statistics

## How to Fix Your Import

### Option 1: Automatic Fix (Recommended)
The updated import script will automatically handle database migrations:

```bash
# Run the import - it will handle migrations automatically
outline-cli import-full-v2 -d /path/to/your/backup --force --verbose
```

### Option 2: Manual Migration First
If you prefer to run migrations manually or the automatic approach fails:

```bash
# Step 1: Run database migrations
./scripts/outline-import-migrate-db

# Step 2: Run import with migration skip
python3 scripts/outline-import-new.py /path/to/workspace.json "$DATABASE_URL" --verbose --skip-migrations
```

### Option 3: Traditional Approach
Using the bash wrapper:

```bash
# Ensure database is migrated first
cd /home/ubuntu/outline && yarn db:migrate

# Then run import
outline-cli import-full-v2 -d /path/to/your/backup --force --verbose
```

## Files Modified

### Core Import Script
- **`scripts/outline-import-new.py`** - Fixed encoding, schema, and transaction issues
  - Added automatic database migration support
  - Fixed UTF-8 encoding throughout
  - Improved transaction handling and error recovery
  - Added detailed success/failure reporting

### Wrapper Scripts
- **`scripts/outline-import-v2`** - Enhanced error handling and guidance
- **`scripts/outline-cli`** - Added troubleshooting help

### New Helper Scripts
- **`scripts/outline-import-migrate-db`** - Database migration helper

## Verification

After applying these fixes, you should see:

1. **Successful migration messages**:
   ```
   🔧 Ensuring database schema exists...
   ✅ Database schema ready
   ```

2. **Successful record imports**:
   ```
   teams: importing 1 records...
   ✅ teams: completed (1/1 records)
   ```

3. **Proper final statistics**:
   ```
   👥 Teams: 1
   👤 Users: 2
   📚 Collections: 9
   📄 Documents: 44
   ```

4. **Success rate reporting**:
   ```
   🎉 Import completed! 67/75 records imported (89.3%)
   ```

## Common Issues and Solutions

### Issue: "Outline directory not found"
```bash
# Ensure you're running inside the Outline container
# or set the correct path in the script
```

### Issue: "yarn command not found"
```bash
# Install Node.js and Yarn in your environment
# or run the migration manually with Sequelize
```

### Issue: "Permission denied"
```bash
chmod +x scripts/outline-import-new.py
chmod +x scripts/outline-import-migrate-db
```

### Issue: Still getting encoding errors
```bash
# Check your system locale
export LANG=en_US.UTF-8
export LC_ALL=en_US.UTF-8
```

## Testing the Fix

To verify the fix works:

```bash
# Test migration
./scripts/outline-import-migrate-db

# Test import with a small dataset
outline-cli import-full-v2 -d /path/to/backup --dry-run --verbose

# Run actual import
outline-cli import-full-v2 -d /path/to/backup --force --verbose
```

## Additional Notes

- The fix maintains backward compatibility with existing scripts
- UTF-8 support now handles emojis, special characters, and international text
- Transaction handling is more robust with individual record error recovery
- Detailed logging helps troubleshoot any remaining issues
- Success rates help identify data quality issues in source exports

Your import should now complete successfully with proper data in the database! 
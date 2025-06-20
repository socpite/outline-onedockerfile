# Outline Export

This directory contains a complete export of an Outline workspace.

## Export Details

- **Exported At**: 2025-06-19 03:39:51 UTC
- **Format**: json
- **Include Files**: true

## Contents

- `workspace.json` - Structured workspace data
- `files/` - File attachments and uploads
- `export_metadata.json` - Export metadata and settings
- `README.md` - This file

## Import

To import this data into another Outline instance, use:

```bash
outline-import -d test-fixed
```

## Manual Import

### Database (SQL)
```bash
psql $DATABASE_URL < database.sql
```

### Files
```bash
cp -r files/* /var/lib/outline/data/
```

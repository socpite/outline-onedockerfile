# Outline Export

This directory contains a complete export of an Outline workspace.

## Export Details

- **Exported At**: 2025-06-20 16:36:10 UTC
- **Format**: json
- **Include Files**: true
- **Include Markdown**: true

## Contents

- `workspace.json` - Structured workspace data
- `files/` - File attachments and uploads
- `markdown/` - All documents exported as markdown files
- `export_metadata.json` - Export metadata and settings
- `README.md` - This file

## Import

To import this data into another Outline instance, use:

```bash
outline-import -d data
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

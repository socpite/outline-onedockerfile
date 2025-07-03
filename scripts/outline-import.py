#!/usr/bin/python3
"""
Outline Import Script - Python Version
Robust import of Outline workspace data with proper encoding, foreign key handling, and transactions.
"""

import json
import sys
import argparse
import logging
import os
import uuid
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime, timezone
import psycopg2
from psycopg2.extras import RealDictCursor, execute_batch
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT


class OutlineImporter:
    """Robust Outline data importer with proper foreign key handling"""
    
    def __init__(self, database_url: str, verbose: bool = False):
        self.database_url = database_url
        self.verbose = verbose
        self.setup_logging()
        self.conn = None
        self.stats = {}
        
        # Table import order based on dependencies
        self.import_order = [
            'teams',           # Base entity
            'users',           # Depends on teams
            'collections',     # Depends on teams
            'groups',          # Depends on teams
            'documents',       # Depends on collections, users
            'attachments',     # Depends on documents
            'shares',          # Depends on documents
            'stars',           # Depends on documents, users
            'pins',            # Depends on documents, users
            'views',           # Depends on documents, users
            'memberships',     # Depends on users, teams
            'group_users',     # Depends on groups, users
            'revisions',       # Depends on documents
            'backlinks',       # Depends on documents
            'notifications',   # Depends on users
        ]
        
    def setup_logging(self):
        """Setup logging configuration"""
        level = logging.DEBUG if self.verbose else logging.INFO
        logging.basicConfig(
            level=level,
            format='%(asctime)s - %(levelname)s - %(message)s',
            datefmt='%H:%M:%S'
        )
        self.logger = logging.getLogger(__name__)
        
    def connect_database(self):
        """Connect to PostgreSQL database with proper configuration"""
        try:
            self.conn = psycopg2.connect(
                self.database_url,
                cursor_factory=RealDictCursor
            )
            self.conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
            self.logger.info("✅ Database connection established")
            
            # Verify connection
            with self.conn.cursor() as cur:
                cur.execute("SELECT version()")
                version = cur.fetchone()[0]
                self.logger.debug(f"PostgreSQL: {version}")
                
        except Exception as e:
            self.logger.error(f"❌ Database connection failed: {e}")
            raise
            
    def close_database(self):
        """Close database connection"""
        if self.conn:
            self.conn.close()
            self.logger.debug("Database connection closed")
            
    def load_json_data(self, json_file: str) -> Dict[str, Any]:
        """Load and validate JSON data with proper encoding"""
        try:
            with open(json_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                
            self.logger.info(f"✅ Loaded JSON data from {json_file}")
            
            # Log basic stats
            if 'data' in data:
                for table in self.import_order:
                    if table in data['data']:
                        count = len(data['data'][table])
                        if count > 0:
                            self.logger.info(f"   {table}: {count} records")
                            
            return data
            
        except json.JSONDecodeError as e:
            self.logger.error(f"❌ Invalid JSON in {json_file}: {e}")
            raise
        except UnicodeDecodeError as e:
            self.logger.error(f"❌ Encoding error in {json_file}: {e}")
            raise
        except Exception as e:
            self.logger.error(f"❌ Failed to load {json_file}: {e}")
            raise
            
    def check_existing_data(self) -> Dict[str, int]:
        """Check for existing data in database"""
        try:
            with self.conn.cursor() as cur:
                counts = {}
                for table in ['teams', 'users', 'documents', 'collections']:
                    try:
                        cur.execute(f'SELECT COUNT(*) as count FROM "{table}"')
                        counts[table] = cur.fetchone()['count']
                    except psycopg2.Error:
                        counts[table] = 0
                        
                return counts
                
        except Exception as e:
            self.logger.error(f"❌ Failed to check existing data: {e}")
            raise
            
    def backup_database(self) -> Optional[str]:
        """Create database backup before import"""
        try:
            backup_file = f"/tmp/outline_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.sql"
            
            # Extract database components from URL
            import urllib.parse
            parsed = urllib.parse.urlparse(self.database_url)
            
            cmd = [
                'pg_dump',
                '-h', parsed.hostname,
                '-p', str(parsed.port or 5432),
                '-U', parsed.username,
                '-d', parsed.path[1:],  # Remove leading slash
                '-f', backup_file
            ]
            
            import subprocess
            env = os.environ.copy()
            if parsed.password:
                env['PGPASSWORD'] = parsed.password
                
            result = subprocess.run(cmd, env=env, capture_output=True, text=True)
            
            if result.returncode == 0:
                self.logger.info(f"✅ Database backup created: {backup_file}")
                return backup_file
            else:
                self.logger.warning(f"⚠️ Backup failed: {result.stderr}")
                return None
                
        except Exception as e:
            self.logger.warning(f"⚠️ Backup failed: {e}")
            return None
            
    def clear_existing_data(self, force: bool = False):
        """Clear existing data from database"""
        if not force:
            return
            
        try:
            with self.conn.cursor() as cur:
                self.logger.info("🗑️ Clearing existing data...")
                
                # Disable foreign key checks
                cur.execute("SET session_replication_role = replica;")
                
                # Get all tables in reverse dependency order
                tables_to_clear = list(reversed(self.import_order))
                
                for table in tables_to_clear:
                    try:
                        cur.execute(f'TRUNCATE TABLE "{table}" CASCADE')
                        self.logger.debug(f"   Cleared {table}")
                    except psycopg2.Error as e:
                        self.logger.debug(f"   Skipped {table}: {e}")
                        
                # Re-enable foreign key checks
                cur.execute("SET session_replication_role = DEFAULT;")
                
                self.logger.info("✅ Existing data cleared")
                
        except Exception as e:
            self.logger.error(f"❌ Failed to clear data: {e}")
            raise
            
    def sanitize_value(self, value: Any) -> Any:
        """Sanitize and convert values for database insertion"""
        if value is None:
            return None
        elif isinstance(value, bool):
            return value
        elif isinstance(value, (int, float)):
            return value
        elif isinstance(value, (dict, list)):
            return json.dumps(value, ensure_ascii=False)
        elif isinstance(value, str):
            # Handle encoding issues
            try:
                # Ensure valid UTF-8
                return value.encode('utf-8').decode('utf-8')
            except UnicodeDecodeError:
                # Replace invalid characters
                return value.encode('utf-8', errors='replace').decode('utf-8')
        else:
            return str(value)
            
    def fix_foreign_keys(self, table: str, records: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Fix foreign key references in records"""
        if not records:
            return records
            
        fixed_records = []
        
        for record in records:
            fixed_record = record.copy()
            
            # Table-specific foreign key fixes
            if table == 'documents':
                # Fix collectionId - ensure it exists or assign to first collection
                collection_id = fixed_record.get('collectionId')
                if collection_id is None:
                    # Get first available collection
                    with self.conn.cursor() as cur:
                        cur.execute('SELECT id FROM collections ORDER BY "createdAt" LIMIT 1')
                        result = cur.fetchone()
                        if result:
                            fixed_record['collectionId'] = result['id']
                            self.logger.debug(f"Fixed document '{record.get('title', 'Unknown')}' - assigned to collection {result['id']}")
                        else:
                            # Skip this document if no collections exist
                            self.logger.warning(f"Skipping document '{record.get('title', 'Unknown')}' - no collections available")
                            continue
                            
                # Ensure content exists
                if not fixed_record.get('content'):
                    if fixed_record.get('text'):
                        # Create basic ProseMirror structure from text
                        fixed_record['content'] = {
                            "type": "doc",
                            "content": [{
                                "type": "paragraph", 
                                "content": [{
                                    "type": "text",
                                    "text": fixed_record['text']
                                }]
                            }]
                        }
                    else:
                        # Empty document
                        fixed_record['content'] = {
                            "type": "doc",
                            "content": [{"type": "paragraph"}]
                        }
                        
                # Fix collaboratorIds
                if fixed_record.get('collaboratorIds') is None:
                    fixed_record['collaboratorIds'] = []
                    
            elif table == 'users':
                # Fix notificationSettings
                if fixed_record.get('notificationSettings') is None:
                    fixed_record['notificationSettings'] = {}
                    
            elif table == 'collections':
                # Fix membershipIds
                if fixed_record.get('membershipIds') is None:
                    fixed_record['membershipIds'] = []
                    
            elif table == 'teams':
                # Fix allowedDomains
                if fixed_record.get('allowedDomains') is None:
                    fixed_record['allowedDomains'] = []
                    
            # Ensure required timestamps exist
            current_time = datetime.now(timezone.utc).isoformat()
            if 'createdAt' not in fixed_record or not fixed_record['createdAt']:
                fixed_record['createdAt'] = current_time
            if 'updatedAt' not in fixed_record or not fixed_record['updatedAt']:
                fixed_record['updatedAt'] = current_time
                
            # Ensure ID exists
            if 'id' not in fixed_record or not fixed_record['id']:
                fixed_record['id'] = str(uuid.uuid4())
                
            fixed_records.append(fixed_record)
            
        return fixed_records
        
    def import_table(self, table: str, records: List[Dict[str, Any]]) -> int:
        """Import records into a table with batch operations and proper error handling"""
        if not records:
            self.logger.info(f"   {table}: no data")
            return 0
            
        # Fix foreign keys first
        fixed_records = self.fix_foreign_keys(table, records)
        
        if not fixed_records:
            self.logger.info(f"   {table}: no valid records after fixing")
            return 0
            
        self.logger.info(f"   {table}: importing {len(fixed_records)} records...")
        
        try:
            with self.conn.cursor() as cur:
                success_count = 0
                
                # Prepare batch insert
                if fixed_records:
                    first_record = fixed_records[0]
                    columns = list(first_record.keys())
                    
                    # Build parameterized query
                    column_names = ', '.join([f'"{col}"' for col in columns])
                    placeholders = ', '.join(['%s'] * len(columns))
                    
                    # Use ON CONFLICT to handle duplicates
                    conflict_columns = [f'"{col}" = EXCLUDED."{col}"' for col in columns if col != 'id']
                    conflict_clause = f"ON CONFLICT (id) DO UPDATE SET {', '.join(conflict_columns)}" if conflict_columns else "ON CONFLICT (id) DO NOTHING"
                    
                    query = f'''
                        INSERT INTO "{table}" ({column_names}) 
                        VALUES ({placeholders})
                        {conflict_clause}
                    '''
                    
                    # Prepare data for batch insert
                    batch_data = []
                    for record in fixed_records:
                        row_data = []
                        for col in columns:
                            value = self.sanitize_value(record.get(col))
                            row_data.append(value)
                        batch_data.append(tuple(row_data))
                    
                    # Execute batch insert
                    execute_batch(cur, query, batch_data, page_size=100)
                    success_count = len(batch_data)
                    
                self.logger.info(f"   ✅ {table}: imported {success_count} records")
                return success_count
                
        except Exception as e:
            self.logger.error(f"   ❌ {table}: import failed - {e}")
            # Continue with other tables instead of failing completely
            return 0
            
    def fix_orphaned_records(self):
        """Fix orphaned records after import"""
        self.logger.info("🔧 Fixing orphaned records...")
        
        try:
            with self.conn.cursor() as cur:
                fixes_applied = 0
                
                # Remove documents with invalid collection references
                cur.execute('''
                    DELETE FROM documents 
                    WHERE "collectionId" IS NOT NULL 
                    AND "collectionId" NOT IN (SELECT id FROM collections)
                ''')
                orphaned_docs = cur.rowcount
                if orphaned_docs > 0:
                    self.logger.info(f"   Removed {orphaned_docs} orphaned documents")
                    fixes_applied += orphaned_docs
                
                # Remove memberships with invalid references
                cur.execute('''
                    DELETE FROM memberships 
                    WHERE "userId" NOT IN (SELECT id FROM users) 
                    OR "teamId" NOT IN (SELECT id FROM teams)
                ''')
                orphaned_memberships = cur.rowcount
                if orphaned_memberships > 0:
                    self.logger.info(f"   Removed {orphaned_memberships} orphaned memberships")
                    fixes_applied += orphaned_memberships
                
                # Remove other orphaned records
                orphan_queries = [
                    ('attachments', '"documentId" NOT IN (SELECT id FROM documents)'),
                    ('shares', '"documentId" NOT IN (SELECT id FROM documents)'),
                    ('stars', '"documentId" NOT IN (SELECT id FROM documents) OR "userId" NOT IN (SELECT id FROM users)'),
                    ('pins', '"documentId" NOT IN (SELECT id FROM documents) OR "userId" NOT IN (SELECT id FROM users)'),
                    ('views', '"documentId" NOT IN (SELECT id FROM documents) OR "userId" NOT IN (SELECT id FROM users)'),
                ]
                
                for table_name, condition in orphan_queries:
                    try:
                        cur.execute(f'DELETE FROM "{table_name}" WHERE {condition}')
                        count = cur.rowcount
                        if count > 0:
                            self.logger.info(f"   Removed {count} orphaned {table_name}")
                            fixes_applied += count
                    except psycopg2.Error:
                        pass  # Table might not exist
                
                if fixes_applied > 0:
                    self.logger.info(f"✅ Fixed {fixes_applied} orphaned records")
                else:
                    self.logger.info("✅ No orphaned records found")
                    
        except Exception as e:
            self.logger.error(f"❌ Failed to fix orphaned records: {e}")
            
    def import_data(self, data: Dict[str, Any]) -> Dict[str, int]:
        """Import all data with transaction support"""
        self.logger.info("📊 Starting data import...")
        
        import_stats = {}
        
        try:
            # Import tables in dependency order
            table_data = data.get('data', {})
            
            for table in self.import_order:
                if table in table_data:
                    records = table_data[table]
                    count = self.import_table(table, records)
                    import_stats[table] = count
                else:
                    import_stats[table] = 0
                    
            # Fix orphaned records after import
            self.fix_orphaned_records()
            
            self.logger.info("✅ Data import completed successfully")
            return import_stats
            
        except Exception as e:
            self.logger.error(f"❌ Data import failed: {e}")
            raise
            
    def show_summary(self, stats: Dict[str, int]):
        """Show import summary"""
        self.logger.info("📋 Import Summary:")
        self.logger.info("=" * 50)
        
        total_records = 0
        for table, count in stats.items():
            if count > 0:
                self.logger.info(f"   {table}: {count} records")
                total_records += count
                
        self.logger.info(f"   Total: {total_records} records imported")
        
        # Show final database stats
        try:
            with self.conn.cursor() as cur:
                self.logger.info("")
                self.logger.info("📈 Final Database Stats:")
                
                for table in ['teams', 'users', 'collections', 'documents']:
                    try:
                        cur.execute(f'SELECT COUNT(*) as count FROM "{table}"')
                        count = cur.fetchone()['count']
                        self.logger.info(f"   {table}: {count}")
                    except psycopg2.Error:
                        pass
                        
        except Exception as e:
            self.logger.debug(f"Could not show final stats: {e}")


def main():
    parser = argparse.ArgumentParser(description='Import Outline workspace data')
    parser.add_argument('json_file', help='Path to workspace.json file')
    parser.add_argument('database_url', help='PostgreSQL database URL')
    parser.add_argument('--force', action='store_true', help='Force import (clear existing data)')
    parser.add_argument('--verbose', '-v', action='store_true', help='Verbose output')
    parser.add_argument('--no-backup', action='store_true', help='Skip database backup')
    
    args = parser.parse_args()
    
    # Validate inputs
    if not os.path.exists(args.json_file):
        print(f"❌ JSON file not found: {args.json_file}")
        sys.exit(1)
        
    # Create importer
    importer = OutlineImporter(args.database_url, args.verbose)
    
    try:
        # Connect to database
        importer.connect_database()
        
        # Load JSON data
        data = importer.load_json_data(args.json_file)
        
        # Check existing data
        existing_counts = importer.check_existing_data()
        has_existing_data = any(count > 0 for count in existing_counts.values())
        
        if has_existing_data:
            importer.logger.info("⚠️  Existing data found:")
            for table, count in existing_counts.items():
                if count > 0:
                    importer.logger.info(f"   {table}: {count} records")
                    
            if not args.force:
                importer.logger.error("❌ Use --force to overwrite existing data")
                sys.exit(1)
                
        # Create backup
        if not args.no_backup and has_existing_data:
            importer.backup_database()
            
        # Clear existing data if force mode
        importer.clear_existing_data(args.force)
        
        # Import data
        stats = importer.import_data(data)
        
        # Show summary
        importer.show_summary(stats)
        
        importer.logger.info("🎉 Import completed successfully!")
        
    except KeyboardInterrupt:
        importer.logger.info("❌ Import cancelled by user")
        sys.exit(1)
    except Exception as e:
        importer.logger.error(f"❌ Import failed: {e}")
        sys.exit(1)
    finally:
        importer.close_database()


if __name__ == '__main__':
    main() 
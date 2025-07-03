#!/usr/bin/python3
"""
Outline Import Script - Fixed Version
Handles database schema creation, proper UTF-8 encoding, and transaction management
"""

import json
import sys
import argparse
import logging
import os
import uuid
import psycopg2
from psycopg2.extras import RealDictCursor, execute_batch
from datetime import datetime, timezone
from typing import Dict, List, Any, Optional
import subprocess


def log_python_info():
    """Log information about the Python executable being used"""
    print(f"🐍 Python executable: {sys.executable}")
    print(f"🐍 Python version: {sys.version}")
    print(f"🐍 Python path: {sys.path[0] if sys.path else 'Unknown'}")
    
    # Check if we're using system Python
    if sys.executable.startswith('/usr/bin/python'):
        print("✅ Using system Python")
    else:
        print(f"⚠️  Using non-system Python: {sys.executable}")


class OutlineImporter:
    def __init__(self, database_url: str, verbose: bool = False):
        self.database_url = database_url
        self.verbose = verbose
        self.setup_logging()
        self.conn = None
        
        # Import order based on dependencies
        self.import_order = [
            'teams', 'users', 'collections', 'groups', 'documents',
            'attachments', 'shares', 'stars', 'pins', 'views', 
            'memberships', 'group_users'
        ]
        
    def setup_logging(self):
        level = logging.DEBUG if self.verbose else logging.INFO
        logging.basicConfig(
            level=level,
            format='%(asctime)s - %(levelname)s - %(message)s',
            datefmt='%H:%M:%S'
        )
        self.logger = logging.getLogger(__name__)
        
    def ensure_database_schema(self):
        """Ensure database schema exists by running migrations"""
        self.logger.info("🔧 Ensuring database schema exists...")
        
        # Change to outline directory and run migrations
        outline_dir = "/home/ubuntu/outline"
        if not os.path.exists(outline_dir):
            self.logger.error(f"❌ Outline directory not found: {outline_dir}")
            raise Exception(f"Outline directory not found: {outline_dir}")
            
        # First, check if schema already exists
        if self.check_tables_exist():
            self.logger.info("✅ Database schema already exists")
            return
            
        self.logger.info("🔄 Database schema missing, running migrations...")
        
        try:
            # Set environment and run migration
            env = os.environ.copy()
            env['DATABASE_URL'] = self.database_url
            
            # Start with SSL-disabled migration as default (since server doesn't have SSL)
            self.logger.info("Running database migration...")
            result = subprocess.run(
                ['yarn', 'db:migrate', '--env=production-ssl-disabled'],
                cwd=outline_dir,
                env=env,
                capture_output=True,
                text=True,
                timeout=300  # 5 minute timeout
            )
            
            if result.returncode == 0:
                self.logger.info("✅ Database migration completed successfully")
                return
            else:
                error_output = result.stderr
                self.logger.warning(f"⚠️  Standard migration failed: {error_output}")
                
                # Try alternative migration approaches
                self.logger.info("🔄 Trying alternative migration methods...")
                
                # Try using sequelize directly
                result_sequelize = subprocess.run(
                    ['npx', 'sequelize-cli', 'db:migrate', '--env=production-ssl-disabled'],
                    cwd=outline_dir,
                    env=env,
                    capture_output=True,
                    text=True,
                    timeout=300
                )
                
                if result_sequelize.returncode == 0:
                    self.logger.info("✅ Migration completed using sequelize-cli directly")
                    return
                else:
                    self.logger.warning(f"⚠️  Direct sequelize migration failed: {result_sequelize.stderr}")
                
                # Final check - maybe migrations ran but failed to report success
                if self.check_tables_exist():
                    self.logger.info("✅ Database tables exist (migration may have partially succeeded)")
                    return
                else:
                    # Last resort: try to create basic schema manually
                    self.logger.info("🔄 Attempting manual schema creation...")
                    if self.create_basic_schema():
                        self.logger.info("✅ Basic schema created manually")
                        return
                    else:
                        raise Exception(f"All migration attempts failed. Last error: {error_output}")
                    
        except subprocess.TimeoutExpired:
            self.logger.error("❌ Database migration timed out")
            # Check if tables exist anyway (migration might have succeeded but not reported)
            if self.check_tables_exist():
                self.logger.info("✅ Database tables exist (migration completed despite timeout)")
                return
            else:
                raise Exception("Database migration timed out and tables don't exist")
        except Exception as e:
            self.logger.error(f"❌ Migration error: {e}")
            # Try to check if tables exist anyway
            if not self.check_tables_exist():
                # Last resort: manual schema creation
                if self.create_basic_schema():
                    self.logger.info("✅ Basic schema created manually after migration failure")
                    return
                else:
                    raise Exception(f"Database schema not ready: {e}")
            else:
                self.logger.info("✅ Database tables exist (migration may have run previously)")
                
    def check_tables_exist(self) -> bool:
        """Check if required database tables exist"""
        try:
            with self.conn.cursor() as cur:
                cur.execute('''
                    SELECT COUNT(*) FROM information_schema.tables 
                    WHERE table_name IN ('teams', 'users', 'collections', 'documents')
                ''')
                count = cur.fetchone()[0]
                return count >= 4
        except Exception:
            return False
        
    def connect_database(self):
        try:
            # Connect with proper UTF-8 encoding
            self.conn = psycopg2.connect(
                self.database_url,
                cursor_factory=RealDictCursor,
                options='-c client_encoding=UTF8'
            )
            # Set autocommit to False for proper transaction handling
            self.conn.autocommit = False  
            self.logger.info("✅ Database connected")
        except Exception as e:
            self.logger.error(f"❌ Database connection failed: {e}")
            raise
            
    def load_json_data(self, json_file: str) -> Dict[str, Any]:
        try:
            with open(json_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            self.logger.info(f"✅ Loaded JSON data from {json_file}")
            return data
        except Exception as e:
            self.logger.error(f"❌ Failed to load JSON: {e}")
            raise
            
    def sanitize_value(self, value: Any) -> Any:
        """Properly sanitize values for database insertion with UTF-8 support"""
        if value is None:
            return None
        elif isinstance(value, bool):
            return value
        elif isinstance(value, (int, float)):
            return value
        elif isinstance(value, list):
            # Handle PostgreSQL arrays properly
            if all(isinstance(item, str) for item in value):
                # Check if this looks like a UUID array (for collaboratorIds, etc.)
                if value and len(value) > 0 and len(value[0]) == 36 and '-' in value[0]:
                    # This looks like UUIDs, return as-is for psycopg2 UUID array handling
                    return value
                else:
                    # Regular string array
                    return value
            else:
                # For mixed or complex arrays, serialize as JSON
                return json.dumps(value, ensure_ascii=False)
        elif isinstance(value, dict):
            # Ensure JSON is properly encoded as UTF-8
            return json.dumps(value, ensure_ascii=False)
        elif isinstance(value, str):
            # Ensure string is properly encoded as UTF-8
            try:
                # Test if string is valid UTF-8
                value.encode('utf-8')
                return value
            except UnicodeDecodeError:
                # If not valid UTF-8, clean it up
                return value.encode('utf-8', errors='replace').decode('utf-8')
        else:
            return str(value)
            
    def create_default_collection(self, team_id: str) -> str:
        """Create a default collection for orphaned documents"""
        collection_id = str(uuid.uuid4())
        current_time = datetime.now(timezone.utc).isoformat()
        
        default_collection = {
            'id': collection_id,
            'name': 'Imported Documents',
            'description': 'Default collection for imported documents without collections',
            'teamId': team_id,
            'createdAt': current_time,
            'updatedAt': current_time,
            'deletedAt': None,
            'sharing': True,
            'sort': {"field": "title", "direction": "asc"},
            'permission': None,
            'maintainerApprovalRequired': False,
            'documentStructure': None,
            'importId': None
        }
        
        try:
            with self.conn.cursor() as cur:
                columns = list(default_collection.keys())
                values = [self.sanitize_value(default_collection[col]) for col in columns]
                
                column_names = ', '.join([f'"{col}"' for col in columns])
                placeholders = ', '.join(['%s'] * len(columns))
                
                query = f'INSERT INTO "collections" ({column_names}) VALUES ({placeholders})'
                cur.execute(query, values)
                self.conn.commit()  # Commit this transaction
                
                self.logger.info(f"   Created default collection: {collection_id}")
                return collection_id
                
        except Exception as e:
            self.logger.error(f"   Failed to create default collection: {e}")
            self.conn.rollback()
            return None

    def import_table(self, table: str, records: List[Dict[str, Any]]) -> int:
        if not records:
            self.logger.info(f"   {table}: no data")
            return 0
            
        self.logger.info(f"   {table}: importing {len(records)} records...")
        success_count = 0
        
        for record in records:
            try:
                # Start a new transaction for each record
                with self.conn.cursor() as cur:
                    # Resolve foreign key constraints
                    record = self.resolve_foreign_keys(table, record)
                    
                    # Fix common issues
                    if table == 'documents':
                        # Handle missing collections for documents
                        if record.get('collectionId') is None:
                            # Check if we have any collections in the database
                            cur.execute('SELECT id FROM collections LIMIT 1')
                            existing_collection = cur.fetchone()
                            
                            if existing_collection:
                                record['collectionId'] = existing_collection['id']
                                self.logger.debug(f"Assigned document to existing collection: {existing_collection['id']}")
                            else:
                                # Create default collection using team from the document
                                team_id = record.get('teamId')
                                if team_id:
                                    default_collection_id = self.create_default_collection(team_id)
                                    if default_collection_id:
                                        record['collectionId'] = default_collection_id
                                        self.logger.debug(f"Assigned document to new default collection: {default_collection_id}")
                                    else:
                                        self.logger.warning(f"Skipping document '{record.get('title', 'Unknown')}' - no valid collection")
                                        continue
                                else:
                                    self.logger.warning(f"Skipping document '{record.get('title', 'Unknown')}' - no team ID")
                                    continue
                        
                        # Fix content
                        if not record.get('content'):
                            if record.get('text'):
                                record['content'] = {
                                    "type": "doc",
                                    "content": [{
                                        "type": "paragraph",
                                        "content": [{"type": "text", "text": record['text']}]
                                    }]
                                }
                            else:
                                record['content'] = {
                                    "type": "doc",
                                    "content": [{"type": "paragraph"}]
                                }
                        
                        # Fix collaboratorIds - ensure it's a proper array
                        if record.get('collaboratorIds') is None:
                            record['collaboratorIds'] = []
                        elif isinstance(record['collaboratorIds'], str):
                            # Handle string representation of arrays
                            try:
                                if record['collaboratorIds'].startswith('[') and record['collaboratorIds'].endswith(']'):
                                    import ast
                                    record['collaboratorIds'] = ast.literal_eval(record['collaboratorIds'])
                                else:
                                    record['collaboratorIds'] = []
                            except:
                                record['collaboratorIds'] = []
                                
                    # Ensure timestamps
                    current_time = datetime.now(timezone.utc).isoformat()
                    if not record.get('createdAt'):
                        record['createdAt'] = current_time
                    if not record.get('updatedAt'):
                        record['updatedAt'] = current_time
                        
                    # Build insert query
                    columns = list(record.keys())
                    values = [self.sanitize_value(record[col]) for col in columns]
                    
                    # Build placeholders with proper casting for UUID arrays
                    placeholders = []
                    for i, col in enumerate(columns):
                        if col in ['collaboratorIds'] and isinstance(record[col], list):
                            # Cast array to UUID array
                            placeholders.append('%s::uuid[]')
                        else:
                            placeholders.append('%s')
                    
                    column_names = ', '.join([f'"{col}"' for col in columns])
                    placeholders_str = ', '.join(placeholders)
                    
                    # Build UPDATE clause with proper casting
                    update_clauses = []
                    for col in columns:
                        if col != 'id':
                            if col in ['collaboratorIds']:
                                update_clauses.append(f'"{col}" = EXCLUDED."{col}"::uuid[]')
                            else:
                                update_clauses.append(f'"{col}" = EXCLUDED."{col}"')
                    
                    query = f'''
                        INSERT INTO "{table}" ({column_names}) 
                        VALUES ({placeholders_str})
                        ON CONFLICT (id) DO UPDATE SET
                        {', '.join(update_clauses)}
                    '''
                    
                    cur.execute(query, values)
                    # Commit this single record
                    self.conn.commit()
                    success_count += 1
                    
            except Exception as e:
                self.logger.warning(f"Failed to insert record in {table}: {e}")
                # Rollback this record and continue with next
                self.conn.rollback()
                continue
                
        self.logger.info(f"   ✅ {table}: completed ({success_count}/{len(records)} records)")
        return success_count
            
    def show_summary(self, data: Dict[str, Any]):
        """Show import summary in consistent format"""
        print("\n📊 Import Summary")
        print("==================")
        
        # Show export metadata if available
        export_date = data.get('exportedAt', 'Unknown')
        export_version = data.get('version', 'Unknown')
        print(f"📅 Export Date: {export_date}")
        print(f"🏷️  Export Version: {export_version}")
        
        # Show final database stats
        try:
            with self.conn.cursor() as cur:
                # Get database counts
                counts = {}
                for table in ['teams', 'users', 'collections', 'documents']:
                    try:
                        cur.execute(f'SELECT COUNT(*) as count FROM "{table}"')
                        counts[table] = cur.fetchone()['count']
                    except psycopg2.Error:
                        counts[table] = 0
                
                print(f"👥 Teams: {counts['teams']}")
                print(f"👤 Users: {counts['users']}")
                print(f"📚 Collections: {counts['collections']}")
                print(f"📄 Documents: {counts['documents']}")
                
        except Exception as e:
            self.logger.debug(f"Could not show database stats: {e}")
            print("👥 Teams: 0")
            print("👤 Users: 0")
            print("📚 Collections: 0")
            print("📄 Documents: 0")
        
        # Show file statistics
        try:
            import subprocess
            
            data_dir = "/var/lib/outline/data"
            if os.path.exists(data_dir):
                file_count = subprocess.check_output(
                    f'find "{data_dir}" -type f | wc -l', 
                    shell=True, text=True
                ).strip()
                file_size = subprocess.check_output(
                    f'du -sh "{data_dir}" | cut -f1', 
                    shell=True, text=True
                ).strip()
                print(f"📎 Files: {file_count} files ({file_size})")
            else:
                print("📎 Files: 0 files (0B)")
                
        except Exception as e:
            self.logger.debug(f"Could not show file stats: {e}")
            print("📎 Files: 0 files (0B)")

    def resolve_foreign_keys(self, table: str, record: Dict[str, Any]) -> Dict[str, Any]:
        """Resolve foreign key constraints by checking references or setting to None"""
        try:
            with self.conn.cursor() as cur:
                # Handle user foreign keys
                if 'invitedById' in record and record['invitedById']:
                    cur.execute('SELECT id FROM users WHERE id = %s', (record['invitedById'],))
                    if not cur.fetchone():
                        self.logger.debug(f"Setting invitedById to NULL - user {record['invitedById']} not found")
                        record['invitedById'] = None
                        
                if 'userId' in record and record['userId'] and table != 'users':
                    cur.execute('SELECT id FROM users WHERE id = %s', (record['userId'],))
                    if not cur.fetchone():
                        self.logger.debug(f"Setting userId to NULL - user {record['userId']} not found")
                        record['userId'] = None
                        
                # Handle team foreign keys  
                if 'teamId' in record and record['teamId']:
                    cur.execute('SELECT id FROM teams WHERE id = %s', (record['teamId'],))
                    if not cur.fetchone():
                        self.logger.debug(f"Setting teamId to NULL - team {record['teamId']} not found")
                        record['teamId'] = None
                        
                # Handle collection foreign keys
                if 'collectionId' in record and record['collectionId']:
                    cur.execute('SELECT id FROM collections WHERE id = %s', (record['collectionId'],))
                    if not cur.fetchone():
                        self.logger.debug(f"Setting collectionId to NULL - collection {record['collectionId']} not found")
                        record['collectionId'] = None
                        
        except Exception as e:
            self.logger.debug(f"Error resolving foreign keys: {e}")
            
        return record

    def create_basic_schema(self) -> bool:
        """Create basic schema manually if migrations fail"""
        self.logger.info("🔧 Creating basic database schema manually...")
        
        try:
            with self.conn.cursor() as cur:
                # Create basic tables that are essential for imports
                basic_schema = '''
                    CREATE TABLE IF NOT EXISTS teams (
                        id UUID PRIMARY KEY,
                        name VARCHAR,
                        "createdAt" TIMESTAMP WITH TIME ZONE NOT NULL,
                        "updatedAt" TIMESTAMP WITH TIME ZONE NOT NULL,
                        "deletedAt" TIMESTAMP WITH TIME ZONE
                    );
                    
                    CREATE TABLE IF NOT EXISTS users (
                        id UUID PRIMARY KEY,
                        email VARCHAR,
                        name VARCHAR,
                        "teamId" UUID REFERENCES teams(id),
                        "invitedById" UUID REFERENCES users(id),
                        "createdAt" TIMESTAMP WITH TIME ZONE NOT NULL,
                        "updatedAt" TIMESTAMP WITH TIME ZONE NOT NULL,
                        "deletedAt" TIMESTAMP WITH TIME ZONE
                    );
                    
                    CREATE TABLE IF NOT EXISTS collections (
                        id UUID PRIMARY KEY,
                        name VARCHAR NOT NULL,
                        description TEXT,
                        "teamId" UUID REFERENCES teams(id) NOT NULL,
                        "createdAt" TIMESTAMP WITH TIME ZONE NOT NULL,
                        "updatedAt" TIMESTAMP WITH TIME ZONE NOT NULL,
                        "deletedAt" TIMESTAMP WITH TIME ZONE,
                        sharing BOOLEAN DEFAULT true,
                        sort JSONB,
                        permission VARCHAR
                    );
                    
                    CREATE TABLE IF NOT EXISTS documents (
                        id UUID PRIMARY KEY,
                        title VARCHAR NOT NULL,
                        text TEXT,
                        content JSONB,
                        "teamId" UUID REFERENCES teams(id) NOT NULL,
                        "collectionId" UUID REFERENCES collections(id),
                        "createdById" UUID REFERENCES users(id),
                        "updatedById" UUID REFERENCES users(id),
                        "collaboratorIds" UUID[],
                        "createdAt" TIMESTAMP WITH TIME ZONE NOT NULL,
                        "updatedAt" TIMESTAMP WITH TIME ZONE NOT NULL,
                        "deletedAt" TIMESTAMP WITH TIME ZONE,
                        "publishedAt" TIMESTAMP WITH TIME ZONE
                    );
                    
                    CREATE TABLE IF NOT EXISTS attachments (
                        id UUID PRIMARY KEY,
                        key VARCHAR NOT NULL,
                        "documentId" UUID REFERENCES documents(id),
                        "teamId" UUID REFERENCES teams(id),
                        "userId" UUID REFERENCES users(id),
                        size INTEGER,
                        "contentType" VARCHAR,
                        "createdAt" TIMESTAMP WITH TIME ZONE NOT NULL,
                        "updatedAt" TIMESTAMP WITH TIME ZONE NOT NULL
                    );
                    
                    CREATE TABLE IF NOT EXISTS views (
                        id UUID PRIMARY KEY,
                        "documentId" UUID REFERENCES documents(id) NOT NULL,
                        "userId" UUID REFERENCES users(id),
                        "createdAt" TIMESTAMP WITH TIME ZONE NOT NULL,
                        "updatedAt" TIMESTAMP WITH TIME ZONE NOT NULL
                    );
                '''
                
                cur.execute(basic_schema)
                self.conn.commit()
                
                self.logger.info("✅ Basic schema created successfully")
                return True
                
        except Exception as e:
            self.logger.error(f"❌ Failed to create basic schema: {e}")
            self.conn.rollback()
            return False

    def grant_full_permissions_to_all_users(self):
        """Grant full read-write permissions to all users on all collections"""
        self.logger.info("🔐 Granting full read-write permissions to all users on all collections...")
        
        try:
            with self.conn.cursor() as cur:
                # Get all users
                cur.execute('SELECT id FROM users')
                users = cur.fetchall()
                user_ids = [user['id'] for user in users]
                
                # Get all collections  
                cur.execute('SELECT id FROM collections')
                collections = cur.fetchall()
                collection_ids = [collection['id'] for collection in collections]
                
                if not user_ids:
                    self.logger.info("   No users found - skipping permission setup")
                    return
                    
                if not collection_ids:
                    self.logger.info("   No collections found - skipping permission setup")
                    return
                
                self.logger.info(f"   Found {len(user_ids)} users and {len(collection_ids)} collections")
                
                # Create user_permissions records for all user-collection combinations
                permissions_created = 0
                permissions_updated = 0
                current_time = datetime.now(timezone.utc).isoformat()
                
                for user_id in user_ids:
                    for collection_id in collection_ids:
                        try:
                            # Check if permission already exists
                            cur.execute('''
                                SELECT id, permission FROM user_permissions 
                                WHERE "userId" = %s AND "collectionId" = %s
                            ''', (user_id, collection_id))
                            
                            existing_permission = cur.fetchone()
                            
                            if existing_permission:
                                # Update existing permission to read_write if it's not already
                                if existing_permission['permission'] != 'read_write':
                                    cur.execute('''
                                        UPDATE user_permissions 
                                        SET permission = %s, "updatedAt" = %s 
                                        WHERE id = %s
                                    ''', ('read_write', current_time, existing_permission['id']))
                                    permissions_updated += 1
                                    self.conn.commit()
                            else:
                                # Create new permission record
                                permission_id = str(uuid.uuid4())
                                cur.execute('''
                                    INSERT INTO user_permissions (id, "userId", "collectionId", permission, "createdAt", "updatedAt", "createdById") 
                                    VALUES (%s, %s, %s, %s, %s, %s, %s)
                                ''', (
                                    permission_id,
                                    user_id,
                                    collection_id,
                                    'read_write',  # Permission level
                                    current_time,  # createdAt
                                    current_time,  # updatedAt
                                    user_id        # createdById - use the user themselves as creator
                                ))
                                permissions_created += 1
                                self.conn.commit()
                            
                        except Exception as e:
                            self.logger.debug(f"Failed to process permission for user {user_id}, collection {collection_id}: {e}")
                            self.conn.rollback()
                            continue
                
                self.logger.info(f"✅ Permission setup complete: {permissions_created} created, {permissions_updated} updated")
                
        except Exception as e:
            self.logger.error(f"❌ Failed to grant permissions: {e}")
            self.conn.rollback()
            # Don't raise the exception - this is a bonus feature, not critical


def main():
    # Log Python information first
    log_python_info()
    print()  # Add spacing
    
    parser = argparse.ArgumentParser(description='Import Outline data')
    parser.add_argument('json_file', help='Path to workspace.json file')
    parser.add_argument('database_url', help='PostgreSQL database URL')
    parser.add_argument('--verbose', '-v', action='store_true', help='Verbose output')
    parser.add_argument('--skip-migrations', action='store_true', help='Skip database migrations (use if already run)')
    
    args = parser.parse_args()
    
    importer = OutlineImporter(args.database_url, args.verbose)
    
    try:
        # Connect to database
        importer.connect_database()
        
        # Ensure database schema exists (unless skipped)
        if not args.skip_migrations:
            importer.ensure_database_schema()
        else:
            importer.logger.info("⏭️  Skipping database migrations")
        
        # Load JSON data
        data = importer.load_json_data(args.json_file)
        
        # Import data - data is at root level, not nested under 'data'
        stats = {}
        total_success = 0
        total_records = 0
        
        for table in importer.import_order:
            if table in data:
                record_count = len(data[table])
                success_count = importer.import_table(table, data[table])
                stats[table] = success_count
                total_success += success_count
                total_records += record_count
            else:
                stats[table] = 0
                
        # Show summary
        importer.show_summary(data)
        
        if total_records > 0:
            success_rate = (total_success / total_records) * 100
            importer.logger.info(f"🎉 Import completed! {total_success}/{total_records} records imported ({success_rate:.1f}%)")
        else:
            importer.logger.info("🎉 Import completed! No data to import.")
        
        # Grant full permissions to all users
        importer.grant_full_permissions_to_all_users()
        
    except Exception as e:
        importer.logger.error(f"❌ Import failed: {e}")
        sys.exit(1)
    finally:
        if importer.conn:
            importer.conn.close()


if __name__ == '__main__':
    main() 
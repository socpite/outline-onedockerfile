#!/usr/bin/env python3
"""
Test script to simulate import process without database connections
"""

import json
import sys
import os
import uuid
from datetime import datetime, timezone

def simulate_import(json_file):
    """Simulate the import process to validate logic"""
    
    print(f"🔍 Simulating import of: {json_file}")
    
    if not os.path.exists(json_file):
        print(f"❌ File not found: {json_file}")
        return False
        
    try:
        with open(json_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
    except Exception as e:
        print(f"❌ Failed to load JSON: {e}")
        return False
        
    print(f"✅ JSON loaded successfully")
    
    # Simulate import order
    import_order = [
        'teams', 'users', 'collections', 'groups', 'documents',
        'attachments', 'shares', 'stars', 'pins', 'views', 
        'memberships', 'group_users'
    ]
    
    print("\n📊 Simulating Import Process:")
    print("=============================")
    
    # Track created collections
    created_collections = {}
    total_imported = 0
    
    for table in import_order:
        if table not in data:
            print(f"   {table}: missing from data")
            continue
            
        records = data[table]
        if not records:
            print(f"   {table}: no data")
            continue
            
        print(f"   {table}: processing {len(records)} records...")
        
        processed_count = 0
        skipped_count = 0
        
        for record in records:
            if not record or not record.get('id'):
                skipped_count += 1
                continue
                
            # Special handling for documents
            if table == 'documents':
                if record.get('collectionId') is None:
                    # Check if we have any collections
                    existing_collections = data.get('collections', [])
                    
                    if existing_collections:
                        # Assign to first existing collection
                        record['collectionId'] = existing_collections[0]['id']
                        print(f"     📄 Fixed document '{record.get('title', 'Unknown')}' - assigned to existing collection")
                    else:
                        # Create default collection
                        team_id = record.get('teamId')
                        if team_id:
                            if team_id not in created_collections:
                                collection_id = str(uuid.uuid4())
                                created_collections[team_id] = collection_id
                                print(f"     📚 Created default collection for team: {team_id}")
                            
                            record['collectionId'] = created_collections[team_id]
                            print(f"     📄 Fixed document '{record.get('title', 'Unknown')}' - assigned to default collection")
                        else:
                            print(f"     ⚠️  Skipping document '{record.get('title', 'Unknown')}' - no team ID")
                            skipped_count += 1
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
                        print(f"     📝 Generated content from text for document '{record.get('title', 'Unknown')}'")
                    else:
                        record['content'] = {
                            "type": "doc",
                            "content": [{"type": "paragraph"}]
                        }
                        print(f"     📝 Created empty content for document '{record.get('title', 'Unknown')}'")
                
                # Fix collaboratorIds
                if record.get('collaboratorIds') is None:
                    record['collaboratorIds'] = []
                    
            processed_count += 1
            
        print(f"     ✅ {table}: {processed_count} processed, {skipped_count} skipped")
        total_imported += processed_count
    
    # Show summary
    print(f"\n📊 Simulation Summary:")
    print(f"======================")
    print(f"   Total records processed: {total_imported}")
    print(f"   Default collections created: {len(created_collections)}")
    
    # Show what would be imported
    final_counts = {}
    for table in import_order:
        if table in data:
            count = len([r for r in data[table] if r and r.get('id')])
            final_counts[table] = count
        else:
            final_counts[table] = 0
    
    # Add created collections
    final_counts['collections'] += len(created_collections)
    
    print(f"\n📊 Final Expected Counts:")
    print(f"=========================")
    print(f"📅 Export Date: {data.get('exportedAt', 'Unknown')}")
    print(f"🏷️  Export Version: {data.get('version', 'Unknown')}")
    print(f"👥 Teams: {final_counts['teams']}")
    print(f"👤 Users: {final_counts['users']}")
    print(f"📚 Collections: {final_counts['collections']}")
    print(f"📄 Documents: {final_counts['documents']}")
    print(f"📎 Files: 0 files (0B)")  # Would need to check files directory
    
    print(f"\n🎯 Import simulation completed successfully!")
    return True

if __name__ == '__main__':
    if len(sys.argv) != 2:
        print("Usage: python3 test-import-dry-run.py <workspace.json>")
        sys.exit(1)
        
    simulate_import(sys.argv[1]) 
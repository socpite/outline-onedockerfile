#!/usr/bin/env python3
"""
Test script to validate import data format
"""

import json
import sys
import os

def test_data_format(json_file):
    """Test the data format to ensure import scripts will work"""
    
    print(f"🔍 Testing data format in: {json_file}")
    
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
    
    # Check top-level structure
    print("\n📊 Data Structure:")
    print("==================")
    
    # Check for expected tables
    tables = ['teams', 'users', 'collections', 'groups', 'documents', 
              'attachments', 'shares', 'stars', 'pins', 'views', 
              'memberships', 'group_users']
    
    total_records = 0
    for table in tables:
        if table in data:
            count = len(data[table]) if isinstance(data[table], list) else 0
            print(f"   {table}: {count} records")
            total_records += count
        else:
            print(f"   {table}: missing")
            
    print(f"\nTotal records: {total_records}")
    
    # Check metadata
    print("\n📅 Metadata:")
    print("=============")
    export_date = data.get('exportedAt', 'Missing')
    export_version = data.get('version', 'Missing')
    print(f"   Export Date: {export_date}")
    print(f"   Version: {export_version}")
    
    # Check for potential issues
    print("\n🔍 Potential Issues:")
    print("===================")
    
    issues = []
    
    # Check documents with null collectionId when no collections exist
    if 'documents' in data and 'collections' in data:
        collections_count = len(data['collections'])
        documents_with_null_collection = sum(
            1 for doc in data['documents'] 
            if doc.get('collectionId') is None
        )
        
        if collections_count == 0 and documents_with_null_collection > 0:
            issues.append(f"Found {documents_with_null_collection} documents with null collectionId but no collections exist")
            
        # Check documents with missing content
        documents_with_no_content = sum(
            1 for doc in data['documents']
            if not doc.get('content') and not doc.get('text')
        )
        
        if documents_with_no_content > 0:
            issues.append(f"Found {documents_with_no_content} documents with no content or text")
    
    if not issues:
        print("   ✅ No obvious issues found")
    else:
        for issue in issues:
            print(f"   ⚠️  {issue}")
            
    print(f"\n🎯 Import should {'work' if total_records > 0 else 'have no data to import'}")
    
    return True

if __name__ == '__main__':
    if len(sys.argv) != 2:
        print("Usage: python3 test-import-format.py <workspace.json>")
        sys.exit(1)
        
    test_data_format(sys.argv[1]) 
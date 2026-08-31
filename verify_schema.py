#!/usr/bin/env python3
"""
Verify database schema is correct
"""

import sqlite3
import os

DB_PATH = r'd:\OD\OneDrive\BaiduSyncdisk\Learn\Project Easy\Python Programs\Too Easy\instance\assignments.db'

def verify_schema():
    print("Verifying database schema...")
    print("=" * 60)
    
    if not os.path.exists(DB_PATH):
        print(f"❌ Database not found at: {DB_PATH}")
        return False
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Check assignment table structure
    print("\n1. Checking assignment table structure...")
    cursor.execute("PRAGMA table_info(assignment)")
    columns = cursor.fetchall()
    
    print(f"   Found {len(columns)} columns:")
    column_names = [col[1] for col in columns]
    for col in columns:
        print(f"   - {col[1]} ({col[2]})")
    
    # Check for required columns
    required_columns = ['id', 'title', 'description', 'created_by', 'created_at', 'due_date', 'is_active', 'html_filename', 'html_content']
    print(f"\n2. Checking for required columns...")
    missing = []
    for req_col in required_columns:
        if req_col in column_names:
            print(f"   ✅ {req_col}")
        else:
            print(f"   ❌ {req_col} - MISSING")
            missing.append(req_col)
    
    # Check data
    print(f"\n3. Checking assignment data...")
    cursor.execute("SELECT COUNT(*) FROM assignment")
    count = cursor.fetchone()[0]
    print(f"   Total assignments: {count}")
    
    if count > 0:
        cursor.execute("SELECT id, title, created_by FROM assignment LIMIT 5")
        assignments = cursor.fetchall()
        print(f"   Sample assignments:")
        for assignment in assignments:
            print(f"   - ID: {assignment[0]}, Title: {assignment[1]}, Created By: {assignment[2]}")
    
    conn.close()
    
    print("\n" + "=" * 60)
    if not missing:
        print("✅ Database schema is CORRECT!")
        print("✅ All required columns are present!")
        return True
    else:
        print(f"❌ Missing columns: {missing}")
        return False

if __name__ == "__main__":
    verify_schema()

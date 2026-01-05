#!/usr/bin/env python3
"""
Script to check and fix the assignment table schema
"""

import sqlite3
import os

db_path = os.path.join(os.path.dirname(__file__), 'instance', 'assignments.db')
print(f"Database path: {db_path}")

conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# Check current schema
print("\n=== Current Assignment Table Schema ===")
cursor.execute("PRAGMA table_info(assignment)")
columns = cursor.fetchall()
for col in columns:
    print(f"  {col[1]} ({col[2]})")

# Check if created_by column exists
column_names = [col[1] for col in columns]
print(f"\nExisting columns: {column_names}")

if 'created_by' not in column_names:
    print("\n❌ 'created_by' column is MISSING!")
    print("Adding 'created_by' column...")
    
    try:
        cursor.execute("ALTER TABLE assignment ADD COLUMN created_by INTEGER")
        conn.commit()
        print("✅ Successfully added 'created_by' column")
        
        # Update existing rows to set created_by to 1 (assuming admin user has id=1)
        cursor.execute("SELECT COUNT(*) FROM assignment")
        count = cursor.fetchone()[0]
        if count > 0:
            print(f"\nUpdating {count} existing assignments...")
            cursor.execute("UPDATE assignment SET created_by = 1 WHERE created_by IS NULL")
            conn.commit()
            print("✅ Updated existing assignments")
    except Exception as e:
        print(f"❌ Error adding column: {e}")
        conn.rollback()
else:
    print("\n✅ 'created_by' column exists")

# Check for other missing columns
print("\n=== Checking for other missing columns ===")
expected_columns = ['id', 'title', 'description', 'created_by', 'created_at', 'due_date', 'is_active', 'html_filename', 'html_content']
for col in expected_columns:
    if col not in column_names:
        print(f"  ❌ Missing: {col}")
    else:
        print(f"  ✅ Exists: {col}")

conn.close()
print("\n=== Schema check complete ===")

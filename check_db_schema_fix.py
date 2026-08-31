#!/usr/bin/env python3
"""Check and fix database schema for HTML-only assignments"""

import sqlite3
import os

def check_database_schema():
    """Check the current database schema"""
    db_path = 'instance/assignments.db'
    
    if not os.path.exists(db_path):
        print("Database file does not exist!")
        return
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Check if assignment table exists
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='assignment'")
    table_exists = cursor.fetchone()
    
    if not table_exists:
        print("Assignment table does not exist!")
        conn.close()
        return
    
    # Get current table schema
    cursor.execute("PRAGMA table_info(assignment)")
    columns = cursor.fetchall()
    
    print("Current assignment table columns:")
    for col in columns:
        print(f"  {col[1]} ({col[2]})")
    
    # Check for required columns
    required_columns = ['html_filename', 'html_content']
    missing_columns = []
    
    for req_col in required_columns:
        if not any(req_col == col[1] for col in columns):
            missing_columns.append(req_col)
    
    print(f"\nMissing columns: {missing_columns}")
    
    if missing_columns:
        print("\nDatabase schema needs updating!")
        return True, missing_columns
    else:
        print("\nDatabase schema is up to date!")
        return False, []
    
    conn.close()

def fix_database_schema():
    """Fix the database schema by adding missing columns"""
    db_path = 'instance/assignments.db'
    
    if not os.path.exists(db_path):
        print("Database file does not exist!")
        return
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Add missing columns
    try:
        # Add html_filename column if it doesn't exist
        cursor.execute("""
            ALTER TABLE assignment ADD COLUMN html_filename TEXT
        """)
        print("✓ Added html_filename column")
    except sqlite3.OperationalError as e:
        if "duplicate column name" in str(e):
            print("✓ html_filename column already exists")
        else:
            print(f"✗ Error adding html_filename: {e}")
    
    try:
        # Add html_content column if it doesn't exist
        cursor.execute("""
            ALTER TABLE assignment ADD COLUMN html_content TEXT
        """)
        print("✓ Added html_content column")
    except sqlite3.OperationalError as e:
        if "duplicate column name" in str(e):
            print("✓ html_content column already exists")
        else:
            print(f"✗ Error adding html_content: {e}")
    
    # Commit changes
    conn.commit()
    
    # Verify the changes
    cursor.execute("PRAGMA table_info(assignment)")
    columns = cursor.fetchall()
    
    print("\nUpdated assignment table columns:")
    for col in columns:
        print(f"  {col[1]} ({col[2]})")
    
    conn.close()

if __name__ == "__main__":
    print("Checking database schema...")
    needs_fix, missing_columns = check_database_schema()
    
    if needs_fix:
        print("\nFixing database schema...")
        fix_database_schema()
        print("\nDatabase schema fixed successfully!")
    else:
        print("\nNo fixes needed.")
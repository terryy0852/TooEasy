#!/usr/bin/env python3
"""Fix the submission table schema by adding the missing screenshot_filename column"""

import sqlite3
import os

def fix_submission_schema():
    db_path = 'instance/assignments.db'
    
    if not os.path.exists(db_path):
        print(f"Database not found at {db_path}")
        return
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        # Check if the column already exists
        cursor.execute('PRAGMA table_info(submission)')
        columns = cursor.fetchall()
        column_names = [column[1] for column in columns]
        
        if 'screenshot_filename' not in column_names:
            print("Adding screenshot_filename column to submission table...")
            cursor.execute('ALTER TABLE submission ADD COLUMN screenshot_filename TEXT')
            print("✅ Column added successfully!")
        else:
            print("screenshot_filename column already exists")
            
        # Commit the changes
        conn.commit()
        
        # Verify the change
        cursor.execute('PRAGMA table_info(submission)')
        columns = cursor.fetchall()
        print("\nUpdated submission table columns:")
        for column in columns:
            print(f"  {column[1]} ({column[2]})")
            
    except Exception as e:
        print(f"Error: {e}")
        conn.rollback()
    finally:
        conn.close()

if __name__ == "__main__":
    fix_submission_schema()
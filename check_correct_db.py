#!/usr/bin/env python3
"""
Check the correct database file
"""

import sqlite3
import os

# Check the correct database path
db_path = 'instance/assignments.db'
if os.path.exists(db_path):
    print(f'Found database at: {db_path}')
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    print('\n=== Database Tables ===')
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
    for table in cursor.fetchall():
        print(f'- {table[0]}')
    
    # Check each table
    for table_name in ['user', 'assignment', 'student_assignment', 'submission']:
        try:
            print(f'\n=== {table_name} Table ===')
            cursor.execute(f'SELECT * FROM {table_name} LIMIT 5')
            rows = cursor.fetchall()
            if rows:
                for row in rows:
                    print(row)
            else:
                print('No data found')
        except sqlite3.OperationalError as e:
            print(f'Table {table_name}: {e}')
    
    conn.close()
else:
    print(f'Database not found at: {db_path}')
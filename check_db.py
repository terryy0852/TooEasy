#!/usr/bin/env python3
"""
Simple script to check the database contents
"""

import sqlite3

def check_database():
    """Check the database contents"""
    conn = sqlite3.connect('school.db')
    cursor = conn.cursor()
    
    print('=== Database Tables ===')
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
    tables = cursor.fetchall()
    for table in tables:
        print(f"- {table[0]}")
    
    # Check each table
    for table_name in ['user', 'assignment', 'student_assignment', 'submission']:
        if table_name in [t[0] for t in tables]:
            print(f'\n=== {table_name} Table ===')
            cursor.execute(f'SELECT * FROM {table_name} LIMIT 5')
            rows = cursor.fetchall()
            if rows:
                for row in rows:
                    print(row)
            else:
                print("No data found")
    
    conn.close()

if __name__ == "__main__":
    check_database()
import sqlite3
import os

print("=== Checking Database Schema ===\n")

# Path to the database
db_path = os.path.join('instance', 'assignments.db')

if os.path.exists(db_path):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Get database schema info
    print("1. Database tables:")
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
    tables = cursor.fetchall()
    for table in tables:
        print(f"   - {table[0]}")
    
    print("\n2. User table schema:")
    cursor.execute("PRAGMA table_info(user)")
    columns = cursor.fetchall()
    for column in columns:
        print(f"   - ID: {column[0]}, Name: {column[1]}, Type: {column[2]}, Not Null: {column[3]}, Default: {column[4]}, Primary Key: {column[5]}")
    
    print("\n3. Assignment table schema:")
    cursor.execute("PRAGMA table_info(assignment)")
    columns = cursor.fetchall()
    for column in columns:
        print(f"   - ID: {column[0]}, Name: {column[1]}, Type: {column[2]}, Not Null: {column[3]}, Default: {column[4]}, Primary Key: {column[5]}")
    
    print("\n4. Submission table schema:")
    cursor.execute("PRAGMA table_info(submission)")
    columns = cursor.fetchall()
    for column in columns:
        print(f"   - ID: {column[0]}, Name: {column[1]}, Type: {column[2]}, Not Null: {column[3]}, Default: {column[4]}, Primary Key: {column[5]}")
    
    # Check user data
    print("\n5. Current user data:")
    cursor.execute("SELECT * FROM user LIMIT 1")
    user = cursor.fetchone()
    if user:
        print(f"   First user data: {user}")
    
    conn.close()
else:
    print(f"Database not found at: {db_path}")
    print("Checking if instance directory exists:")
    if os.path.exists('instance'):
        print("Instance directory exists. Files:")
        for file in os.listdir('instance'):
            print(f"   - {file}")
    else:
        print("Instance directory does not exist.")

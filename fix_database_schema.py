import sqlite3
import os

print("=== Fixing Database Schema ===\n")

# Path to the database
db_path = os.path.join('instance', 'assignments.db')

if os.path.exists(db_path):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    print("1. Current user table columns:")
    cursor.execute("PRAGMA table_info(user)")
    columns = cursor.fetchall()
    column_names = [col[1] for col in columns]
    for col in columns:
        print(f"   - {col[1]} ({col[2]})")
    
    # Fix the column name from 'hash' to 'password_hash'
    if 'hash' in column_names:
        print("\n2. Fixing column name from 'hash' to 'password_hash'...")
        
        # Step 1: Create a temporary table with the correct schema
        cursor.execute('''
            CREATE TABLE user_temp (
                id INTEGER PRIMARY KEY,
                username VARCHAR(100) UNIQUE NOT NULL,
                email VARCHAR(100) UNIQUE NOT NULL,
                password_hash VARCHAR(200) NOT NULL,
                role VARCHAR(50) NOT NULL DEFAULT 'student',
                created_at DATETIME
            )
        ''')
        
        # Step 2: Copy data from old table to new table
        cursor.execute('''
            INSERT INTO user_temp (id, username, email, password_hash, role, created_at)
            SELECT id, username, email, hash, role, created_at
            FROM user
        ''')
        
        # Step 3: Drop the old table
        cursor.execute('DROP TABLE user')
        
        # Step 4: Rename the new table to user
        cursor.execute('ALTER TABLE user_temp RENAME TO user')
        
        conn.commit()
        print("✓ Column name fixed successfully!")
    
    else:
        print("\n2. No 'hash' column found. Checking if 'password_hash' exists...")
        if 'password_hash' in column_names:
            print("✓ 'password_hash' column already exists. Database schema is correct.")
        else:
            print("✗ Neither 'hash' nor 'password_hash' column found. Database schema is incorrect.")
    
    print("\n3. Updated user table columns:")
    cursor.execute("PRAGMA table_info(user)")
    columns = cursor.fetchall()
    for col in columns:
        print(f"   - {col[1]} ({col[2]})")
    
    # Verify the admin user still exists
    print("\n4. Verifying admin user:")
    cursor.execute("SELECT username, email, role FROM user WHERE username='admin'")
    admin = cursor.fetchone()
    if admin:
        print(f"✓ Admin user found: {admin[0]} ({admin[2]})")
    else:
        print("✗ Admin user not found!")
    
    conn.close()
    print("\n=== Database schema fix completed! ===")
else:
    print(f"Database not found at: {db_path}")
    print("Please make sure the database exists in the instance folder.")

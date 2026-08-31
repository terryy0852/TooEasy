import sqlite3
import os
from werkzeug.security import generate_password_hash

print("=== Creating Test User ===\n")

# Path to the database
db_path = os.path.join('instance', 'assignments.db')

if os.path.exists(db_path):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Create a test student user
    test_username = 'teststudent'
    test_email = 'teststudent@example.com'
    test_password = 'password123'
    test_role = 'student'
    
    # Check if user already exists
    cursor.execute("SELECT username FROM user WHERE username=?", (test_username,))
    existing_user = cursor.fetchone()
    
    if existing_user:
        print(f"Test user '{test_username}' already exists. Deleting and recreating...")
        cursor.execute("DELETE FROM user WHERE username=?", (test_username,))
    
    # Hash the password
    hashed_password = generate_password_hash(test_password)
    
    # Insert the test user
    cursor.execute(
        "INSERT INTO user (username, email, password_hash, role) VALUES (?, ?, ?, ?)",
        (test_username, test_email, hashed_password, test_role)
    )
    
    conn.commit()
    print(f"✅ Test user created successfully!")
    print(f"   Username: {test_username}")
    print(f"   Email: {test_email}")
    print(f"   Password: {test_password}")
    print(f"   Role: {test_role}")
    
    # Verify the user was created
    cursor.execute("SELECT username, role FROM user WHERE username=?", (test_username,))
    created_user = cursor.fetchone()
    
    if created_user:
        print(f"\n✅ Verification: User '{created_user[0]}' ({created_user[1]}) created successfully!")
    
    # Show all users
    print(f"\n=== Current Users in Database ===")
    cursor.execute("SELECT username, role, email FROM user")
    users = cursor.fetchall()
    
    for user in users:
        print(f"  - {user[0]} (role: {user[1]}, email: {user[2]})")
    
    conn.close()
else:
    print(f"Database not found at: {db_path}")

import sqlite3
import os
from werkzeug.security import check_password_hash

print("=== Checking Admin Password ===\n")

# Path to the database
db_path = os.path.join('instance', 'assignments.db')

if os.path.exists(db_path):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Get admin user data
    cursor.execute("SELECT username, password_hash, role FROM user WHERE username='admin'")
    admin = cursor.fetchone()
    
    if admin:
        username, password_hash, role = admin
        print(f"Admin user found:")
        print(f"  Username: {username}")
        print(f"  Role: {role}")
        print(f"  Password hash: {password_hash[:50]}...")
        
        # Test common passwords
        common_passwords = ['admin', 'password', '123456', 'admin123', 'Admin123', '']
        print(f"\nTesting common passwords:")
        
        for password in common_passwords:
            is_correct = check_password_hash(password_hash, password)
            print(f"  '{password}': {'✓ CORRECT' if is_correct else '✗ INCORRECT'}")
            if is_correct:
                print(f"  ✅ Found the correct password: '{password}'")
                break
        
        if not any(check_password_hash(password_hash, pwd) for pwd in common_passwords):
            print("\n⚠️  None of the common passwords worked.")
            print("   The admin password might be something else.")
            
    else:
        print("✗ Admin user not found in database!")
    
    conn.close()
else:
    print(f"Database not found at: {db_path}")

# Let's also check if there are any other users
print("\n=== Checking All Users ===")
if os.path.exists(db_path):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    cursor.execute("SELECT username, role, email FROM user")
    users = cursor.fetchall()
    
    if users:
        print(f"Found {len(users)} user(s) in database:")
        for user in users:
            print(f"  - {user[0]} (role: {user[1]}, email: {user[2]})")
    else:
        print("No users found in database.")
    
    conn.close()

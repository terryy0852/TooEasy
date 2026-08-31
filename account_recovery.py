#!/usr/bin/env python3
"""
Account recovery script for Too Easy application
This script can help recover access by:
1. Listing all users in the database
2. Resetting passwords for specific users
"""

import os
import sys
import psycopg2
from werkzeug.security import check_password_hash, generate_password_hash

# Get database URL from environment or use default
# Try Railway URL first, then fallback to Supabase URL from check_production_user.py
railway_url = os.environ.get('DATABASE_URL')
supabase_url = 'postgresql://postgres:n5jTtilYoz2S1LwO@db.xqjscxsvcespsrkyoekf.supabase.co:5432/postgres'
database_url = railway_url or supabase_url

def list_all_users():
    """List all users in the database"""
    try:
        print("Connecting to database...")
        conn = psycopg2.connect(database_url)
        cursor = conn.cursor()
        
        # Check if the table exists and what columns it has
        cursor.execute("SELECT column_name FROM information_schema.columns WHERE table_name = 'user'")
        columns = [col[0] for col in cursor.fetchall()]
        print(f"\nUser table columns: {', '.join(columns)}")
        
        # Get all users
        print("\n=== All Users ===")
        if 'username' in columns and 'email' in columns:
            cursor.execute('SELECT id, username, email FROM "user"')
            users = cursor.fetchall()
            
            if users:
                print(f"Found {len(users)} user(s):")
                for user in users:
                    print(f"ID: {user[0]}, Username: {user[1]}, Email: {user[2]}")
            else:
                print("No users found in database")
        else:
            # Fallback if column names are different
            cursor.execute('SELECT * FROM "user"')
            users = cursor.fetchall()
            if users:
                print(f"Found {len(users)} user(s):")
                for i, user in enumerate(users):
                    print(f"User {i+1}: {user}")
            else:
                print("No users found in database")
        
        conn.close()
        return users
        
    except Exception as e:
        print(f"Error listing users: {e}")
        return None

def reset_user_password(username, new_password):
    """Reset password for a specific user"""
    try:
        print(f"\nResetting password for user '{username}'...")
        conn = psycopg2.connect(database_url)
        cursor = conn.cursor()
        
        # Generate new password hash
        hashed_password = generate_password_hash(new_password)
        
        # Update the user's password
        cursor.execute('UPDATE "user" SET password = %s WHERE username = %s', (hashed_password, username))
        conn.commit()
        
        if cursor.rowcount > 0:
            print(f"✅ Password reset successful for user '{username}'")
        else:
            print(f"❌ User '{username}' not found")
        
        conn.close()
        return cursor.rowcount > 0
        
    except Exception as e:
        print(f"Error resetting password: {e}")
        return False

def main():
    print("🚀 Too Easy Account Recovery Tool")
    print("=" * 50)
    print(f"Using database: {database_url}")
    
    # List all users
    users = list_all_users()
    
    if not users:
        print("\nNo users found. Exiting...")
        sys.exit(1)
    
    # Ask if user wants to reset a password
    reset_choice = input("\nWould you like to reset a password? (y/n): ").lower()
    
    if reset_choice == 'y':
        username = input("Enter the username to reset: ")
        new_password = input("Enter new password: ")
        
        # Validate password strength
        if len(new_password) < 8:
            print("❌ Password must be at least 8 characters long")
            sys.exit(1)
        
        if not any(c.isupper() for c in new_password):
            print("❌ Password must contain at least one uppercase letter")
            sys.exit(1)
        
        if not any(c.islower() for c in new_password):
            print("❌ Password must contain at least one lowercase letter")
            sys.exit(1)
        
        if not any(c.isdigit() for c in new_password):
            print("❌ Password must contain at least one digit")
            sys.exit(1)
        
        # Check for special characters
        special_chars = "!@#$%^&*()-_=+[]{}|;:,.<>?"
        if not any(c in special_chars for c in new_password):
            print("❌ Password must contain at least one special character")
            sys.exit(1)
        
        reset_user_password(username, new_password)
    
    print("\nAccount recovery process complete.")

if __name__ == "__main__":
    main()



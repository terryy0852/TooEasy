#!/usr/bin/env python3
"""
Script to check if test_tutor user exists in production database and verify their credentials
"""

import os
import psycopg2
from werkzeug.security import check_password_hash

# Get database URL from environment (same as production)
database_url = os.environ.get('DATABASE_URL', 'postgresql://postgres:n5jTtilYoz2S1LwO@db.xqjscxsvcespsrkyoekf.supabase.co:5432/postgres')

def check_user_in_production():
    try:
        print("Connecting to production database...")
        conn = psycopg2.connect(database_url)
        cursor = conn.cursor()
        
        # Check if test_tutor user exists
        cursor.execute("SELECT id, username, password_hash, role FROM users WHERE username = %s", ('test_tutor',))
        user = cursor.fetchone()
        
        if user:
            print(f"✅ User found: ID={user[0]}, Username={user[1]}, Role={user[3]}")
            print(f"   Password hash: {user[2]}")
            
            # Test if we can verify the password (this should work if SECRET_KEY is correct)
            test_password = "test_password"
            if user[2].startswith('pbkdf2:sha256:'):
                # Modern hashed password
                is_valid = check_password_hash(user[2], test_password)
                print(f"   Password verification: {'✅ SUCCESS' if is_valid else '❌ FAILED'}")
            else:
                # Legacy plaintext password
                is_valid = (user[2] == test_password)
                print(f"   Legacy password check: {'✅ MATCH' if is_valid else '❌ MISMATCH'}")
                
        else:
            print("❌ User 'test_tutor' not found in production database")
            
        # Check total user count
        cursor.execute("SELECT COUNT(*) FROM users")
        user_count = cursor.fetchone()[0]
        print(f"Total users in database: {user_count}")
        
        conn.close()
        
    except Exception as e:
        print(f"❌ Error connecting to database: {e}")

if __name__ == "__main__":
    check_user_in_production()
# Script to recreate the database with all required columns
import os
import sys

# Add the current directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Import the app module
from app import app, db, create_tables

# Path to the database file using the instance folder
instance_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'instance')
db_path = os.path.join(instance_dir, 'assignments.db')

def recreate_database():
    print("=== Recreating Database ===")
    print(f"Database file: {db_path}")
    
    # Remove the old database file if it exists
    if os.path.exists(db_path):
        os.remove(db_path)
        print(f"✓ Removed old database: {db_path}")
    else:
        print(f"Database file {db_path} not found")
    
    # Create new tables
    print("Creating new tables...")
    with app.app_context():
        create_tables()
        print("✓ Created all tables")
        
        # Verify tables exist
        from app import User
        print("\n✓ User model columns:")
        print(f"  - id: {hasattr(User, 'id')}")
        print(f"  - username: {hasattr(User, 'username')}")
        print(f"  - email: {hasattr(User, 'email')}")
        print(f"  - password_hash: {hasattr(User, 'password_hash')}")
        print(f"  - role: {hasattr(User, 'role')}")
        print(f"  - created_at: {hasattr(User, 'created_at')}")

    print("\n=== Database Recreation Complete ===")
    print("All columns should now be available!")

if __name__ == "__main__":
    recreate_database()

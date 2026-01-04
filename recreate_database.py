# Script to recreate the database with all required columns
import os
import sys

# Add the current directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Import the app module
from app import app, db, create_tables

# Path to the database file
db_path = 'assignments.db'

def recreate_database():
    print("=== Recreating Database ===")
    
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
        print("\n✓ User model has password reset fields:")
        print(f"  - reset_token: {hasattr(User, 'reset_token')}")
        print(f"  - reset_token_expiry: {hasattr(User, 'reset_token_expiry')}")
    
    print("\n=== Database Recreation Complete ===")
    print("All columns including password reset fields should now be available!")

if __name__ == "__main__":
    recreate_database()

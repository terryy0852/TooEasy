# Force recreate all database tables with password reset columns
import os
import sys
from sqlalchemy import inspect

# Add the current directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Import the app module
from app import app, db

def force_recreate_database():
    print("=== Force Recreating Database ===")
    
    # Path to the database file from the app config
    db_url = app.config['SQLALCHEMY_DATABASE_URI']
    print(f"Database URL: {db_url}")
    
    # Remove the old database file if it's SQLite
    if db_url.startswith('sqlite:///'):
        db_path = db_url[10:]
        if os.path.exists(db_path):
            os.remove(db_path)
            print(f"✓ Removed old SQLite database: {db_path}")
        else:
            print(f"Database file {db_path} not found")
    
    with app.app_context():
        print("\n=== Recreating Tables ===")
        
        # Drop all existing tables first
        print("Dropping all existing tables...")
        try:
            db.drop_all()
            print("✓ Dropped all tables")
        except Exception as e:
            print(f"⚠️  Warning: Could not drop tables: {e}")
        
        # Now create all tables with the updated models
        print("Creating new tables...")
        db.create_all()
        print("✓ Created all tables")
        
        # Verify the User table structure
        print("\n=== Verifying User Table Structure ===")
        inspector = inspect(db.engine)
        
        if inspector.has_table('user'):
            user_columns = inspector.get_columns('user')
            print(f"User table columns: {[col['name'] for col in user_columns]}")
            
            # Check for password reset columns
            columns = {col['name'] for col in user_columns}
            required_columns = {'id', 'username', 'email', 'password', 'is_tutor', 'reset_token', 'reset_token_expiry'}
            
            missing = required_columns - columns
            if missing:
                print(f"❌ Missing columns: {missing}")
                return False
            else:
                print("✅ All required columns are present!")
                
                # Test inserting a user with password reset fields
                print("\n=== Testing User Insert with Reset Fields ===")
                from app import User
                from werkzeug.security import generate_password_hash
                import datetime
                import secrets
                
                try:
                    # Create a test user with reset token
                    test_user = User(
                        username='test_user',
                        email='test@example.com',
                        password=generate_password_hash('Test123!'),
                        is_tutor=False,
                        reset_token=secrets.token_hex(16),
                        reset_token_expiry=datetime.datetime.utcnow() + datetime.timedelta(hours=1)
                    )
                    db.session.add(test_user)
                    db.session.commit()
                    print("✅ Successfully inserted user with reset token fields!")
                    
                    # Test querying by reset token
                    found_user = User.query.filter_by(reset_token=test_user.reset_token).first()
                    if found_user:
                        print("✅ Successfully queried user by reset token!")
                    
                    # Clean up
                    db.session.delete(test_user)
                    db.session.commit()
                    print("✅ Cleaned up test user")
                    
                except Exception as e:
                    print(f"❌ Error testing insert: {e}")
                    import traceback
                    traceback.print_exc()
                    return False
        else:
            print("❌ User table not found!")
            return False
    
    print("\n=== Database Recreation Complete ===")
    print("All tables have been successfully recreated with password reset columns!")
    return True

if __name__ == "__main__":
    success = force_recreate_database()
    sys.exit(0 if success else 1)

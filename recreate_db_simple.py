import os
import sys
from app import app, db

# Add the current directory to the path to ensure imports work correctly
# sys.path.append(os.path.dirname(os.path.abspath(__file__)))

print("Recreating database...")

# Path to the SQLite database file
instance_dir = 'instance'
db_file = os.path.join(instance_dir, 'assignments.db')

# Create instance directory if it doesn't exist
if not os.path.exists(instance_dir):
    os.makedirs(instance_dir)

# Remove the existing database file if it exists
if os.path.exists(db_file):
    print(f"Removing existing database: {db_file}")
    os.remove(db_file)

with app.app_context():
    try:
        # Create all tables
        print("Creating database tables...")
        db.create_all()
        print("Database tables created successfully")
        
        # Import User model here to avoid circular imports
        from app import User
        
        # Create admin user
        print("Creating admin user...")
        admin_user = User(username='admin', email='admin@example.com', role='admin')
        admin_user.set_password('admin123')
        db.session.add(admin_user)
        db.session.commit()
        print("Admin user created successfully")
        
        print("Database recreation completed successfully")
        
    except Exception as e:
        print(f"Error recreating database: {e}")
        import traceback
        traceback.print_exc()
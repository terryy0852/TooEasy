# Script to properly recreate the database
from app import app, db, User
import os

# Delete existing empty database file
if os.path.exists('app.db'):
    os.remove('app.db')
    print("Removed existing empty database file")

with app.app_context():
    try:
        # Create all tables
        db.create_all()
        print("Successfully created database tables")
        
        # Test creating a teacher account for debugging
        test_teacher = User(
            username='testteacher',
            email='testteacher@example.com',
            role='teacher'
        )
        test_teacher.set_password('password123')
        
        test_student = User(
            username='teststudent',
            email='teststudent@example.com',
            role='student'
        )
        test_student.set_password('password123')
        
        db.session.add(test_teacher)
        db.session.add(test_student)
        db.session.commit()
        print("Created test teacher and student accounts")
        
        # Verify accounts were created
        users = User.query.all()
        print(f"Total users created: {len(users)}")
        for user in users:
            print(f"  {user.username} ({user.role}): {user.email}")
            
    except Exception as e:
        print(f"Error creating database: {e}")
        import traceback
        traceback.print_exc()

print("Database recreation complete!")

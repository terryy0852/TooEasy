# Debug script to check teacher login issues
from app import app, db, User
from werkzeug.security import check_password_hash, generate_password_hash

with app.app_context():
    print("=== Teacher Login Debug ===")
    
    # Check all users in database
    users = User.query.all()
    print(f"\nTotal users in database: {len(users)}")
    print("\nUser details:")
    for user in users:
        print(f"ID: {user.id}, Username: {user.username}, Role: {user.role}, Email: {user.email}")
        print(f"  Password hash: {user.password_hash}")
        
    # Check if teacher accounts exist
    teacher_users = User.query.filter_by(role='teacher').all()
    print(f"\nTeacher accounts: {len(teacher_users)}")
    for teacher in teacher_users:
        print(f"  Teacher: {teacher.username} (ID: {teacher.id})")
        
    # Test password check
    if teacher_users:
        test_teacher = teacher_users[0]
        print(f"\nTesting password check for {test_teacher.username}:")
        # Try with a common password (you might need to adjust this)
        test_passwords = ['password', 'teacher123', '123456']
        for pwd in test_passwords:
            is_valid = check_password_hash(test_teacher.password_hash, pwd)
            print(f"  Password '{pwd}': {'Valid' if is_valid else 'Invalid'}")
    
    print("\n=== Debug Complete ===")

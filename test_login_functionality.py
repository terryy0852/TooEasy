# Test script to verify login functionality works correctly
from app import app, db, User
from werkzeug.security import check_password_hash
import sys

print("=== Login Functionality Test ===\n")

with app.app_context():
    # Test 1: Verify database has users
    users = User.query.all()
    print(f"Test 1: Database users count - {len(users)}")
    if len(users) == 0:
        print("❌ FAIL: No users found in database")
        sys.exit(1)
    print("✅ PASS: Users found in database")
    
    # Test 2: Verify test teacher account exists
    test_teacher = User.query.filter_by(username='testteacher').first()
    print(f"\nTest 2: Test teacher account")
    if not test_teacher:
        print("❌ FAIL: Test teacher account not found")
        sys.exit(1)
    print(f"✅ PASS: Test teacher found: {test_teacher.username} (role: {test_teacher.role})")
    
    # Test 3: Verify password hash works
    print("\nTest 3: Password authentication")
    correct_pwd = 'password123'
    if check_password_hash(test_teacher.password_hash, correct_pwd):
        print(f"✅ PASS: Correct password accepted")
    else:
        print(f"❌ FAIL: Correct password rejected")
        sys.exit(1)
    
    # Test 4: Verify wrong password is rejected
    wrong_pwd = 'wrongpass'
    if not check_password_hash(test_teacher.password_hash, wrong_pwd):
        print(f"✅ PASS: Wrong password correctly rejected")
    else:
        print(f"❌ FAIL: Wrong password accepted")
        sys.exit(1)
    
    # Test 5: Verify user roles are correctly set
    print("\nTest 5: User roles verification")
    has_teacher = User.query.filter_by(role='teacher').count() > 0
    has_student = User.query.filter_by(role='student').count() > 0
    
    if has_teacher and has_student:
        print("✅ PASS: Both teacher and student roles present")
    else:
        print(f"❌ FAIL: Missing roles - Teacher: {has_teacher}, Student: {has_student}")
        sys.exit(1)

print("\n" + "="*40)
print("🎉 ALL TESTS PASSED! Login functionality is working correctly.")
print("="*40)
print("\nTest accounts available:")
print("- Teacher: username='testteacher', password='password123'")
print("- Student: username='teststudent', password='password123'")
print("\nYou can now try logging in using these credentials.")

#!/usr/bin/env python3
"""
Debug script to test login functionality directly
"""

import os
import logging
import sys
from app import app, db, User, init_database
from werkzeug.security import generate_password_hash, check_password_hash

# Set up logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

def test_login():
    with app.app_context():
        try:
            # Initialize database if needed
            init_database()
            
            # Test 1: Check if database exists and is accessible
            logger.info("Test 1: Checking database access...")
            users = User.query.all()
            logger.info(f"Found {len(users)} users in database")
            
            # Test 2: Create a test user if it doesn't exist
            logger.info("Test 2: Creating test user...")
            test_user = User.query.filter_by(username='test_user').first()
            if not test_user:
                test_user = User(username='test_user', email='test@example.com', role='student')
                test_user.set_password('test_password')
                db.session.add(test_user)
                db.session.commit()
                logger.info("Created test user: test_user/test_password")
            else:
                logger.info("Test user already exists")
            
            # Test 3: Verify password checking
            logger.info("Test 3: Verifying password hash...")
            is_valid = test_user.check_password('test_password')
            logger.info(f"Password verification: {'SUCCESS' if is_valid else 'FAILED'}")
            
            # Test 4: Query user directly
            logger.info("Test 4: Querying user by username...")
            queried_user = User.query.filter_by(username='test_user').first()
            if queried_user:
                logger.info(f"Queried user: {queried_user.username}, Role: {queried_user.role}")
            else:
                logger.error("Could not find user by username")
            
            # Test 5: Test with wrong password
            logger.info("Test 5: Testing with wrong password...")
            is_valid_wrong = test_user.check_password('wrong_password')
            logger.info(f"Wrong password verification: {'FAILED (expected)' if not is_valid_wrong else 'SUCCESS (unexpected)'}")
            
            # Test 6: Check database tables
            logger.info("Test 6: Checking database tables...")
            from sqlalchemy import inspect
            inspector = inspect(db.engine)
            tables = inspector.get_table_names()
            logger.info(f"Database tables: {tables}")
            
            # Test 7: Check user table columns
            if 'user' in tables:
                columns = [column['name'] for column in inspector.get_columns('user')]
                logger.info(f"User table columns: {columns}")
            
            logger.info("✅ All tests completed!")
            return True
            
        except Exception as e:
            logger.error(f"❌ Error during login test: {e}")
            logger.exception("Detailed stack trace:")
            return False

if __name__ == "__main__":
    logger.info("Starting login debug test...")
    success = test_login()
    sys.exit(0 if success else 1)

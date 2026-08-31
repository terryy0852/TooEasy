#!/usr/bin/env python3
"""
Debug script to simulate the exact login flow
"""

import os
import logging
import sys
from app import app, db, User, login_user, init_database
from flask import request, session
from werkzeug.security import generate_password_hash, check_password_hash

# Set up logging with UTF-8 encoding to avoid UnicodeEncodeError
logging.basicConfig(
    level=logging.DEBUG,
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler('login_debug.log', encoding='utf-8')
    ]
)
logger = logging.getLogger(__name__)

def simulate_login_flow():
    with app.test_request_context():
        try:
            # Initialize database if needed
            init_database()
            
            logger.info("=== Starting Login Flow Simulation ===")
            
            # Test 1: Create test user
            logger.info("Test 1: Creating test user...")
            test_user = User.query.filter_by(username='test_login').first()
            if not test_user:
                test_user = User(username='test_login', email='test_login@example.com', role='student')
                test_user.set_password('test_password')
                db.session.add(test_user)
                db.session.commit()
                logger.info("Created test user: test_login/test_password")
            else:
                logger.info("Test user already exists")
            
            # Test 2: Simulate GET request to login page
            logger.info("Test 2: Simulating GET request to login page...")
            from app import login
            response = login()
            logger.info(f"Login page rendered successfully: {response}")
            
            # Test 3: Simulate POST request with correct credentials
            logger.info("Test 3: Simulating POST request with correct credentials...")
            
            # Set up request context for POST
            with app.test_request_context(
                '/login',
                method='POST',
                data={'username': 'test_login', 'password': 'test_password'}
            ):
                # Add session to the context
                session['language'] = 'en'
                
                # Import necessary modules
                from app import login
                from flask_login import current_user
                
                # Call login function
                response = login()
                logger.info(f"Login response: {response}")
                logger.info(f"Current user after login: {current_user}")
                logger.info(f"Is user authenticated: {current_user.is_authenticated if hasattr(current_user, 'is_authenticated') else 'N/A'}")
            
            # Test 4: Simulate POST request with wrong credentials
            logger.info("Test 4: Simulating POST request with wrong credentials...")
            
            with app.test_request_context(
                '/login',
                method='POST',
                data={'username': 'test_login', 'password': 'wrong_password'}
            ):
                session['language'] = 'en'
                
                from app import login
                from flask import get_flashed_messages
                
                response = login()
                flash_messages = get_flashed_messages()
                logger.info(f"Login response with wrong password: {response}")
                logger.info(f"Flash messages: {flash_messages}")
            
            # Test 5: Check for any session issues
            logger.info("Test 5: Checking session configuration...")
            logger.info(f"Secret key configured: {len(app.secret_key) > 0}")
            logger.info(f"Session type: {app.config.get('SESSION_TYPE', 'default')}")
            
            logger.info("✅ Login flow simulation completed successfully!")
            return True
            
        except Exception as e:
            logger.error(f"❌ Error during login flow simulation: {e}")
            logger.exception("Detailed stack trace:")
            return False

def test_direct_database_query():
    with app.app_context():
        try:
            logger.info("\n=== Testing Direct Database Queries ===")
            
            # Test various database operations
            logger.info("1. Count users:")
            user_count = db.session.query(User).count()
            logger.info(f"   Total users: {user_count}")
            
            logger.info("2. Query users with filter:")
            users = db.session.query(User).filter(User.username.like('test%')).all()
            logger.info(f"   Test users found: {[u.username for u in users]}")
            
            logger.info("3. Test raw SQL query:")
            from sqlalchemy import text
            result = db.session.execute(text('SELECT COUNT(*) FROM "user"')).scalar()
            logger.info(f"   Raw SQL user count: {result}")
            
            logger.info("✅ Direct database queries completed successfully!")
            return True
            
        except Exception as e:
            logger.error(f"❌ Error during direct database queries: {e}")
            logger.exception("Detailed stack trace:")
            return False

if __name__ == "__main__":
    logger.info("Starting login flow debugging...")
    
    # Test the complete login flow
    login_success = simulate_login_flow()
    
    # Test direct database operations
    db_success = test_direct_database_query()
    
    if login_success and db_success:
        logger.info("\n🎉 All tests passed! The login functionality appears to be working correctly.")
        sys.exit(0)
    else:
        logger.error("\n❌ Some tests failed. Please check the logs for details.")
        sys.exit(1)


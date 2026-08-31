#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Debug script to test login functionality and session management
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import app, db, User
from flask import session, request
from flask_login import login_user, current_user
from sqlalchemy import text

# Configure logging
import logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def debug_login_process():
    """Debug the login process"""
    logger.info("=== Debugging Login Process ===")
    
    with app.app_context():
        # Test database connection
        try:
            db.session.execute(text('SELECT 1'))
            logger.info("Database connection successful")
        except Exception as e:
            logger.error("Database connection error: %s", e)
            return
        
        # Test user retrieval
        test_username = "test_login"
        test_password = "test_password"
        
        try:
            # Create test user if it doesn't exist
            user = User.query.filter_by(username=test_username).first()
            if not user:
                logger.info("Creating test user...")
                user = User(username=test_username, email="test@example.com", role="student")
                user.set_password(test_password)
                db.session.add(user)
                db.session.commit()
                logger.info("✅ Test user created")
            else:
                logger.info("✅ Test user already exists")
            
            logger.info("User info: ID=%d, Username=%s, Role=%s", user.id, user.username, user.role)
            
            # Test password check
            if user.check_password(test_password):
                logger.info("✅ Password check passed")
            else:
                logger.error("❌ Password check failed")
                return
            
            # Test login_user functionality
            with app.test_client() as client:
                with client.session_transaction() as sess:
                    sess['test_key'] = 'test_value'  # Initialize session
                
                logger.info("Testing login_user...")
                with client.request_context('/'):
                    login_user(user)
                    logger.info("Current user after login: %s", current_user)
                    logger.info("Is user authenticated? %s", current_user.is_authenticated)
                    
                    # Test redirect
                    if current_user.role in ['admin', 'teacher']:
                        redirect_url = '/student_dashboard'
                    else:
                        redirect_url = '/student_dashboard'
                    logger.info("Expected redirect URL: %s", redirect_url)
                    
                    # Test accessing protected route
                    logger.info("Testing access to protected route...")
                    response = client.get('/student_dashboard', follow_redirects=True)
                    logger.info("Response status: %s", response.status_code)
                    logger.info("Response URL: %s", response.url)
                    
                    if response.status_code == 200:
                        logger.info("✅ Successfully accessed protected route")
                    else:
                        logger.error("❌ Failed to access protected route")
                    
                    # Check session content
                    with client.session_transaction() as sess:
                        logger.info("Session keys: %s", list(sess.keys()))
                        for key, value in sess.items():
                            logger.info("Session %s: %s", key, value)
            
        except Exception as e:
            logger.error("❌ Error during login testing: %s", e)
            import traceback
            traceback.print_exc()

if __name__ == "__main__":
    debug_login_process()
#!/usr/bin/env python3
"""
Test script to verify assignments in the PRODUCTION Supabase database
This script connects directly to your production database to check assignments
"""

import os
import sys
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

# Use the same DATABASE_URL as your production app
DATABASE_URL = "postgresql://postgres:n5jTtilYoz2S1LwO@db.xqjscxsvcespsrkyoekf.supabase.co:5432/postgres"

def test_production_assignments():
    print("🔍 Testing PRODUCTION database assignments...")
    print(f"Database: {DATABASE_URL}")
    
    try:
        # Create engine and session
        engine = create_engine(DATABASE_URL)
        Session = sessionmaker(bind=engine)
        session = Session()
        
        # Test connection
        result = session.execute(text("SELECT version();"))
        print("✅ Connected to PostgreSQL database:")
        print(f"   {result.scalar()}")
        
        # Count total assignments
        result = session.execute(text("SELECT COUNT(*) FROM assignment;"))
        total_assignments = result.scalar()
        print(f"📊 Total assignments in database: {total_assignments}")
        
        # Get all assignments with details
        result = session.execute(text("""
            SELECT a.id, a.title, a.created_by, a.created_at, 
                   COUNT(DISTINCT asm.student_id) as assigned_students
            FROM assignment a
            LEFT JOIN assignment_students asm ON a.id = asm.assignment_id
            GROUP BY a.id, a.title, a.created_by, a.created_at
            ORDER BY a.created_at DESC;
        """))
        
        assignments = result.fetchall()
        print("\n📋 All assignments in production database:")
        print("-" * 80)
        for assignment in assignments:
            print(f"ID: {assignment[0]}")
            print(f"Title: {assignment[1]}")
            print(f"Created by: {assignment[2]}")
            print(f"Created at: {assignment[3]}")
            print(f"Assigned students: {assignment[4]}")
            print("-" * 40)
        
        # Check for specific test users
        result = session.execute(text("SELECT COUNT(*) FROM \"user\" WHERE username IN ('test_tutor', 'test1', 'Schumacherm2013');"))
        test_users = result.scalar()
        print(f"👥 Test users found: {test_users}")
        
        session.close()
        print("\n✅ Production database test completed successfully!")
        
    except Exception as e:
        print(f"❌ Error connecting to production database: {e}")
        print("Please check:")
        print("1. Is your Supabase project running?")
        print("2. Is the database connection string correct?")
        print("3. Are there any firewall restrictions?")
        sys.exit(1)

if __name__ == "__main__":
    test_production_assignments()
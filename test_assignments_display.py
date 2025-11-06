#!/usr/bin/env python3
"""
Test script to verify assignments are being retrieved correctly from the database
and to check if there are any display issues in the tutor dashboard.
"""

from app import app, db, Assignment, User

def test_assignment_retrieval():
    """Test that assignments are being retrieved correctly from the database"""
    with app.app_context():
        # Get all assignments ordered by creation date
        assignments = Assignment.query.order_by(Assignment.created_at.desc()).all()
        
        print(f"Total assignments in database: {len(assignments)}")
        print("=" * 50)
        
        for i, assignment in enumerate(assignments):
            print(f"{i+1}. {assignment.title} (ID: {assignment.id})")
            print(f"   Created: {assignment.created_at}")
            print(f"   Tutor ID: {assignment.tutor_id}")
            print(f"   Description: {assignment.description[:100]}..." if len(assignment.description) > 100 else f"   Description: {assignment.description}")
            print(f"   File path: {assignment.file_path}")
            print(f"   Due date: {assignment.due_date}")
            print(f"   Number of submissions: {len(assignment.submissions)}")
            print(f"   Number of assigned students: {assignment.assigned_students.count()}")
            print("-" * 50)

def test_tutor_dashboard_query():
    """Test the exact query used in the tutor_dashboard route"""
    with app.app_context():
        # This is the exact query from tutor_dashboard route
        assignments = Assignment.query.order_by(Assignment.created_at.desc()).all()
        
        print(f"Tutor dashboard query results: {len(assignments)} assignments")
        print("=" * 50)
        
        for i, assignment in enumerate(assignments[:10]):  # Show first 10
            print(f"{i+1}. {assignment.title} (ID: {assignment.id}, Created: {assignment.created_at})")

def check_assignment_visibility():
    """Check if assignments might be hidden due to filtering or other issues"""
    with app.app_context():
        assignments = Assignment.query.order_by(Assignment.created_at.desc()).all()
        
        print("Checking assignment visibility issues:")
        print("=" * 50)
        
        # Check for assignments with no file paths
        no_file_assignments = [a for a in assignments if not a.file_path]
        print(f"Assignments without files: {len(no_file_assignments)}")
        
        # Check for assignments with no due dates
        no_due_date_assignments = [a for a in assignments if not a.due_date]
        print(f"Assignments without due dates: {len(no_due_date_assignments)}")
        
        # Check for assignments with no submissions
        no_submission_assignments = [a for a in assignments if len(a.submissions) == 0]
        print(f"Assignments with no submissions: {len(no_submission_assignments)}")
        
        # Check for assignments with no assigned students
        no_students_assignments = [a for a in assignments if a.assigned_students.count() == 0]
        print(f"Assignments with no assigned students: {len(no_students_assignments)}")

if __name__ == "__main__":
    print("Testing assignment retrieval and visibility...")
    print("=" * 60)
    
    test_assignment_retrieval()
    print("\n" + "=" * 60)
    
    test_tutor_dashboard_query()
    print("\n" + "=" * 60)
    
    check_assignment_visibility()
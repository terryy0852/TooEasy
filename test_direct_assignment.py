#!/usr/bin/env python3
"""
Direct test of student assignment functionality
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import app, db, User, Assignment

def test_direct_assignment():
    with app.app_context():
        print("=== Direct Test of Student Assignment Functionality ===\n")
        
        # Get test tutor
        tutor = User.query.filter_by(username='test_tutor').first()
        if not tutor:
            print("Test tutor not found")
            return False
        
        # Get students to assign
        students = User.query.filter_by(is_tutor=False).all()
        print(f"Available students: {[s.username for s in students]}")
        
        # Create a new assignment
        new_assignment = Assignment(
            title="Direct Test Assignment",
            description="Test assignment created directly",
            tutor_id=tutor.id
        )
        
        db.session.add(new_assignment)
        
        # Test the student assignment code that was previously broken
        assigned_student_ids = ['1', '3']  # IDs of test1 and Schumacherm2013
        
        print("\nTesting student assignment with IDs:", assigned_student_ids)
        
        try:
            ids = [int(sid) for sid in assigned_student_ids]
            selected_students = User.query.filter(User.id.in_(ids), User.is_tutor == False).all()
            
            print(f"Found {len(selected_students)} students to assign:")
            for s in selected_students:
                print(f"  - {s.username} (ID: {s.id})")
                new_assignment.assigned_students.append(s)
            
            print(f"Successfully assigned {len(selected_students)} students to assignment")
            
        except Exception as e:
            print(f"Error assigning students to assignment: {e}")
            # Don't fail the test, just show the error
        
        # Commit the changes
        db.session.commit()
        
        print("\n=== Verification ===")
        
        # Reload the assignment with relationships
        assignment = Assignment.query.get(new_assignment.id)
        assigned_students = assignment.assigned_students.all()
        
        print(f"Assignment created: {assignment.title}")
        print(f"Assigned students count: {len(assigned_students)}")
        
        if assigned_students:
            print("Assigned students:")
            for student in assigned_students:
                print(f"  - {student.username} (ID: {student.id})")
        else:
            print("No students assigned (this indicates the fix may not be working)")
        
        # Check the association table directly
        from sqlalchemy import text
        result = db.session.execute(text("SELECT * FROM assignment_students WHERE assignment_id = :id"), 
                                  {'id': assignment.id})
        relationships = result.fetchall()
        
        print(f"\nDirect database relationships: {len(relationships)}")
        for rel in relationships:
            print(f"  Assignment ID: {rel[0]}, Student ID: {rel[1]}")
        
        return len(assigned_students) > 0

if __name__ == "__main__":
    success = test_direct_assignment()
    
    if success:
        print("\n✓ Student assignment test PASSED")
    else:
        print("\n✗ Student assignment test FAILED")
        sys.exit(1)
#!/usr/bin/env python3
"""
Test script to verify student assignment functionality
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import app, db, User, Assignment

def test_student_assignment():
    with app.app_context():
        print("=== Testing Student Assignment Functionality ===\n")
        
        # Get all assignments
        assignments = Assignment.query.all()
        
        print(f"Total assignments in database: {len(assignments)}")
        print("\nAssignment details:")
        
        for i, assignment in enumerate(assignments, 1):
            print(f"\n{i}. Assignment: {assignment.title}")
            print(f"   ID: {assignment.id}")
            
            # Load tutor relationship
            tutor = User.query.get(assignment.tutor_id)
            print(f"   Created by: {tutor.username if tutor else 'Unknown'} (ID: {assignment.tutor_id})")
            
            # Load assigned students relationship
            assigned_students = assignment.assigned_students.all()
            print(f"   Assigned students count: {len(assigned_students)}")
            
            if assigned_students:
                print("   Assigned students:")
                for student in assigned_students:
                    print(f"     - {student.username} (ID: {student.id})")
            else:
                print("   No students assigned")
        
        # Check if any students exist
        students = User.query.filter_by(is_tutor=False).all()
        print(f"\nTotal students in database: {len(students)}")
        if students:
            print("Available students:")
            for student in students:
                print(f"  - {student.username} (ID: {student.id})")
        
        # Check assignment-student relationships
        print("\n=== Assignment-Student Relationships ===")
        from sqlalchemy import text
        
        # Check the assignment_students association table directly
        result = db.session.execute(text("SELECT * FROM assignment_students"))
        relationships = result.fetchall()
        
        print(f"Total assignment-student relationships: {len(relationships)}")
        for rel in relationships:
            print(f"  Assignment ID: {rel[0]}, Student ID: {rel[1]}")

if __name__ == "__main__":
    test_student_assignment()
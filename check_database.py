import sqlite3
import os

db_path = r'D:\OD\OneDrive\BaiduSyncdisk\Learn\Project Easy\Python Programs\Too Easy\instance\assignments.db'

print("=== Checking database contents ===")

if os.path.exists(db_path):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Check assignments
    cursor.execute("SELECT id, title, description FROM assignment")
    assignments = cursor.fetchall()
    print(f"Found {len(assignments)} assignments:")
    for assignment in assignments:
        print(f"  ID: {assignment[0]}, Title: {assignment[1]}, Description: {assignment[2][:50]}...")
    
    # Check submissions
    cursor.execute("SELECT id, assignment_id, student_id FROM submission")
    submissions = cursor.fetchall()
    print(f"\nFound {len(submissions)} submissions:")
    for submission in submissions:
        print(f"  ID: {submission[0]}, Assignment ID: {submission[1]}, Student ID: {submission[2]}")
    
    conn.close()
else:
    print("Database file not found!")
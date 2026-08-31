import sqlite3
import os

db_path = r'D:\OD\OneDrive\BaiduSyncdisk\Learn\Project Easy\Python Programs\Too Easy\instance\assignments.db'

print("=== Checking actual submission content ===")

if os.path.exists(db_path):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Get submission details
    cursor.execute("SELECT id, assignment_id, student_id, content, submitted_at FROM submission")
    submissions = cursor.fetchall()
    
    for submission in submissions:
        print(f"\nSubmission ID: {submission[0]}")
        print(f"Assignment ID: {submission[1]}")
        print(f"Student ID: {submission[2]}")
        print(f"Submitted at: {submission[4]}")
        print(f"Content length: {len(submission[3])} characters")
        print(f"Content preview (first 200 chars):")
        print(f"'{submission[3][:200]}...'")
        print("-" * 50)
    
    conn.close()
else:
    print("Database file not found!")
import sqlite3

# Check all submissions to see if any have actual student answers
def check_all_submissions():
    conn = sqlite3.connect('d:/OD/OneDrive/BaiduSyncdisk/Learn/Project Easy/Python Programs/Too Easy/instance/assignments.db')
    cursor = conn.cursor()
    
    # Get all submissions
    cursor.execute('SELECT id, student_id, assignment_id, submission_date FROM submission ORDER BY id')
    submissions = cursor.fetchall()
    
    print("=== ALL SUBMISSIONS ===")
    for submission in submissions:
        submission_id, student_id, assignment_id, submission_date = submission
        
        # Get the content
        cursor.execute('SELECT content FROM submission WHERE id = ?', (submission_id,))
        content = cursor.fetchone()[0]
        
        print(f"\nSubmission ID: {submission_id}")
        print(f"Student ID: {student_id}")
        print(f"Assignment ID: {assignment_id}")
        print(f"Submission Date: {submission_date}")
        print(f"Content Length: {len(content)} characters")
        
        # Quick check for filled form elements
        import re
        
        # Count filled vs empty textareas
        textarea_pattern = r'<textarea[^>]*>(.*?)</textarea>'
        textarea_matches = re.findall(textarea_pattern, content, re.IGNORECASE | re.DOTALL)
        
        filled_textareas = sum(1 for match in textarea_matches if match.strip())
        empty_textareas = sum(1 for match in textarea_matches if not match.strip())
        
        # Count filled vs empty inputs
        input_pattern = r'<input[^>]*value="([^"]*)"[^>]*>'
        input_matches = re.findall(input_pattern, content, re.IGNORECASE)
        
        filled_inputs = sum(1 for match in input_matches if match.strip())
        empty_inputs = sum(1 for match in input_matches if not match.strip())
        
        print(f"Textareas: {filled_textareas} filled, {empty_textareas} empty")
        print(f"Inputs: {filled_inputs} filled, {empty_inputs} empty")
        
        if filled_textareas > 0 or filled_inputs > 0:
            print("✅ This submission appears to have student answers!")
        else:
            print("❌ This submission appears to be empty/template")
    
    conn.close()

if __name__ == "__main__":
    check_all_submissions()
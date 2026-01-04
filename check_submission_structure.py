import sqlite3

# Check the submission table structure and all submissions
def check_submission_structure():
    conn = sqlite3.connect('d:/OD/OneDrive/BaiduSyncdisk/Learn/Project Easy/Python Programs/Too Easy/instance/assignments.db')
    cursor = conn.cursor()
    
    # Get table schema
    cursor.execute("PRAGMA table_info(submission)")
    columns = cursor.fetchall()
    
    print("=== SUBMISSION TABLE STRUCTURE ===")
    for col in columns:
        print(f"Column: {col[1]} (Type: {col[2]})")
    
    # Get all submissions
    cursor.execute('SELECT * FROM submission ORDER BY id')
    submissions = cursor.fetchall()
    
    print(f"\n=== ALL SUBMISSIONS ({len(submissions)} total) ===")
    for submission in submissions:
        print(f"\nSubmission: {submission}")
        
        # Get content for analysis
        submission_id = submission[0]
        cursor.execute('SELECT content FROM submission WHERE id = ?', (submission_id,))
        content = cursor.fetchone()[0]
        
        print(f"Content length: {len(content)} characters")
        
        # Quick analysis
        import re
        
        # Count filled vs empty textareas
        textarea_pattern = r'<textarea[^>]*>(.*?)</textarea>'
        textarea_matches = re.findall(textarea_pattern, content, re.IGNORECASE | re.DOTALL)
        
        filled_textareas = sum(1 for match in textarea_matches if match.strip())
        empty_textareas = sum(1 for match in textarea_matches if not match.strip())
        
        print(f"Textareas: {filled_textareas} filled, {empty_textareas} empty")
        
        if filled_textareas > 0:
            print("✅ This submission has filled textareas!")
            # Show first filled textarea
            for match in textarea_matches:
                if match.strip():
                    print(f"Sample content: '{match.strip()[:100]}...'")
                    break
        else:
            print("❌ This submission appears to be empty/template")
    
    conn.close()

if __name__ == "__main__":
    check_submission_structure()
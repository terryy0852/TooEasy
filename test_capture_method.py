import sqlite3
import re

# Test the current submission capture method vs what it should be
def test_submission_capture():
    conn = sqlite3.connect('d:/OD/OneDrive/BaiduSyncdisk/Learn/Project Easy/Python Programs/Too Easy/instance/assignments.db')
    cursor = conn.cursor()
    
    # Get the assignment content (what the student sees)
    cursor.execute('SELECT html_content FROM assignment WHERE id = 1')
    assignment_content = cursor.fetchone()[0]
    
    # Get the submission content (what was captured)
    cursor.execute('SELECT content FROM submission WHERE id = 1')
    submission_content = cursor.fetchone()[0]
    
    print("=== SUBMISSION CAPTURE ANALYSIS ===")
    print(f"Assignment content length: {len(assignment_content)}")
    print(f"Submission content length: {len(submission_content)}")
    
    # Look for form elements in the assignment
    textarea_pattern = r'<textarea[^>]*id="([^"]*)"[^>]*>([^<]*)</textarea>'
    assignment_textareas = re.findall(textarea_pattern, assignment_content, re.IGNORECASE)
    
    print(f"\n=== ASSIGNMENT TEXTAREAS ===")
    for textarea_id, default_content in assignment_textareas:
        print(f"ID: {textarea_id}")
        print(f"Default content: '{default_content.strip()}'")
    
    # Look for form elements in the submission
    submission_textareas = re.findall(textarea_pattern, submission_content, re.IGNORECASE)
    
    print(f"\n=== SUBMISSION TEXTAREAS ===")
    for textarea_id, submitted_content in submission_textareas:
        print(f"ID: {textarea_id}")
        print(f"Submitted content: '{submitted_content.strip()}'")
    
    # Check if they're identical (indicating no capture of user input)
    if assignment_content == submission_content:
        print(f"\n❌ PROBLEM IDENTIFIED:")
        print("Assignment and submission content are identical!")
        print("This means the JavaScript capture method is not working properly.")
        print("The outerHTML method doesn't capture form input values.")
    else:
        print(f"\n✅ Content differs - some user input may have been captured")
    
    conn.close()

if __name__ == "__main__":
    test_submission_capture()
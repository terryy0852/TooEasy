import sqlite3
import difflib

# Compare assignment vs submission to see what changed
def compare_assignment_vs_submission():
    conn = sqlite3.connect('d:/OD/OneDrive/BaiduSyncdisk/Learn/Project Easy/Python Programs/Too Easy/instance/assignments.db')
    cursor = conn.cursor()
    
    # Get the assignment content (what the student sees)
    cursor.execute('SELECT html_content FROM assignment WHERE id = 1')
    assignment_content = cursor.fetchone()[0]
    
    # Get the submission content (what was captured)
    cursor.execute('SELECT content FROM submission WHERE id = 1')
    submission_content = cursor.fetchone()[0]
    
    print("=== DETAILED COMPARISON ===")
    print(f"Assignment length: {len(assignment_content)}")
    print(f"Submission length: {len(submission_content)}")
    
    # Show differences
    diff = difflib.unified_diff(
        assignment_content.splitlines(),
        submission_content.splitlines(),
        fromfile='assignment',
        tofile='submission',
        lineterm=''
    )
    
    print("\n=== DIFFERENCES ===")
    diff_lines = list(diff)
    if diff_lines:
        for line in diff_lines[:50]:  # Show first 50 lines of diff
            print(line)
    else:
        print("No differences found")
    
    # Check if submission has any filled form values
    import re
    
    # Look for value attributes that might contain student input
    value_pattern = r'<input[^>]*value="([^"]*)"[^>]*>'
    input_values = re.findall(value_pattern, submission_content, re.IGNORECASE)
    
    if input_values:
        print(f"\n=== INPUT VALUES FOUND ===")
        for value in input_values:
            if value.strip():
                print(f"Filled input value: '{value}'")
    else:
        print(f"\n=== NO INPUT VALUES FOUND ===")
    
    # Look for textarea content that might not be captured by regex
    textarea_pattern = r'<textarea[^>]*>(.*?)</textarea>'
    textarea_matches = re.findall(textarea_pattern, submission_content, re.IGNORECASE | re.DOTALL)
    
    filled_textareas = [match.strip() for match in textarea_matches if match.strip()]
    if filled_textareas:
        print(f"\n=== FILLED TEXTAREAS FOUND ===")
        for i, content in enumerate(filled_textareas[:5]):  # Show first 5
            print(f"Textarea {i+1}: '{content[:100]}{'...' if len(content) > 100 else ''}'")
    else:
        print(f"\n=== NO FILLED TEXTAREAS FOUND ===")
    
    conn.close()

if __name__ == "__main__":
    compare_assignment_vs_submission()
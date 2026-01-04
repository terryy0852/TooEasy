import sqlite3
import json

# Check if the submission content contains actual student answers
def analyze_submission_content():
    conn = sqlite3.connect('d:/OD/OneDrive/BaiduSyncdisk/Learn/Project Easy/Python Programs/Too Easy/instance/assignments.db')
    cursor = conn.cursor()
    
    # Get the submission content
    cursor.execute('SELECT id, content FROM submission WHERE id = 1')
    result = cursor.fetchone()
    
    if result:
        submission_id, content = result
        print(f"Submission ID: {submission_id}")
        print(f"Content length: {len(content)} characters")
        
        # Look for common form input patterns that would indicate filled answers
        patterns_to_check = [
            ('input fields', r'<input[^>]*value="([^"]*)"'),
            ('textarea content', r'<textarea[^>]*>([^<]*)</textarea>'),
            ('select options', r'<option[^>]*selected[^>]*>([^<]*)</option>'),
            ('text content changes', r'>([^<]{10,})<'),  # Look for longer text content
        ]
        
        import re
        
        print("\n=== Analyzing submission content for student answers ===")
        
        for pattern_name, pattern in patterns_to_check:
            matches = re.findall(pattern, content, re.IGNORECASE | re.DOTALL)
            if matches:
                print(f"\n✅ Found {len(matches)} {pattern_name}:")
                for i, match in enumerate(matches[:5]):  # Show first 5 matches
                    clean_match = match.strip() if isinstance(match, str) else str(match)
                    if len(clean_match) > 0:
                        print(f"  {i+1}: '{clean_match[:100]}{'...' if len(clean_match) > 100 else ''}'")
            else:
                print(f"❌ No {pattern_name} found")
        
        # Check for specific Chinese text that might indicate student answers
        chinese_patterns = [
            '學生回答', '学生回答', '答案', '回答', '解答',
            '選擇', '选择', '填寫', '填写', '完成'
        ]
        
        print(f"\n=== Checking for Chinese answer indicators ===")
        for pattern in chinese_patterns:
            if pattern in content:
                print(f"✅ Found '{pattern}' in content")
                # Show context around the pattern
                index = content.find(pattern)
                start = max(0, index - 50)
                end = min(len(content), index + 50)
                context = content[start:end]
                print(f"  Context: '{context}'")
        
        # Look for any non-template content
        print(f"\n=== Checking for student-specific content ===")
        
        # Common template markers that should NOT be in student submissions
        template_markers = [
            'placeholder=', 'value=""', 'selected>', 'checked>'
        ]
        
        student_content_found = False
        for marker in template_markers:
            if marker in content:
                print(f"⚠️  Found template marker '{marker}' - might indicate empty form")
            else:
                print(f"✅ No template marker '{marker}' - form might be filled")
        
        # Check for actual text content (not just HTML structure)
        text_content = re.sub(r'<[^>]+>', '', content)
        text_content = re.sub(r'\s+', ' ', text_content).strip()
        
        if len(text_content) > 1000:  # If there's substantial text content
            print(f"✅ Found substantial text content ({len(text_content)} characters)")
            print(f"Sample text: '{text_content[:200]}...'")
        else:
            print(f"❌ Limited text content found ({len(text_content)} characters)")
        
    else:
        print("No submission found")
    
    conn.close()

if __name__ == "__main__":
    analyze_submission_content()
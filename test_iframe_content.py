import sqlite3
import html

# Check what's actually in the submission content
def check_submission_content():
    conn = sqlite3.connect('d:/OD/OneDrive/BaiduSyncdisk/Learn/Project Easy/Python Programs/Too Easy/instance/assignments.db')
    cursor = conn.cursor()
    
    cursor.execute('SELECT id, content FROM submission WHERE id = 1')
    result = cursor.fetchone()
    
    if result:
        submission_id, content = result
        print(f"Submission ID: {submission_id}")
        print(f"Content length: {len(content)} characters")
        print(f"Content type: {type(content)}")
        
        # Check if content contains actual student answers
        if '學生回答' in content or 'student answer' in content.lower():
            print("✅ Found student answer markers in content")
        else:
            print("❌ No student answer markers found")
            
        # Look for form fields or input areas
        if 'input' in content.lower() or 'textarea' in content.lower():
            print("✅ Found form input elements")
        else:
            print("❌ No form input elements found")
            
        # Check for filled-in values
        if 'value=' in content:
            print("✅ Found filled-in values")
            # Extract some sample values
            import re
            values = re.findall(r'value="([^"]*)"', content)
            if values:
                print(f"Sample filled values: {values[:3]}")
        else:
            print("❌ No filled-in values found")
            
        # Show first 1000 characters to see the structure
        print("\nFirst 1000 characters of content:")
        print("-" * 50)
        print(content[:1000])
        print("-" * 50)
        
        # Show last 1000 characters to see the end
        print("\nLast 1000 characters of content:")
        print("-" * 50)
        print(content[-1000:])
        print("-" * 50)
        
    else:
        print("No submission found")
    
    conn.close()

if __name__ == "__main__":
    check_submission_content()
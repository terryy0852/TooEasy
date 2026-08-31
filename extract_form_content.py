import sqlite3
import re

# Extract and analyze the actual form content from the submission
def extract_form_content():
    conn = sqlite3.connect('d:/OD/OneDrive/BaiduSyncdisk/Learn/Project Easy/Python Programs/Too Easy/instance/assignments.db')
    cursor = conn.cursor()
    
    # Get the submission content
    cursor.execute('SELECT id, content FROM submission WHERE id = 1')
    result = cursor.fetchone()
    
    if result:
        submission_id, content = result
        
        print(f"=== EXTRACTING FORM CONTENT FROM SUBMISSION ===")
        print(f"Submission ID: {submission_id}")
        print(f"Total content length: {len(content)} characters")
        
        # Look for form elements and their content
        form_patterns = {
            'textareas': r'<textarea[^>]*id="([^"]*)"[^>]*>([^<]*)</textarea>',
            'inputs': r'<input[^>]*id="([^"]*)"[^>]*value="([^"]*)"[^>]*>',
            'selects': r'<select[^>]*id="([^"]*)"[^>]*>(.*?)</select>',
        }
        
        for element_type, pattern in form_patterns.items():
            matches = re.findall(pattern, content, re.IGNORECASE | re.DOTALL)
            if matches:
                print(f"\n=== {element_type.upper()} FOUND ===")
                for match in matches[:10]:  # Show first 10 matches
                    if len(match) >= 2:
                        element_id = match[0]
                        element_value = match[1].strip() if match[1] else ""
                        print(f"ID: {element_id}")
                        print(f"Value: '{element_value}'")
                        print(f"Length: {len(element_value)} characters")
                        if element_value:
                            print(f"✅ Has content!")
                        else:
                            print(f"❌ Empty")
                        print("---")
            else:
                print(f"No {element_type} found")
        
        # Look for any filled content in textareas specifically
        textarea_pattern = r'<textarea[^>]*>(.*?)</textarea>'
        textarea_matches = re.findall(textarea_pattern, content, re.IGNORECASE | re.DOTALL)
        
        if textarea_matches:
            print(f"\n=== TEXTAREA CONTENT ANALYSIS ===")
            filled_textareas = 0
            empty_textareas = 0
            
            for i, content in enumerate(textarea_matches):
                clean_content = content.strip()
                if clean_content:
                    filled_textareas += 1
                    print(f"Textarea {i+1}: ✅ FILLED")
                    print(f"  Content: '{clean_content[:100]}{'...' if len(clean_content) > 100 else ''}'")
                else:
                    empty_textareas += 1
                    print(f"Textarea {i+1}: ❌ EMPTY")
            
            print(f"\nSummary: {filled_textareas} filled, {empty_textareas} empty")
        
        # Check if this looks like the original template vs filled submission
        print(f"\n=== TEMPLATE vs SUBMISSION ANALYSIS ===")
        
        # Look for placeholder text that should be replaced
        placeholder_pattern = r'placeholder="([^"]*)"'
        placeholders = re.findall(placeholder_pattern, content)
        if placeholders:
            print(f"Found {len(placeholders)} placeholders:")
            for placeholder in placeholders[:5]:
                print(f"  - '{placeholder}'")
        
        # Look for empty value attributes
        empty_values = re.findall(r'value=""', content)
        if empty_values:
            print(f"Found {len(empty_values)} empty value attributes")
        
        # Extract a sample of the content to see the structure
        print(f"\n=== CONTENT SAMPLE ===")
        # Find the first form element and show context
        first_form = re.search(r'<(textarea|input|select)[^>]*>', content, re.IGNORECASE)
        if first_form:
            start = max(0, first_form.start() - 200)
            end = min(len(content), first_form.end() + 200)
            sample = content[start:end]
            print("Sample around first form element:")
            print(sample)
    
    conn.close()

if __name__ == "__main__":
    extract_form_content()
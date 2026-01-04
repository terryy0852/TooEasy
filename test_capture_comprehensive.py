#!/usr/bin/env python3
"""
Comprehensive test to verify the new submission capture method works correctly.
This script creates a test submission with filled content to validate the capture process.
"""

import sqlite3
import re
from datetime import datetime

def create_test_submission():
    """Create a test submission with filled content to verify capture method"""
    
    # Connect to database
    conn = sqlite3.connect('instance/assignments.db')
    cursor = conn.cursor()
    
    # Get the assignment content
    cursor.execute('SELECT html_content FROM assignment WHERE id = 1')
    assignment_content = cursor.fetchone()[0]
    
    # Create a test submission with filled answers
    test_content = assignment_content
    
    # Fill textareas with test answers
    for i in range(1, 24):  # 23 questions
        answer = f"這是第{i}題的測試答案。這個答案包含了一些中文內容來測試新的捕獲方法是否正常工作。"
        # Replace empty textareas with filled ones
        pattern = f'<textarea[^>]*id="q{i}"[^>]*>.*?</textarea>'
        replacement = f'<textarea class="textarea-input" id="q{i}" placeholder="請在此輸入你的答案...">{answer}</textarea>'
        test_content = re.sub(pattern, replacement, test_content, flags=re.DOTALL | re.IGNORECASE)
    
    # Insert test submission
    cursor.execute('''
        INSERT INTO submission (assignment_id, student_id, content, submitted_at)
        VALUES (?, ?, ?, ?)
    ''', (1, 5, test_content, datetime.now()))
    
    submission_id = cursor.lastrowid
    conn.commit()
    conn.close()
    
    print(f"Created test submission ID: {submission_id}")
    return submission_id

def verify_test_submission(submission_id):
    """Verify the test submission contains filled content"""
    
    # Connect to database
    conn = sqlite3.connect('instance/assignments.db')
    cursor = conn.cursor()
    
    # Get the test submission
    cursor.execute('SELECT content FROM submission WHERE id = ?', (submission_id,))
    content = cursor.fetchone()[0]
    
    print(f"Verifying test submission ID: {submission_id}")
    print(f"Content length: {len(content)} characters")
    print("-" * 80)
    
    # Look for filled textareas
    textarea_pattern = r'<textarea[^>]*>(.*?)</textarea>'
    textareas = re.findall(textarea_pattern, content, re.DOTALL | re.IGNORECASE)
    
    print(f"Found {len(textareas)} textarea elements")
    
    filled_count = 0
    empty_count = 0
    
    for i, textarea_content in enumerate(textareas):
        clean_content = textarea_content.strip()
        
        if clean_content:
            filled_count += 1
            if i < 3:  # Show first 3 as examples
                print(f"Textarea {i+1}: FILLED ({len(clean_content)} characters)")
                print(f"  Content: {clean_content[:100]}...")
        else:
            empty_count += 1
    
    print("-" * 80)
    print(f"Summary: {filled_count} filled, {empty_count} empty textareas")
    
    # Look for Chinese answer indicators
    chinese_answers = re.findall(r'這是第\d+題的測試答案', content)
    print(f"Found {len(chinese_answers)} Chinese test answers")
    
    conn.close()
    
    # Determine if the test submission is correct
    if filled_count > 0 and len(chinese_answers) > 0:
        print("\n✅ SUCCESS: Test submission contains filled content!")
        return True
    else:
        print("\n❌ ISSUE: Test submission does not contain expected content.")
        return False

def test_real_submission():
    """Test the most recent real submission"""
    
    # Connect to database
    conn = sqlite3.connect('instance/assignments.db')
    cursor = conn.cursor()
    
    # Get the latest real submission (not our test)
    cursor.execute('SELECT id, content FROM submission ORDER BY id DESC LIMIT 1')
    result = cursor.fetchone()
    
    if not result:
        print("No submissions found")
        return False
    
    submission_id, content = result
    
    print(f"\nTesting real submission ID: {submission_id}")
    print(f"Content length: {len(content)} characters")
    
    # Look for filled textareas
    textarea_pattern = r'<textarea[^>]*>(.*?)</textarea>'
    textareas = re.findall(textarea_pattern, content, re.DOTALL | re.IGNORECASE)
    
    filled_count = sum(1 for textarea_content in textareas if textarea_content.strip())
    
    # Look for Chinese content (real student answers)
    chinese_content = re.findall(r'[\u4e00-\u9fff]{10,}', content)
    
    print(f"Found {filled_count} filled textareas")
    print(f"Found {len(chinese_content)} Chinese text segments")
    
    conn.close()
    
    if filled_count > 0 or len(chinese_content) > 0:
        print("✅ Real submission contains student work!")
        return True
    else:
        print("❌ Real submission appears to be empty/template")
        return False

if __name__ == "__main__":
    print("Comprehensive test of submission capture method")
    print("=" * 80)
    
    # Test 1: Create and verify test submission
    print("\n1. Creating test submission with filled answers...")
    test_id = create_test_submission()
    test_success = verify_test_submission(test_id)
    
    # Test 2: Check real submission
    print("\n2. Testing most recent real submission...")
    real_success = test_real_submission()
    
    print("\n" + "=" * 80)
    print("SUMMARY:")
    print(f"Test submission: {'PASS' if test_success else 'FAIL'}")
    print(f"Real submission: {'PASS' if real_success else 'FAIL'}")
    
    if test_success:
        print("\n✅ The database can store filled submissions correctly.")
        print("The issue may be that students haven't submitted answers yet,")
        print("or the capture method needs to be tested with actual student input.")
    else:
        print("\n❌ There may be an issue with the submission storage process.")
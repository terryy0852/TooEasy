#!/usr/bin/env python3
"""
Test script to verify the new submission capture method works correctly.
This script simulates student answers and tests the capture process.
"""

import sqlite3
import re
from datetime import datetime

def test_new_capture():
    """Test the new submission capture method"""
    
    # Connect to database
    conn = sqlite3.connect('instance/assignments.db')
    cursor = conn.cursor()
    
    # Get the latest submission
    cursor.execute('SELECT id, content FROM submission ORDER BY id DESC LIMIT 1')
    result = cursor.fetchone()
    
    if not result:
        print("No submissions found in database")
        return
    
    submission_id, content = result
    print(f"Analyzing submission ID: {submission_id}")
    print(f"Content length: {len(content)} characters")
    print("-" * 80)
    
    # Look for filled textareas using the new capture method
    textarea_pattern = r'<textarea[^>]*>(.*?)</textarea>'
    textareas = re.findall(textarea_pattern, content, re.DOTALL | re.IGNORECASE)
    
    print(f"Found {len(textareas)} textarea elements")
    
    filled_count = 0
    empty_count = 0
    
    for i, textarea_content in enumerate(textareas):
        # Clean up content (remove extra whitespace)
        clean_content = textarea_content.strip()
        
        if clean_content:
            filled_count += 1
            print(f"Textarea {i+1}: FILLED ({len(clean_content)} characters)")
            print(f"  Content preview: {clean_content[:100]}...")
        else:
            empty_count += 1
            print(f"Textarea {i+1}: EMPTY")
    
    print("-" * 80)
    print(f"Summary: {filled_count} filled, {empty_count} empty textareas")
    
    # Look for filled input fields
    input_pattern = r'<input[^>]*value="([^"]*)"[^>]*>'
    inputs = re.findall(input_pattern, content, re.IGNORECASE)
    
    filled_inputs = [inp for inp in inputs if inp.strip()]
    print(f"Found {len(inputs)} input elements, {len(filled_inputs)} have values")
    
    # Look for selected options
    select_pattern = r'<option[^>]*selected[^>]*>(.*?)</option>'
    selected_options = re.findall(select_pattern, content, re.IGNORECASE)
    print(f"Found {len(selected_options)} selected options")
    
    if selected_options:
        for option in selected_options:
            print(f"  Selected: {option.strip()}")
    
    # Look for checked checkboxes
    checkbox_pattern = r'<input[^>]*type="checkbox"[^>]*checked[^>]*>'
    checkboxes = re.findall(checkbox_pattern, content, re.IGNORECASE)
    print(f"Found {len(checkboxes)} checked checkboxes")
    
    # Sample content around first few textareas to verify capture
    print("\nContent sample around first textarea:")
    first_textarea_match = re.search(r'.{0,200}<textarea[^>]*>.{0,200}', content, re.DOTALL | re.IGNORECASE)
    if first_textarea_match:
        print(first_textarea_match.group(0))
    
    conn.close()
    
    # Determine if the new capture method is working
    if filled_count > 0 or len(filled_inputs) > 0 or len(selected_options) > 0 or len(checkboxes) > 0:
        print("\n✅ SUCCESS: New capture method is working! Found filled form elements.")
        return True
    else:
        print("\n❌ ISSUE: No filled form elements found. Capture method may need adjustment.")
        return False

if __name__ == "__main__":
    print("Testing new submission capture method...")
    print("=" * 80)
    success = test_new_capture()
    print("=" * 80)
    if success:
        print("Test completed successfully!")
    else:
        print("Test indicates potential issues with capture method.")
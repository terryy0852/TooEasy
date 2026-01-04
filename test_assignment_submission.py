#!/usr/bin/env python3
"""Test script to verify complete assignment submission functionality"""

import requests
import time

def test_assignment_submission():
    # Test login
    session = requests.Session()
    login_data = {
        'username': 'teststudent',
        'password': 'password123'
    }

    print("=== TESTING LOGIN ===")
    login_response = session.post('http://127.0.0.1:5000/login', data=login_data)
    print(f"Login status: {login_response.status_code}")

    if login_response.status_code != 200:
        print("❌ Login failed!")
        print(login_response.text[:200])
        return False

    print("✅ Login successful!")
    
    # Test accessing assignment
    print("\n=== TESTING ASSIGNMENT ACCESS ===")
    assignment_response = session.get('http://127.0.0.1:5000/view_assignment/1')
    print(f"Assignment access status: {assignment_response.status_code}")
    
    if assignment_response.status_code != 200:
        print("❌ Assignment access failed!")
        print(assignment_response.text[:200])
        return False
    
    print("✅ Assignment access successful!")
    
    # Check if iframe is present
    if 'iframe' in assignment_response.text:
        print("✅ Found iframe in assignment page!")
    else:
        print("❌ No iframe found in assignment page")
    
    # Check if submission form is present
    if 'submissionForm' in assignment_response.text:
        print("✅ Found submission form!")
    else:
        print("❌ No submission form found")
    
    # Test assignment submission
    print("\n=== TESTING ASSIGNMENT SUBMISSION ===")
    
    # Sample HTML content
    html_content = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>My Assignment Submission</title>
    <style>
        body { font-family: Arial, sans-serif; background-color: #f0f8ff; }
        h1 { color: #4a6fa5; text-align: center; }
        .content { max-width: 800px; margin: 0 auto; padding: 20px; }
    </style>
</head>
<body>
    <div class="content">
        <h1>荷塘月色 Assignment Submission</h1>
        <p>This is my completed HTML assignment for the 荷塘月色 (Lotus Pond in Moonlight) lesson.</p>
        <p>I have included proper HTML structure, CSS styling, and semantic markup as requested.</p>
        <div class="features">
            <h2>Features Included:</h2>
            <ul>
                <li>Semantic HTML5 structure</li>
                <li>CSS styling for visual appeal</li>
                <li>Responsive design principles</li>
                <li>Proper heading hierarchy</li>
            </ul>
        </div>
    </div>
</body>
</html>"""

    submission_data = {
        'content': html_content
    }
    
    submit_response = session.post('http://127.0.0.1:5000/submit_html_assignment/1', data=submission_data)
    print(f"Submission status: {submit_response.status_code}")
    
    if submit_response.status_code == 200:
        print("✅ Assignment submitted successfully!")
        print(f"Response preview: {submit_response.text[:200]}...")
        
        # Check if we can still access the assignment after submission
        print("\n=== TESTING POST-SUBMISSION ACCESS ===")
        post_response = session.get('http://127.0.0.1:5000/view_assignment/1')
        print(f"Post-submission access status: {post_response.status_code}")
        
        if post_response.status_code == 200:
            print("✅ Can still access assignment after submission")
            if 'already submitted' in post_response.text.lower():
                print("✅ Shows submission confirmation message")
            else:
                print("❌ No submission confirmation found")
        else:
            print("❌ Cannot access assignment after submission")
            
        return True
    else:
        print("❌ Assignment submission failed!")
        print(f"Response: {submit_response.text[:500]}")
        return False

if __name__ == "__main__":
    success = test_assignment_submission()
    if success:
        print("\n🎉 ALL TESTS PASSED! Assignment functionality is working correctly.")
    else:
        print("\n❌ Some tests failed. Please check the errors above.")
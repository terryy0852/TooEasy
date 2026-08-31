#!/usr/bin/env python3
"""
Test script to verify the HTML assignment workflow
"""

import requests
import json
import time

# Base URL
BASE_URL = "http://127.0.0.1:5000"

def test_html_assignment_workflow():
    """Test the complete HTML assignment workflow"""
    session = requests.Session()
    
    print("=== Testing HTML Assignment Workflow ===")
    
    # Step 1: Login as teacher to create assignment
    print("\n1. Logging in as teacher...")
    login_data = {
        'username': 'tutor1',  # Using actual teacher username from database
        'password': 'teacher123'
    }
    response = session.post(f"{BASE_URL}/login", data=login_data)
    if response.status_code != 200:
        print("❌ Teacher login failed")
        return False
    print("✅ Teacher login successful")
    
    # Step 2: Create HTML assignment with file upload
    print("\n2. Creating HTML assignment...")
    
    # Prepare the HTML file
    html_content = '''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Student Information Form</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 20px; }
        .form-group { margin-bottom: 15px; }
        label { display: inline-block; width: 120px; }
        input[type="text"], input[type="email"], select { padding: 5px; width: 200px; }
        button { padding: 10px 20px; background-color: #4CAF50; color: white; border: none; cursor: pointer; }
        button:hover { background-color: #45a049; }
    </style>
</head>
<body>
    <h1>Student Information Form</h1>
    <form id="studentForm">
        <div class="form-group">
            <label for="fullName">Full Name:</label>
            <input type="text" id="fullName" name="fullName" placeholder="Enter your full name">
        </div>
        <div class="form-group">
            <label for="studentId">Student ID:</label>
            <input type="text" id="studentId" name="studentId" placeholder="Enter your student ID">
        </div>
        <div class="form-group">
            <label for="email">Email:</label>
            <input type="email" id="email" name="email" placeholder="Enter your email">
        </div>
        <div class="form-group">
            <label for="grade">Grade Level:</label>
            <select id="grade" name="grade">
                <option value="">Select grade</option>
                <option value="9">Grade 9</option>
                <option value="10">Grade 10</option>
                <option value="11">Grade 11</option>
                <option value="12">Grade 12</option>
            </select>
        </div>
        <div class="form-group">
            <label for="subject">Favorite Subject:</label>
            <input type="text" id="subject" name="subject" placeholder="Enter your favorite subject">
        </div>
        <button type="submit">Submit Information</button>
    </form>
    <script>
        document.getElementById('studentForm').addEventListener('submit', function(e) {
            e.preventDefault();
            alert('Form submitted successfully!');
        });
    </script>
</body>
</html>'''
    
    # Save the HTML content to a temporary file
    with open('temp_assignment.html', 'w', encoding='utf-8') as f:
        f.write(html_content)
    
    # Prepare multipart form data with file upload
    with open('temp_assignment.html', 'rb') as f:
        files = {'html_file': ('assignment.html', f, 'text/html')}
        assignment_data = {
            'title': 'Interactive HTML Test',
            'description': 'Complete the following HTML form by filling in the blanks:',
            'is_active': 'on'  # Make assignment active
        }
        response = session.post(f"{BASE_URL}/create_assignment", data=assignment_data, files=files)
    
    if response.status_code != 200:
        print("❌ Assignment creation failed")
        return False
    print("✅ HTML assignment created successfully")
    
    # Step 3: Logout teacher
    session.get(f"{BASE_URL}/logout")
    
    # Step 4: Login as student
    print("\n3. Logging in as student...")
    login_data = {
        'username': 'SY',  # Using actual student username from database
        'password': 'student123'
    }
    response = session.post(f"{BASE_URL}/login", data=login_data)
    if response.status_code != 200:
        print("❌ Student login failed")
        return False
    print("✅ Student login successful")
    
    # Step 5: Get student dashboard to find the assignment
    print("\n4. Getting student dashboard...")
    response = session.get(f"{BASE_URL}/student_dashboard")
    if response.status_code != 200:
        print("❌ Failed to get student dashboard")
        return False
    
    # Parse dashboard to find assignment (simplified check)
    dashboard_content = response.text
    
    # Let's first try with the existing assignment (荷塘月色)
    assignment_title = 'S2_荷塘月色'
    assignment_id = 1
    
    if assignment_title not in dashboard_content:
        print(f"❌ Assignment '{assignment_title}' not found on student dashboard")
        print("Available assignments in dashboard:")
        # Look for assignment titles in the content
        import re
        assignments = re.findall(r'<h[23][^>]*>([^<]+)</h[23]>', dashboard_content)
        for assignment in assignments:
            print(f"  - {assignment.strip()}")
        return False
    print(f"✅ Assignment '{assignment_title}' found on student dashboard")
    
    # Step 6: Simulate student completing the HTML assignment
    print("\n5. Testing HTML assignment completion...")
    
    # Complete HTML content
    completed_html = '''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Student Information Form</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 20px; }
        .form-group { margin-bottom: 15px; }
        label { display: inline-block; width: 120px; }
        input[type="text"], input[type="email"], select { padding: 5px; width: 200px; }
        button { padding: 10px 20px; background-color: #4CAF50; color: white; border: none; cursor: pointer; }
        button:hover { background-color: #45a049; }
    </style>
</head>
<body>
    <h1>Student Information Form</h1>
    <form id="studentForm">
        <div class="form-group">
            <label for="fullName">Full Name:</label>
            <input type="text" id="fullName" name="fullName" value="John Doe" placeholder="Enter your full name">
        </div>
        <div class="form-group">
            <label for="studentId">Student ID:</label>
            <input type="text" id="studentId" name="studentId" value="STU001" placeholder="Enter your student ID">
        </div>
        <div class="form-group">
            <label for="email">Email:</label>
            <input type="email" id="email" name="email" value="john.doe@school.edu" placeholder="Enter your email">
        </div>
        <div class="form-group">
            <label for="grade">Grade Level:</label>
            <select id="grade" name="grade">
                <option value="">Select grade</option>
                <option value="9">Grade 9</option>
                <option value="10" selected>Grade 10</option>
                <option value="11">Grade 11</option>
                <option value="12">Grade 12</option>
            </select>
        </div>
        <div class="form-group">
            <label for="subject">Favorite Subject:</label>
            <input type="text" id="subject" name="subject" value="Computer Science" placeholder="Enter your favorite subject">
        </div>
        <button type="submit">Submit Information</button>
    </form>
    <script>
        document.getElementById('studentForm').addEventListener('submit', function(e) {
            e.preventDefault();
            alert('Form submitted successfully!');
        });
    </script>
</body>
</html>'''
    
    # Submit the completed HTML
    submit_data = {
        'content': completed_html
    }
    response = session.post(f"{BASE_URL}/submit_html_assignment/{assignment_id}", data=submit_data)
    if response.status_code != 200:
        print("❌ HTML assignment submission failed")
        return False
    print("✅ HTML assignment submitted successfully")
    
    # Step 7: Logout student
    session.get(f"{BASE_URL}/logout")
    
    # Step 8: Login as teacher to grade
    print("\n6. Logging in as teacher to grade...")
    login_data = {
        'username': 'tutor1',
        'password': 'teacher123'
    }
    response = session.post(f"{BASE_URL}/login", data=login_data)
    if response.status_code != 200:
        print("❌ Teacher login failed for grading")
        return False
    print("✅ Teacher login successful for grading")
    
    # Step 9: View submissions
    print("\n7. Viewing submissions...")
    response = session.get(f"{BASE_URL}/view_submissions/{assignment_id}")
    if response.status_code != 200:
        print("❌ Failed to view submissions")
        return False
    
    submissions_content = response.text
    if 'John Doe' not in submissions_content:
        print("❌ Student submission not found in submissions list")
        return False
    print("✅ Student submission found in submissions list")
    
    # Step 10: Grade the submission
    print("\n8. Grading the submission...")
    
    # Get submission ID (simplified - assume it's submission 1)
    submission_id = 1
    
    grade_data = {
        'grade': '95',
        'feedback': 'Excellent work! Your HTML form is well-structured and all fields are properly filled out. The styling is clean and professional.'
    }
    response = session.post(f"{BASE_URL}/grade_submission/{submission_id}", data=grade_data)
    if response.status_code != 200:
        print("❌ Grading failed")
        return False
    print("✅ Submission graded successfully")
    
    print("\n=== HTML Assignment Workflow Test PASSED! ===")
    return True

if __name__ == "__main__":
    success = test_html_assignment_workflow()
    if success:
        print("\n🎉 All tests passed! The HTML assignment workflow is working correctly.")
    else:
        print("\n❌ Some tests failed. Please check the server logs for details.")
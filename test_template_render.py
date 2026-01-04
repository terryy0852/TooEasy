# Test rendering the login template which includes the forgot_password link
from app import app
from flask import render_template_string
import os

with app.test_request_context():
    print("Testing template rendering...")
    
    try:
        # Read the login.html template content
        login_template_path = os.path.join(app.root_path, 'templates', 'login.html')
        with open(login_template_path, 'r', encoding='utf-8') as f:
            login_template_content = f.read()
        
        # Render the template
        rendered_template = render_template_string(login_template_content)
        print(f"Template rendered successfully!")
        print(f"Rendered content length: {len(rendered_template)} bytes")
        
        # Check if the forgot_password link is in the rendered content
        if 'forgot_password' in rendered_template:
            print("✓ Found 'forgot_password' in rendered content")
        else:
            print("✗ 'forgot_password' not found in rendered content")
        
        # Show a small part of the rendered content
        print(f"\nRendered content (first 200 chars):")
        print(rendered_template[:200])
        
    except Exception as e:
        print(f"\nError: {e}")
        import traceback
        traceback.print_exc()

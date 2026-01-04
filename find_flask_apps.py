import os
import re

def find_flask_app_files():
    """Find Python files that contain Flask app code"""
    flask_app_files = []
    flask_patterns = [
        r'from flask import',
        r'app\s*=\s*Flask'
    ]
    
    for filename in os.listdir('.'):
        if filename.endswith('.py') and os.path.isfile(filename):
            try:
                with open(filename, 'r', encoding='utf-8') as f:
                    content = f.read()
                    for pattern in flask_patterns:
                        if re.search(pattern, content, re.IGNORECASE):
                            flask_app_files.append(filename)
                            break
            except Exception as e:
                print(f"Error reading {filename}: {e}")
    
    return flask_app_files

def main():
    print("Searching for Flask app files...")
    flask_files = find_flask_app_files()
    
    print(f"\nFound {len(flask_files)} files containing Flask app code:")
    for filename in flask_files:
        print(f"- {filename}")
    
    # Check app.py specifically
    if os.path.exists('app.py'):
        size = os.path.getsize('app.py')
        print(f"\napp.py file size: {size} bytes")
        if size == 0:
            print("WARNING: app.py is empty!")

if __name__ == '__main__':
    main()

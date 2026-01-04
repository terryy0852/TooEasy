# Check what routes are registered in the Flask application
from flask import Flask
import sys
import os

# Add current directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Import the app
from app import app

# Print all registered routes
print("Registered routes:")
print("-" * 50)
for rule in app.url_map.iter_rules():
    methods = ', '.join(sorted(rule.methods))
    path = str(rule)
    endpoint = rule.endpoint
    print(f"{path} ({methods}) -> {endpoint}")

# Check specifically for the password reset routes
print("\nChecking password reset routes:")
print("-" * 50)
for rule in app.url_map.iter_rules():
    if 'password' in rule.endpoint or 'forgot' in rule.endpoint or 'reset' in rule.endpoint:
        methods = ', '.join(sorted(rule.methods))
        path = str(rule)
        endpoint = rule.endpoint
        print(f"{path} ({methods}) -> {endpoint}")

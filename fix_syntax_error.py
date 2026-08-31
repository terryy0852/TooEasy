# Fix the syntax error in app.py where the logout route is missing a newline

with open('app.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Find the problematic area and add a newline
fixed_content = content.replace('    return render_template(\'reset_password.html\', token=token)\n@app.route(\'/logout\')', '    return render_template(\'reset_password.html\', token=token)\n\n@app.route(\'/logout\')')

# Write the fixed content back to the file
with open('app.py', 'w', encoding='utf-8') as f:
    f.write(fixed_content)

print("Fixed the syntax error by adding a newline before the logout route")

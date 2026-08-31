import sqlite3
import re

conn = sqlite3.connect('instance/assignments.db')
cursor = conn.cursor()

cursor.execute('SELECT content FROM submission ORDER BY id DESC LIMIT 1')
content = cursor.fetchone()[0]

print(f'Total content length: {len(content)} characters\n')

# Find all textarea elements
textareas = re.findall(r'<textarea[^>]*>(.*?)</textarea>', content, re.DOTALL)
print(f'Found {len(textareas)} textarea elements\n')

for i, ta in enumerate(textareas):
    print(f'Textarea {i+1}:')
    cleaned = ta.strip()
    if cleaned:
        print(f'  Content: {cleaned[:150]}...' if len(cleaned) > 150 else f'  Content: {cleaned}')
    else:
        print(f'  Content: [EMPTY]')
    print()

# Find all input elements with values
inputs = re.findall(r'<input[^>]*value="([^"]*)"[^>]*>', content)
print(f'Found {len(inputs)} input elements with values\n')

for i, val in enumerate(inputs[:5]):
    print(f'Input {i+1} value: {val}')

conn.close()

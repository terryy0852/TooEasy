import sqlite3

conn = sqlite3.connect('instance/assignments.db')
cursor = conn.cursor()

print("Submission table schema:")
cursor.execute('PRAGMA table_info(submission)')
columns = cursor.fetchall()
for col in columns:
    print(f"  {col[1]}: {col[2]}")

print(f"\nTotal columns: {len(columns)}")

print("\nSample submissions:")
cursor.execute('SELECT * FROM submission ORDER BY id DESC LIMIT 2')
rows = cursor.fetchall()
for i, row in enumerate(rows):
    print(f"  Submission {i+1}:")
    for j, col_value in enumerate(row):
        col_name = columns[j][1]
        if col_name == 'content' and col_value:
            print(f"    {col_name}: {len(col_value)} characters")
        else:
            print(f"    {col_name}: {col_value}")
    print()

conn.close()
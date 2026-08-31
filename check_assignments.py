#!/usr/bin/env python3
"""Check assignments and their creators"""

import sqlite3

conn = sqlite3.connect('instance/assignments.db')
cursor = conn.cursor()

cursor.execute('SELECT id, title, created_by FROM assignment')
assignments = cursor.fetchall()

print('Assignments:')
for assignment in assignments:
    print(f'ID {assignment[0]}: {assignment[1]} (created by user ID {assignment[2]})')

cursor.execute('SELECT id, username FROM user WHERE id IN (SELECT DISTINCT created_by FROM assignment)')
creators = cursor.fetchall()
print('\nAssignment creators:')
for creator in creators:
    print(f'User ID {creator[0]}: {creator[1]}')

conn.close()
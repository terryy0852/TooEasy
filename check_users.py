#!/usr/bin/env python3
"""Check available users in the database"""

import sqlite3

conn = sqlite3.connect('instance/assignments.db')
cursor = conn.cursor()

cursor.execute('SELECT id, username, role FROM user')
users = cursor.fetchall()

print('Available users:')
for user in users:
    print(f'ID {user[0]}: {user[1]} ({user[2]})')

conn.close()
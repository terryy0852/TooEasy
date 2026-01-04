from app import app, db
from sqlalchemy import text

with app.app_context():
    print('Checking database schema...')
    print('\nTables in the database:')
    tables = db.session.execute(text('SELECT name FROM sqlite_master WHERE type=\'table\' ORDER BY name;'))
    for table in tables:
        print(f'- {table[0]}')
    
    print('\nAssignment table schema:')
    schema = db.session.execute(text('PRAGMA table_info(assignment);'))
    for column in schema:
        print(f'- {column[1]} ({column[2]})')
    
    print('\nUser table schema:')
    schema = db.session.execute(text('PRAGMA table_info(user);'))
    for column in schema:
        print(f'- {column[1]} ({column[2]})')
    
    print('\nChecking for admin user:')
    from app import User
    admin = User.query.filter_by(username='admin').first()
    if admin:
        print(f'Admin user found: ID={admin.id}, Username={admin.username}, Role={admin.role}')
    else:
        print('Admin user not found!')


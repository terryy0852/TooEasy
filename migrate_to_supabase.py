"""
Migration script to move data from Render PostgreSQL to Supabase.

Prerequisites:
1. Create a Supabase project at https://supabase.com
2. Get your Supabase connection string
3. Keep your Render database running during migration

Usage:
1. Set RENDER_DATABASE_URL to your Render PostgreSQL connection string
2. Set SUPABASE_DATABASE_URL to your Supabase connection string
3. Run: python migrate_to_supabase.py

Example (PowerShell):
$env:RENDER_DATABASE_URL = "postgresql://user:pass@your-render-db.url.render.com:5432/db"
$env:SUPABASE_DATABASE_URL = "postgresql://postgres:password@db.project-ref.supabase.co:5432/postgres"
python migrate_to_supabase.py
"""

import os
import psycopg2
from psycopg2.extras import execute_values
from sqlalchemy import create_engine, MetaData, Table, select
from sqlalchemy.dialects.postgresql import insert as pg_insert

# Get connection strings from environment
RENDER_DB_URL = os.environ.get('RENDER_DATABASE_URL')
SUPABASE_DB_URL = os.environ.get('SUPABASE_DATABASE_URL')

if not RENDER_DB_URL or not SUPABASE_DB_URL:
    print("Error: Please set both RENDER_DATABASE_URL and SUPABASE_DATABASE_URL environment variables")
    print("Example:")
    print("  $env:RENDER_DATABASE_URL = 'postgresql://user:pass@host:port/db'")
    print("  $env:SUPABASE_DATABASE_URL = 'postgresql://postgres:pass@db.project.supabase.co:5432/postgres'")
    exit(1)

def migrate_table(source_conn, target_conn, table_name):
    """Migrate data from source to target for a specific table"""
    print(f"Migrating {table_name}...")
    
    # Get all data from source
    with source_conn.cursor() as cur:
        cur.execute(f"SELECT * FROM {table_name}")
        rows = cur.fetchall()
        
        if not rows:
            print(f"  No data found in {table_name}")
            return 0
            
        # Get column names
        colnames = [desc[0] for desc in cur.description]
        
        # Insert into target
        with target_conn.cursor() as target_cur:
            # Create insert query
            columns = ", ".join(colnames)
            placeholders = ", ".join(["%s"] * len(colnames))
            insert_query = f"INSERT INTO {table_name} ({columns}) VALUES ({placeholders})"
            
            # Insert all rows
            target_cur.executemany(insert_query, rows)
            
            print(f"  Migrated {len(rows)} rows to {table_name}")
            return len(rows)

def main():
    print("Starting migration from Render to Supabase...")
    print(f"Source: {RENDER_DB_URL}")
    print(f"Target: {SUPABASE_DB_URL}")
    
    try:
        # Connect to both databases
        source_conn = psycopg2.connect(RENDER_DB_URL)
        target_conn = psycopg2.connect(SUPABASE_DB_URL)
        
        # List of tables to migrate (in correct order to respect foreign keys)
        tables = ['user', 'assignment', 'assignment_students', 'submission']
        
        total_migrated = 0
        
        for table in tables:
            try:
                count = migrate_table(source_conn, target_conn, table)
                total_migrated += count
                target_conn.commit()  # Commit after each table
            except Exception as e:
                print(f"Error migrating {table}: {e}")
                target_conn.rollback()
                
        print(f"\nMigration completed! Total rows migrated: {total_migrated}")
        
        # Close connections
        source_conn.close()
        target_conn.close()
        
    except Exception as e:
        print(f"Migration failed: {e}")
        if 'source_conn' in locals():
            source_conn.close()
        if 'target_conn' in locals():
            target_conn.close()

if __name__ == "__main__":
    main()
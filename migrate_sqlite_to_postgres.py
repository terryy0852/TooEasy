"""
SQLite → PostgreSQL one-time data migration script for this app.

Prereqs:
- Ensure your Postgres DB is created and tables exist (deploy the app on Render once).
- Install dependencies: `pip install -r requirements.txt`.

Usage (local machine):
1) Set DATABASE_URL to Render External Database URL, e.g.
   PowerShell:
     $env:DATABASE_URL = "postgres://<user>:<pass>@<host>:<port>/<db>"
2) Run:
     python migrate_sqlite_to_postgres.py

Notes:
- This script copies tables: user, assignment, submission.
- It preserves IDs and resets sequences after insert.
- If rows already exist in Postgres, they are skipped.
"""

import os
from sqlalchemy import create_engine, MetaData, Table, select, text
from sqlalchemy.dialects.postgresql import insert as pg_insert

SQLITE_PATH = os.environ.get("SQLITE_PATH", "instance/assignments.db")
DATABASE_URL = os.environ.get("DATABASE_URL")

if not DATABASE_URL:
    raise SystemExit("Please set DATABASE_URL to your PostgreSQL connection string.")

# Normalize Render-provided URL for SQLAlchemy
if DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)

sqlite_url = f"sqlite:///{SQLITE_PATH}"

print(f"[MIGRATE] SQLite: {sqlite_url}")
print(f"[MIGRATE] Postgres: {DATABASE_URL}")

sqlite_engine = create_engine(sqlite_url)
pg_engine = create_engine(DATABASE_URL)

# Reflect schemas
sqlite_meta = MetaData()
sqlite_meta.reflect(bind=sqlite_engine, only=["user", "assignment", "submission"])

pg_meta = MetaData()
pg_meta.reflect(bind=pg_engine, only=["user", "assignment", "submission"])

sqlite_user = sqlite_meta.tables.get("user")
sqlite_assignment = sqlite_meta.tables.get("assignment")
sqlite_submission = sqlite_meta.tables.get("submission")

pg_user = pg_meta.tables.get("user")
pg_assignment = pg_meta.tables.get("assignment")
pg_submission = pg_meta.tables.get("submission")

if not all([sqlite_user, sqlite_assignment, sqlite_submission]):
    raise SystemExit("Expected tables not found in SQLite. Make sure the local app has been run at least once.")
if not all([pg_user, pg_assignment, pg_submission]):
    raise SystemExit("Expected tables not found in Postgres. Deploy/run the app once to create tables, then retry.")

def copy_table(sqlite_tbl: Table, pg_tbl: Table, key_cols):
    """Copy rows from sqlite_tbl to pg_tbl, skipping conflicts on provided key_cols."""
    src_conn = sqlite_engine.connect()
    dst_conn = pg_engine.connect()
    trans = dst_conn.begin()
    try:
        rows = src_conn.execute(select(sqlite_tbl)).mappings().all()
        print(f"[MIGRATE] Copying {len(rows)} rows into {pg_tbl.name}")
        for row in rows:
            # Convert SQLite bools (0/1) to Python bools for Postgres
            payload = dict(row)
            for k, v in payload.items():
                if isinstance(v, int) and k in {"is_tutor", "is_graded"}:
                    payload[k] = bool(v)

            ins = pg_insert(pg_tbl).values(**payload)
            # ON CONFLICT DO NOTHING on primary key
            ins = ins.on_conflict_do_nothing(index_elements=key_cols)
            dst_conn.execute(ins)

        trans.commit()
        print(f"[MIGRATE] Finished {pg_tbl.name}")
    except Exception as e:
        trans.rollback()
        raise
    finally:
        src_conn.close()
        dst_conn.close()


def reset_sequence(table_name: str, pk_column: str = "id"):
    """Reset Postgres sequence to max(id)."""
    stmt = text(
        f"SELECT setval(pg_get_serial_sequence('{table_name}', '{pk_column}'), COALESCE(MAX({pk_column}), 1)) FROM {table_name};"
    )
    with pg_engine.connect() as conn:
        conn.execute(stmt)
        print(f"[MIGRATE] Sequence reset for {table_name}")


if __name__ == "__main__":
    copy_table(sqlite_user, pg_user, key_cols=["id"])
    copy_table(sqlite_assignment, pg_assignment, key_cols=["id"])
    copy_table(sqlite_submission, pg_submission, key_cols=["id"])

    # Reset sequences
    reset_sequence("user", "id")
    reset_sequence("assignment", "id")
    reset_sequence("submission", "id")

    print("[MIGRATE] Done.")
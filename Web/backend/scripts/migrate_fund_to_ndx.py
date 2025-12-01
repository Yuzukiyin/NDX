"""Migrate existing fund.db data into unified ndx_users.db with user_id=1.
Run locally:
  python scripts/migrate_fund_to_ndx.py
"""
from pathlib import Path
import sqlite3

ROOT = Path(__file__).resolve().parents[1].parents[1]
BACKEND_DIR = ROOT / 'Web' / 'backend'
NDX_DB = BACKEND_DIR / 'ndx_users.db'
LEGACY_FUND_DB = ROOT / 'fund.db'
SCHEMA_SQL = BACKEND_DIR / 'app' / 'db' / 'fund_multitenant.sql'

USER_ID = 1


def ensure_schema():
    if not NDX_DB.exists():
        NDX_DB.touch()
    conn = sqlite3.connect(NDX_DB)
    try:
        cur = conn.cursor()
        cur.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='fund_overview'")
        if cur.fetchone() is None and SCHEMA_SQL.exists():
            conn.executescript(SCHEMA_SQL.read_text(encoding='utf-8'))
        conn.commit()
    finally:
        conn.close()


def migrate():
    if not LEGACY_FUND_DB.exists():
        print(f"Legacy fund.db not found at {LEGACY_FUND_DB}")
        return

    src = sqlite3.connect(LEGACY_FUND_DB)
    dst = sqlite3.connect(NDX_DB)
    try:
        s = src.cursor()
        d = dst.cursor()

        # Transactions -> transactions (add user_id)
        s.execute("SELECT fund_code, fund_name, transaction_date, nav_date, transaction_type, target_amount, shares, unit_nav, amount, note, created_at FROM transactions")
        rows = s.fetchall()
        d.executemany(
            """
            INSERT INTO transactions (user_id, fund_code, fund_name, transaction_date, nav_date, transaction_type, target_amount, shares, unit_nav, amount, note, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            [(USER_ID,)+r for r in rows]
        )

        # Fund overview will be rebuilt by triggers from transactions; optional: recompute by touching rows
        dst.commit()
        print(f"✅ Migrated {len(rows)} transactions into {NDX_DB}")
    finally:
        src.close()
        dst.close()


if __name__ == '__main__':
    ensure_schema()
    migrate()
    print("✨ Migration complete. You can now use ndx_users.db for both auth and fund data.")

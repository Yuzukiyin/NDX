"""Migrate legacy SQLite fund data into PostgreSQL."""
import argparse
import sqlite3
import sys
from pathlib import Path
from typing import Iterable, List, Dict, Any

from sqlalchemy import create_engine, text

BACKEND_DIR = Path(__file__).resolve().parents[1]
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

from app.config import settings  # noqa: E402

DEFAULT_SQLITE = (BACKEND_DIR / "ndx_users.db").resolve()

def chunked(items: List[Dict[str, Any]], size: int = 500) -> Iterable[List[Dict[str, Any]]]:
    for idx in range(0, len(items), size):
        yield items[idx: idx + size]


def load_sqlite(path: Path) -> sqlite3.Connection:
    if not path.exists():
        raise FileNotFoundError(f"SQLite database not found: {path}")
    conn = sqlite3.connect(str(path))
    conn.row_factory = sqlite3.Row
    return conn


def ensure_schema(engine):
    schema_path = BACKEND_DIR / "app" / "db" / "fund_multitenant_postgres.sql"
    with engine.connect() as conn:
        exists = conn.execute(text("SELECT to_regclass('public.transactions')")).scalar()
    if exists:
        return
    if not schema_path.exists():
        raise FileNotFoundError(f"Schema file missing: {schema_path}")
    sql = schema_path.read_text(encoding="utf-8")
    raw = engine.raw_connection()
    try:
        cur = raw.cursor()
        cur.execute(sql)
        raw.commit()
        print("✅ Created fund schema in PostgreSQL")
    finally:
        raw.close()


def migrate_transactions(src: sqlite3.Connection, engine, user_id: int) -> int:
    rows = src.execute(
        """
        SELECT fund_code, fund_name, transaction_date, nav_date, transaction_type,
               target_amount, shares, unit_nav, amount, note, created_at
        FROM transactions
        ORDER BY transaction_date, transaction_id
        """
    ).fetchall()

    if not rows:
        return 0

    payloads = [
        {
            "user_id": user_id,
            "fund_code": row["fund_code"],
            "fund_name": row["fund_name"],
            "transaction_date": row["transaction_date"],
            "nav_date": row["nav_date"],
            "transaction_type": row["transaction_type"],
            "target_amount": row["target_amount"],
            "shares": row["shares"],
            "unit_nav": row["unit_nav"],
            "amount": row["amount"],
            "note": row["note"],
            "created_at": row["created_at"],
        }
        for row in rows
    ]

    insert_sql = text(
        """
        INSERT INTO transactions (
            user_id, fund_code, fund_name, transaction_date, nav_date,
            transaction_type, target_amount, shares, unit_nav, amount, note, created_at
        ) VALUES (
            :user_id, :fund_code, :fund_name, :transaction_date, :nav_date,
            :transaction_type, :target_amount, :shares, :unit_nav, :amount, :note, :created_at
        )
        """
    )

    inserted = 0
    with engine.begin() as conn:
        for batch in chunked(payloads):
            conn.execute(insert_sql, batch)
            inserted += len(batch)
    return inserted


def migrate_nav_history(src: sqlite3.Connection, engine) -> int:
    rows = src.execute(
        """
        SELECT fund_code, fund_name, price_date, unit_nav,
               cumulative_nav, daily_growth_rate, data_source, fetched_at
        FROM fund_nav_history
        ORDER BY price_date
        """
    ).fetchall()

    if not rows:
        return 0

    payloads = [
        {
            "fund_code": row["fund_code"],
            "fund_name": row["fund_name"],
            "price_date": row["price_date"],
            "unit_nav": row["unit_nav"],
            "cumulative_nav": row["cumulative_nav"],
            "daily_growth_rate": row["daily_growth_rate"],
            "data_source": row["data_source"],
            "fetched_at": row["fetched_at"],
        }
        for row in rows
    ]

    insert_sql = text(
        """
        INSERT INTO fund_nav_history (
            fund_code, fund_name, price_date, unit_nav,
            cumulative_nav, daily_growth_rate, data_source, fetched_at
        ) VALUES (
            :fund_code, :fund_name, :price_date, :unit_nav,
            :cumulative_nav, :daily_growth_rate, :data_source, :fetched_at
        )
        ON CONFLICT (fund_code, price_date, data_source) DO UPDATE SET
            unit_nav = EXCLUDED.unit_nav,
            cumulative_nav = EXCLUDED.cumulative_nav,
            daily_growth_rate = EXCLUDED.daily_growth_rate,
            fetched_at = EXCLUDED.fetched_at
        """
    )

    inserted = 0
    with engine.begin() as conn:
        for batch in chunked(payloads):
            conn.execute(insert_sql, batch)
            inserted += len(batch)
    return inserted


def truncate_tables(engine, tables: List[str]):
    stmt = text("TRUNCATE TABLE " + ", ".join(tables) + " RESTART IDENTITY CASCADE")
    with engine.begin() as conn:
        conn.execute(stmt)


def main():
    parser = argparse.ArgumentParser(description="Migrate SQLite fund data into PostgreSQL")
    parser.add_argument("--sqlite-path", type=Path, default=DEFAULT_SQLITE, help="Path to source SQLite db")
    parser.add_argument("--user-id", type=int, default=1, help="User ID to assign to imported transactions")
    parser.add_argument("--postgres-url", type=str, default=None, help="Override PostgreSQL connection URL")
    parser.add_argument("--truncate", action="store_true", help="Truncate target tables before import")
    args = parser.parse_args()

    sqlite_conn = load_sqlite(args.sqlite_path)
    try:
        pg_url = args.postgres_url or settings.database_url_sync
        engine = create_engine(pg_url, future=True)

        ensure_schema(engine)

        if args.truncate:
            truncate_tables(engine, ["fund_overview", "transactions"])
            truncate_tables(engine, ["fund_nav_history"])

        tx_count = migrate_transactions(sqlite_conn, engine, args.user_id)
        nav_count = migrate_nav_history(sqlite_conn, engine)
        print(f"✅ Imported {tx_count} transactions and {nav_count} NAV rows into PostgreSQL")
    finally:
        sqlite_conn.close()


if __name__ == "__main__":
    main()

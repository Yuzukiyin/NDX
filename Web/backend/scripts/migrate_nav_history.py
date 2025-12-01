"""Import NAV history from fund.db into ndx_users.db (global shared table)."""
from pathlib import Path
import sqlite3

ROOT = Path(__file__).resolve().parents[1].parents[1]
BACKEND_DIR = ROOT / 'Web' / 'backend'
NDX_DB = BACKEND_DIR / 'ndx_users.db'
LEGACY_FUND_DB = ROOT / 'fund.db'


def migrate_nav_history():
    if not LEGACY_FUND_DB.exists():
        print(f"Legacy fund.db not found at {LEGACY_FUND_DB}")
        return

    src = sqlite3.connect(LEGACY_FUND_DB)
    dst = sqlite3.connect(NDX_DB)
    try:
        s = src.cursor()
        d = dst.cursor()

        # Copy fund_nav_history (global table, no user_id)
        s.execute("SELECT fund_code, fund_name, price_date, unit_nav, cumulative_nav, daily_growth_rate, data_source, fetched_at FROM fund_nav_history")
        rows = s.fetchall()
        
        if rows:
            d.executemany(
                """
                INSERT OR IGNORE INTO fund_nav_history 
                (fund_code, fund_name, price_date, unit_nav, cumulative_nav, daily_growth_rate, data_source, fetched_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """,
                rows
            )
            dst.commit()
            print(f"✅ Migrated {len(rows)} NAV history records into {NDX_DB}")
        else:
            print("⚠️ No NAV history found in fund.db")
    finally:
        src.close()
        dst.close()


if __name__ == '__main__':
    migrate_nav_history()
    print("✨ NAV history migration complete.")

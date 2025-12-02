"""Migrate legacy SQLite fund data into PostgreSQL."""
import argparse
import sqlite3
import sys
from pathlib import Path
from typing import Iterable, List, Dict, Any
import os

from sqlalchemy import create_engine, text

# 获取 DATABASE_URL
db_url = os.getenv('DATABASE_URL')

# 如果是 Railway 内部环境，DATABASE_URL 已经是正确的
# 如果包含 postgres.railway.internal，说明在 Railway 容器内
if db_url and 'postgres.railway.internal' in db_url:
    # 直接使用，不需要修改
    pass
elif db_url and db_url.startswith('postgresql://'):
    # 如果是外部 URL，添加 psycopg2 驱动
    db_url = db_url.replace('postgresql://', 'postgresql+psycopg2://')

BACKEND_DIR = Path(__file__).resolve().parents[1]
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

from app.config import settings  # noqa: E402

DEFAULT_SQLITE = (BACKEND_DIR / "ndx_users.db").resolve()

def chunked(items: List[Dict[str, Any]], size: int = 2000) -> Iterable[List[Dict[str, Any]]]:
    for idx in range(0, len(items), size):
        yield items[idx: idx + size]


def load_sqlite(path: Path) -> sqlite3.Connection:
    if not path.exists():
        raise FileNotFoundError(f"SQLite database not found: {path}")
    conn = sqlite3.connect(str(path))
    conn.row_factory = sqlite3.Row
    return conn


def ensure_schema(engine):
    print("🔍 检查数据库schema...")
    schema_path = BACKEND_DIR / "app" / "db" / "fund_multitenant_postgres.sql"
    with engine.connect() as conn:
        exists = conn.execute(text("SELECT to_regclass('public.transactions')")).scalar()
    if exists:
        print("✅ Schema已存在，跳过创建")
        return
    if not schema_path.exists():
        raise FileNotFoundError(f"Schema file missing: {schema_path}")
    print("📝 创建fund schema...")
    sql = schema_path.read_text(encoding="utf-8")
    raw = engine.raw_connection()
    try:
        cur = raw.cursor()
        cur.execute(sql)
        raw.commit()
        print("✅ Schema创建成功")
    finally:
        raw.close()


def migrate_transactions(src: sqlite3.Connection, engine, user_id: int) -> int:
    print("📊 读取交易记录...")
    rows = src.execute(
        """
        SELECT fund_code, fund_name, transaction_date, nav_date, transaction_type,
               target_amount, shares, unit_nav, amount, note, created_at
        FROM transactions
        ORDER BY transaction_date, transaction_id
        """
    ).fetchall()

    if not rows:
        print("⚠️  没有找到交易记录")
        return 0

    total = len(rows)
    print(f"📦 准备迁移 {total} 条交易记录（user_id={user_id}）...")

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
    print("🚀 开始插入数据...")
    with engine.begin() as conn:
        for batch in chunked(payloads):
            conn.execute(insert_sql, batch)
            inserted += len(batch)
            percentage = (inserted / total) * 100
            print(f"   ⏳ 已插入 {inserted}/{total} 条交易记录 ({percentage:.1f}%)")
    print(f"✅ 交易记录迁移完成：{inserted} 条")
    return inserted


def migrate_nav_history(src: sqlite3.Connection, engine) -> int:
    print("\n📈 读取历史净值数据...")
    rows = src.execute(
        """
        SELECT fund_code, fund_name, price_date, unit_nav,
               cumulative_nav, daily_growth_rate, data_source, fetched_at
        FROM fund_nav_history
        ORDER BY price_date
        """
    ).fetchall()

    if not rows:
        print("⚠️  没有找到历史净值数据")
        return 0

    total = len(rows)
    print(f"📦 准备迁移 {total} 条历史净值记录...")

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
    print("🚀 开始插入数据...")
    with engine.begin() as conn:
        for batch in chunked(payloads):
            conn.execute(insert_sql, batch)
            inserted += len(batch)
            percentage = (inserted / total) * 100
            print(f"   ⏳ 已插入 {inserted}/{total} 条历史净值 ({percentage:.1f}%)")
    print(f"✅ 历史净值迁移完成：{inserted} 条")
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

    print("="*60)
    print("🚀 开始迁移 fund.db 数据到 PostgreSQL")
    print("="*60)
    print(f"📂 SQLite路径: {args.sqlite_path}")
    print(f"👤 目标用户ID: {args.user_id}")
    
    sqlite_conn = load_sqlite(args.sqlite_path)
    try:
        pg_url = args.postgres_url or settings.database_url_sync
        # 隐藏密码显示
        display_url = pg_url.split('@')[1] if '@' in pg_url else 'PostgreSQL'
        print(f"🔗 PostgreSQL: {display_url}")
        print("\n🔌 正在连接数据库...")
        engine = create_engine(pg_url, future=True)
        print("✅ 数据库连接成功\n")

        ensure_schema(engine)

        if args.truncate:
            print("\n🗑️  清空现有数据...")
            truncate_tables(engine, ["fund_overview", "transactions"])
            truncate_tables(engine, ["fund_nav_history"])
            print("✅ 数据清空完成\n")

        tx_count = migrate_transactions(sqlite_conn, engine, args.user_id)
        nav_count = migrate_nav_history(sqlite_conn, engine)
        
        print("\n" + "="*60)
        print("🎉 迁移完成！")
        print("="*60)
        print(f"✅ 交易记录: {tx_count} 条")
        print(f"✅ 历史净值: {nav_count} 条")
        print(f"📊 总计: {tx_count + nav_count} 条数据")
        print("="*60)
    finally:
        sqlite_conn.close()


if __name__ == "__main__":
    main()

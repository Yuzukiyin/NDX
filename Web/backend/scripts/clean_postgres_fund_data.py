"""
清空 PostgreSQL 基金相关表，准备重新迁移数据
使用方法：
    $env:DATABASE_URL="postgresql://..." ; python scripts/clean_postgres_fund_data.py
"""
import os
import sys
from pathlib import Path
from sqlalchemy import create_engine, text

BACKEND_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BACKEND_DIR))

from app.config import settings

# PostgreSQL URL
PG_URL = os.environ.get('DATABASE_URL') or settings.DATABASE_URL
if PG_URL.startswith('sqlite'):
    print("❌ 需要 PostgreSQL 数据库")
    sys.exit(1)

# 转换为同步驱动
if PG_URL.startswith('postgresql+asyncpg://'):
    PG_URL = PG_URL.replace('postgresql+asyncpg://', 'postgresql+psycopg2://')
elif PG_URL.startswith('postgresql://'):
    PG_URL = PG_URL.replace('postgresql://', 'postgresql+psycopg2://')

print("=" * 60)
print("🗑️  清空 PostgreSQL 基金数据")
print("=" * 60)
print(f"数据库: {PG_URL.split('@')[1] if '@' in PG_URL else 'PostgreSQL'}")
print("=" * 60)

engine = create_engine(PG_URL, future=True)

def clean_tables():
    """清空基金相关表（保留 users 和 refresh_tokens）"""
    with engine.begin() as conn:
        # 先删除有外键依赖的表
        print("\n📊 清空 fund_overview（会级联删除）...")
        result = conn.execute(text("DELETE FROM fund_overview"))
        print(f"  删除 {result.rowcount} 行")
        
        print("\n📈 清空 transactions...")
        result = conn.execute(text("DELETE FROM transactions"))
        print(f"  删除 {result.rowcount} 行")
        
        print("\n📉 清空 fund_nav_history...")
        result = conn.execute(text("DELETE FROM fund_nav_history"))
        print(f"  删除 {result.rowcount} 行")
        
        # 重置序列（PostgreSQL 自增 ID）
        print("\n🔄 重置序列...")
        conn.execute(text("ALTER SEQUENCE transactions_transaction_id_seq RESTART WITH 1"))
        conn.execute(text("ALTER SEQUENCE fund_overview_fund_id_seq RESTART WITH 1"))
        conn.execute(text("ALTER SEQUENCE fund_nav_history_nav_id_seq RESTART WITH 1"))
    
    print("\n✅ 清空完成！")

def verify():
    """验证表已清空"""
    print("\n🔍 验证结果...")
    with engine.connect() as conn:
        tables = ['transactions', 'fund_overview', 'fund_nav_history']
        for table in tables:
            count = conn.execute(text(f"SELECT COUNT(*) FROM {table}")).scalar()
            print(f"  {table}: {count} 行")

if __name__ == '__main__':
    confirm = input("\n⚠️  确认清空所有基金数据？(输入 yes 继续): ")
    if confirm.lower() != 'yes':
        print("已取消")
        sys.exit(0)
    
    try:
        clean_tables()
        verify()
        print("\n" + "=" * 60)
        print("✨ 现在可以运行迁移脚本了：")
        print("   python scripts/migrate_sqlite_to_postgres.py --sqlite-path ../../fund.db --user-id 1")
        print("=" * 60)
    except Exception as e:
        print(f"\n❌ 清空失败: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

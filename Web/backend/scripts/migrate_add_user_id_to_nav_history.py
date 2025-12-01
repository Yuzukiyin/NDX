"""
数据库迁移脚本：为 fund_nav_history 表添加 user_id 字段
"""
import sqlite3
import sys
from pathlib import Path

def migrate_nav_history(db_path='./ndx_users.db', default_user_id=1):
    """
    为现有的 fund_nav_history 表添加 user_id 字段
    
    Args:
        db_path: 数据库文件路径
        default_user_id: 默认用户ID（将现有数据分配给此用户）
    """
    print(f"开始迁移数据库: {db_path}")
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        # 检查表是否存在
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='fund_nav_history'")
        if not cursor.fetchone():
            print("fund_nav_history 表不存在，跳过迁移")
            conn.close()
            return
        
        # 检查是否已有 user_id 字段
        cursor.execute("PRAGMA table_info(fund_nav_history)")
        columns = [row[1] for row in cursor.fetchall()]
        
        if 'user_id' in columns:
            print("fund_nav_history 表已有 user_id 字段，跳过迁移")
            conn.close()
            return
        
        print("开始迁移...")
        
        # 创建新表结构
        cursor.execute("""
            CREATE TABLE fund_nav_history_new (
                nav_id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL DEFAULT 1,
                fund_code TEXT NOT NULL,
                fund_name TEXT NOT NULL,
                price_date TEXT NOT NULL,
                unit_nav REAL NOT NULL,
                cumulative_nav REAL,
                daily_growth_rate REAL,
                data_source TEXT DEFAULT 'fundSpider',
                fetched_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(user_id, fund_code, price_date, data_source)
            )
        """)
        
        # 复制数据，设置默认 user_id
        cursor.execute(f"""
            INSERT INTO fund_nav_history_new (
                nav_id, user_id, fund_code, fund_name, price_date, 
                unit_nav, cumulative_nav, daily_growth_rate, data_source, fetched_at
            )
            SELECT 
                nav_id, {default_user_id}, fund_code, fund_name, price_date,
                unit_nav, cumulative_nav, daily_growth_rate, data_source, fetched_at
            FROM fund_nav_history
        """)
        
        # 删除旧表
        cursor.execute("DROP TABLE fund_nav_history")
        
        # 重命名新表
        cursor.execute("ALTER TABLE fund_nav_history_new RENAME TO fund_nav_history")
        
        # 创建索引
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_fund_nav_history_code_date
            ON fund_nav_history(user_id, fund_code, price_date)
        """)
        
        conn.commit()
        
        # 统计迁移的记录数
        cursor.execute("SELECT COUNT(*) FROM fund_nav_history")
        count = cursor.fetchone()[0]
        
        print(f"✅ 迁移成功！共迁移 {count} 条历史净值记录")
        print(f"   所有记录已分配给 user_id={default_user_id}")
        
    except Exception as e:
        conn.rollback()
        print(f"❌ 迁移失败: {e}")
        import traceback
        traceback.print_exc()
    finally:
        conn.close()


if __name__ == '__main__':
    # 可以通过命令行参数指定数据库路径
    db_path = sys.argv[1] if len(sys.argv) > 1 else './ndx_users.db'
    default_user_id = int(sys.argv[2]) if len(sys.argv) > 2 else 1
    
    migrate_nav_history(db_path, default_user_id)

"""
添加 auto_invest_plans 表到 PostgreSQL 数据库
可以在 Railway 或本地运行此脚本
"""

import os
import sys
from pathlib import Path

# 添加父目录到 path
backend_dir = Path(__file__).parent.parent
sys.path.insert(0, str(backend_dir))

from sqlalchemy import create_engine, text

def add_auto_invest_plans_table():
    """添加 auto_invest_plans 表"""
    # 从环境变量或默认值获取数据库 URL
    db_url = os.getenv('DATABASE_URL')
    
    if not db_url:
        print("错误: 未设置 DATABASE_URL 环境变量")
        print("请使用: export DATABASE_URL='postgresql://...'")
        return
    
    # 处理 Railway 的数据库 URL (可能是 postgres:// 而不是 postgresql://)
    if db_url.startswith('postgres://'):
        db_url = db_url.replace('postgres://', 'postgresql://', 1)
    
    print(f"连接数据库: {db_url.split('@')[1] if '@' in db_url else 'local'}")
    
    engine = create_engine(db_url, future=True)
    
    sql = """
    -- Auto-invest plans table
    CREATE TABLE IF NOT EXISTS auto_invest_plans (
        plan_id BIGSERIAL PRIMARY KEY,
        user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
        plan_name TEXT NOT NULL,
        fund_code TEXT NOT NULL,
        fund_name TEXT NOT NULL,
        amount NUMERIC(20,2) NOT NULL CHECK(amount > 0),
        frequency TEXT NOT NULL CHECK(frequency IN ('daily','weekly','monthly')),
        start_date DATE NOT NULL,
        end_date DATE NOT NULL,
        enabled BOOLEAN NOT NULL DEFAULT true,
        created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
        UNIQUE(user_id, plan_name)
    );

    CREATE INDEX IF NOT EXISTS idx_auto_invest_user
    ON auto_invest_plans(user_id, enabled);
    """
    
    try:
        with engine.connect() as conn:
            with conn.begin():
                # 检查表是否已存在
                check_result = conn.execute(text("""
                    SELECT EXISTS (
                        SELECT FROM information_schema.tables 
                        WHERE table_name = 'auto_invest_plans'
                    )
                """))
                exists = check_result.scalar()
                
                if exists:
                    print("✅ auto_invest_plans 表已存在，跳过创建")
                else:
                    print("正在创建 auto_invest_plans 表...")
                    conn.execute(text(sql))
                    print("✅ auto_invest_plans 表创建成功！")
        
        # 验证表结构
        with engine.connect() as conn:
            result = conn.execute(text("""
                SELECT column_name, data_type 
                FROM information_schema.columns 
                WHERE table_name = 'auto_invest_plans'
                ORDER BY ordinal_position
            """))
            columns = result.fetchall()
            
            print("\n表结构:")
            for col_name, col_type in columns:
                print(f"  - {col_name}: {col_type}")
        
        print("\n✅ 所有操作完成！")
        
    except Exception as e:
        print(f"❌ 错误: {e}")
        import traceback
        traceback.print_exc()


if __name__ == '__main__':
    add_auto_invest_plans_table()

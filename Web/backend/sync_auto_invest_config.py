"""
同步 auto_invest_setting.json 到数据库的脚本
将JSON配置中的定投计划导入到 auto_invest_plans 表
"""
import json
import sqlite3
from pathlib import Path

def sync_config_to_db(config_path='auto_invest_setting.json', db_path='ndx_users.db', user_id=1):
    """
    同步配置文件到数据库
    
    Args:
        config_path: JSON配置文件路径
        db_path: 数据库路径
        user_id: 用户ID (默认为1,即admin用户)
    """
    # 读取JSON配置
    config_file = Path(config_path)
    if not config_file.exists():
        print(f"配置文件不存在: {config_path}")
        return
    
    with open(config_file, 'r', encoding='utf-8') as f:
        config = json.load(f)
    
    plans = config.get('plans', [])
    if not plans:
        print("配置文件中没有定投计划")
        return
    
    # 连接数据库
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()
    
    # 确保表存在
    cur.execute("""
        CREATE TABLE IF NOT EXISTS auto_invest_plans (
            plan_id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            plan_name TEXT NOT NULL,
            fund_code TEXT NOT NULL,
            fund_name TEXT NOT NULL,
            amount REAL NOT NULL CHECK(amount > 0),
            frequency TEXT NOT NULL CHECK(frequency IN ('daily', 'weekly', 'monthly')),
            start_date TEXT NOT NULL,
            end_date TEXT NOT NULL,
            enabled INTEGER NOT NULL DEFAULT 1,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(user_id, plan_name)
        )
    """)
    
    # 为user_id和enabled创建索引
    cur.execute("""
        CREATE INDEX IF NOT EXISTS idx_auto_invest_user_enabled 
        ON auto_invest_plans(user_id, enabled)
    """)
    
    # 插入或更新计划
    synced = 0
    updated = 0
    
    for plan in plans:
        try:
            # 检查是否已存在
            cur.execute("""
                SELECT plan_id FROM auto_invest_plans
                WHERE user_id = ? AND plan_name = ?
            """, (user_id, plan['plan_name']))
            
            existing = cur.fetchone()
            
            if existing:
                # 更新现有计划
                cur.execute("""
                    UPDATE auto_invest_plans
                    SET fund_code = ?,
                        fund_name = ?,
                        amount = ?,
                        frequency = ?,
                        start_date = ?,
                        end_date = ?,
                        enabled = ?
                    WHERE plan_id = ?
                """, (
                    plan['fund_code'],
                    plan['fund_name'],
                    plan['amount'],
                    plan['frequency'],
                    plan['start_date'],
                    plan['end_date'],
                    1 if plan.get('enabled', True) else 0,
                    existing[0]
                ))
                updated += 1
                print(f"✓ 更新计划: {plan['plan_name']}")
            else:
                # 插入新计划
                cur.execute("""
                    INSERT INTO auto_invest_plans (
                        user_id, plan_name, fund_code, fund_name,
                        amount, frequency, start_date, end_date, enabled
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    user_id,
                    plan['plan_name'],
                    plan['fund_code'],
                    plan['fund_name'],
                    plan['amount'],
                    plan['frequency'],
                    plan['start_date'],
                    plan['end_date'],
                    1 if plan.get('enabled', True) else 0
                ))
                synced += 1
                print(f"✓ 新增计划: {plan['plan_name']}")
        
        except Exception as e:
            print(f"✗ 处理计划失败 {plan.get('plan_name', 'Unknown')}: {e}")
    
    conn.commit()
    conn.close()
    
    print(f"\n同步完成: 新增 {synced} 个, 更新 {updated} 个")

if __name__ == '__main__':
    # 在backend目录下运行
    sync_config_to_db(
        config_path='auto_invest_setting.json',
        db_path='ndx_users.db',
        user_id=1  # admin用户
    )

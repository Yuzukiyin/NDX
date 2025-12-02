"""
数据同步脚本 - 定期更新净值数据
可以设置为定时任务（cron/scheduled task）
"""
import sys
import os
from datetime import datetime

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'Web', 'backend'))

from fetch_history_nav import HistoryNavFetcher
from update_pending_transactions import process_pending_records

def sync_nav_data():
    """同步所有启用计划的净值数据"""
    print(f"\n[{datetime.now()}] 开始同步净值数据...")
    
    # 从环境变量获取数据库URL
    db_url = os.getenv('DATABASE_URL')
    if not db_url:
        print("错误：未设置DATABASE_URL环境变量")
        return False
    
    try:
        # 抓取最新净值（仅更新增量数据）
        fetcher = HistoryNavFetcher(db_url=db_url)
        details = fetcher.import_enabled_plans()
        
        success_count = sum(1 for d in details if d['success'])
        print(f"✓ 净值同步完成: {success_count}/{len(details)} 个基金成功")
        
        # 更新待确认交易
        print("\n更新待确认交易...")
        process_pending_records(db_url=db_url)
        print("✓ 待确认交易更新完成")
        
        return True
    except Exception as e:
        print(f"✗ 同步失败: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == '__main__':
    success = sync_nav_data()
    sys.exit(0 if success else 1)

"""
本地数据库维护工具
用于本地开发和测试，不应在生产环境使用
"""
import sys
import os

# 添加项目根目录到路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'Web', 'backend'))

from fetch_history_nav import fetch_nav_history
from import_transactions import import_from_csv
from update_pending_transactions import process_pending_records
from tradeDate import TradeDateChecker

def main():
    """本地开发用的简化版基金管理工具"""
    print("=" * 50)
    print("NDX 基金管理系统 - 本地开发工具")
    print("=" * 50)
    print("\n注意：此工具仅用于本地开发，生产环境请使用Web界面")
    print()
    
    # 使用环境变量或默认的PostgreSQL连接
    db_url = os.getenv('DATABASE_URL', 'postgresql://localhost:5432/ndx')
    
    while True:
        print("\n可用操作：")
        print("1. 抓取历史净值")
        print("2. 导入CSV交易记录")
        print("3. 更新待确认交易")
        print("4. 检查交易日")
        print("0. 退出")
        
        choice = input("\n请选择操作 (0-4): ").strip()
        
        if choice == '0':
            print("退出程序")
            break
        elif choice == '1':
            print("\n开始抓取历史净值...")
            try:
                fetch_nav_history(db_path=db_url)
                print("✓ 历史净值抓取完成")
            except Exception as e:
                print(f"✗ 抓取失败: {e}")
        elif choice == '2':
            csv_file = input("请输入CSV文件路径 (默认: transactions.csv): ").strip() or 'transactions.csv'
            try:
                import_from_csv(csv_file=csv_file, db_path=db_url)
                print("✓ 交易记录导入完成")
            except Exception as e:
                print(f"✗ 导入失败: {e}")
        elif choice == '3':
            try:
                process_pending_records(db_url=db_url)
                print("✓ 待确认交易更新完成")
            except Exception as e:
                print(f"✗ 更新失败: {e}")
        elif choice == '4':
            date_str = input("请输入日期 (YYYY-MM-DD): ").strip()
            try:
                from datetime import datetime
                date = datetime.strptime(date_str, '%Y-%m-%d')
                checker = TradeDateChecker()
                is_trading = checker.is_trading_day(date)
                print(f"{date_str} 是{'交易日' if is_trading else '非交易日'}")
            except Exception as e:
                print(f"✗ 检查失败: {e}")
        else:
            print("无效选择，请重试")

if __name__ == '__main__':
    main()

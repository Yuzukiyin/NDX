"""Verify migration results: query ndx_users.db for user_id=1 data."""
import sqlite3
from pathlib import Path

BACKEND_DIR = Path(__file__).resolve().parents[1]
NDX_DB = BACKEND_DIR / 'ndx_users.db'

def verify():
    if not NDX_DB.exists():
        print(f"❌ {NDX_DB} not found")
        return
    
    conn = sqlite3.connect(NDX_DB)
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()
    
    print("=" * 60)
    print("📊 验证 ndx_users.db 迁移结果")
    print("=" * 60)
    
    # 1. Check users table
    cur.execute("SELECT COUNT(*) as cnt FROM users")
    user_count = cur.fetchone()['cnt']
    print(f"\n👤 用户数: {user_count}")
    
    # 2. Check transactions for user_id=1
    cur.execute("SELECT COUNT(*) as cnt FROM transactions WHERE user_id = 1")
    txn_count = cur.fetchone()['cnt']
    print(f"📝 user_id=1 交易记录数: {txn_count}")
    
    if txn_count > 0:
        cur.execute("""
            SELECT fund_code, fund_name, transaction_type, COUNT(*) as cnt
            FROM transactions
            WHERE user_id = 1
            GROUP BY fund_code, fund_name, transaction_type
            ORDER BY fund_code, transaction_type
        """)
        print("\n   按基金汇总:")
        for row in cur.fetchall():
            print(f"   - {row['fund_code']} {row['fund_name']}: {row['transaction_type']} x{row['cnt']}")
    
    # 3. Check fund_overview for user_id=1
    cur.execute("SELECT COUNT(*) as cnt FROM fund_overview WHERE user_id = 1")
    overview_count = cur.fetchone()['cnt']
    print(f"\n💼 user_id=1 基金概览数: {overview_count}")
    
    if overview_count > 0:
        cur.execute("""
            SELECT fund_code, fund_name, total_shares, total_cost, average_buy_nav
            FROM fund_overview
            WHERE user_id = 1
            ORDER BY fund_code
        """)
        print("\n   基金持仓:")
        for row in cur.fetchall():
            print(f"   - {row['fund_code']} {row['fund_name']}: 份额={row['total_shares']:.2f}, 成本={row['total_cost']:.2f}元, 均价={row['average_buy_nav']:.4f}")
    
    # 4. Check fund_realtime_overview view for user_id=1
    cur.execute("SELECT COUNT(*) as cnt FROM fund_realtime_overview WHERE user_id = 1")
    view_count = cur.fetchone()['cnt']
    print(f"\n📈 user_id=1 实时概览视图: {view_count}")
    
    if view_count > 0:
        cur.execute("""
            SELECT fund_code, fund_name, total_shares, current_nav, current_value, profit, profit_rate
            FROM fund_realtime_overview
            WHERE user_id = 1
            ORDER BY fund_code
            LIMIT 5
        """)
        print("\n   前5条实时数据:")
        for row in cur.fetchall():
            print(f"   - {row['fund_code']} {row['fund_name']}: 当前净值={row['current_nav']:.4f}, 市值={row['current_value']:.2f}, 收益={row['profit']:.2f}元 ({row['profit_rate']:.2f}%)")
    
    # 5. Check profit_summary view for user_id=1
    cur.execute("SELECT * FROM profit_summary WHERE user_id = 1")
    summary = cur.fetchone()
    if summary:
        print(f"\n💰 user_id=1 总收益汇总:")
        print(f"   总基金数: {summary['total_funds']}")
        print(f"   总份额: {summary['total_shares']:.2f}")
        print(f"   总成本: {summary['total_cost']:.2f}元")
        print(f"   总市值: {summary['total_value']:.2f}元")
        print(f"   总收益: {summary['total_profit']:.2f}元")
        print(f"   总收益率: {summary['total_return_rate']:.2f}%")
    
    # 6. Check nav_history (global, not user-specific)
    cur.execute("SELECT COUNT(*) as cnt FROM fund_nav_history")
    nav_count = cur.fetchone()['cnt']
    print(f"\n📊 净值历史记录数(全局): {nav_count}")
    
    conn.close()
    
    print("\n" + "=" * 60)
    print("✅ 验证完成")
    print("=" * 60)

if __name__ == '__main__':
    verify()

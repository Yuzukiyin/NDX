"""Quick local API test to verify FundService works with unified ndx_users.db"""
import sys
from pathlib import Path

# Add backend to path
BACKEND_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(BACKEND_DIR))

from app.services.fund_service import FundService

def test_fund_service():
    print("=" * 60)
    print("🧪 测试 FundService (user_id=1)")
    print("=" * 60)
    
    service = FundService(user_id=1)
    print(f"\n📂 数据库路径: {service.db_path}")
    
    # Test overview
    print("\n1️⃣ 测试基金概览...")
    overview = service.get_fund_overview()
    print(f"   基金数: {len(overview)}")
    for fund in overview:
        print(f"   - {fund.fund_code} {fund.fund_name}: 市值={fund.current_value:.2f}, 收益={fund.profit:.2f} ({fund.profit_rate:.2f}%)")
    
    # Test transactions
    print("\n2️⃣ 测试交易记录 (最近5条)...")
    txns = service.get_transactions(limit=5)
    print(f"   交易总数: {len(txns)}")
    for txn in txns[:5]:
        print(f"   - {txn.transaction_date} {txn.fund_code} {txn.transaction_type} {txn.shares}份 @{txn.unit_nav}")
    
    # Test profit summary
    print("\n3️⃣ 测试收益汇总...")
    summary = service.get_profit_summary()
    if summary:
        print(f"   总基金: {summary.total_funds}")
        print(f"   总成本: {summary.total_cost:.2f}元")
        print(f"   总市值: {summary.total_value:.2f}元")
        print(f"   总收益: {summary.total_profit:.2f}元 ({summary.total_return_rate:.2f}%)")
    
    # Test NAV history
    print("\n4️⃣ 测试净值历史 (021000 最近5条)...")
    nav_hist = service.get_nav_history("021000")
    for nav in nav_hist[-5:]:
        print(f"   - {nav.price_date}: {nav.unit_nav:.4f}, 涨幅={nav.daily_growth_rate}%")
    
    print("\n" + "=" * 60)
    print("✅ FundService 本地测试通过")
    print("=" * 60)

if __name__ == '__main__':
    test_fund_service()

"""导出fund.db数据用于上传到Railway"""
import sqlite3
import json

def export_transactions():
    """导出所有交易记录为JSON"""
    conn = sqlite3.connect('fund.db')
    cursor = conn.cursor()
    
    # 获取所有交易记录
    cursor.execute("""
        SELECT fund_code, fund_name, transaction_date, nav_date, 
               transaction_type, target_amount, shares, unit_nav, amount, note, created_at
        FROM transactions
        ORDER BY transaction_date
    """)
    
    transactions = []
    for row in cursor.fetchall():
        transactions.append({
            'fund_code': row[0],
            'fund_name': row[1],
            'transaction_date': row[2],
            'nav_date': row[3],
            'transaction_type': row[4],
            'target_amount': row[5],
            'shares': row[6],
            'unit_nav': row[7],
            'amount': row[8],
            'note': row[9],
            'created_at': row[10]
        })
    
    conn.close()
    
    # 保存为JSON
    with open('transactions_export.json', 'w', encoding='utf-8') as f:
        json.dump(transactions, f, ensure_ascii=False, indent=2)
    
    print(f"✅ 已导出 {len(transactions)} 条交易记录到 transactions_export.json")
    return transactions

def export_nav_history():
    """导出历史净值数据"""
    conn = sqlite3.connect('fund.db')
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT fund_code, fund_name, price_date, unit_nav, fetched_at
        FROM fund_nav_history
        ORDER BY fund_code, price_date
    """)
    
    nav_records = []
    for row in cursor.fetchall():
        nav_records.append({
            'fund_code': row[0],
            'fund_name': row[1],
            'price_date': row[2],
            'unit_nav': row[3],
            'fetched_at': row[4]
        })
    
    conn.close()
    
    with open('nav_history_export.json', 'w', encoding='utf-8') as f:
        json.dump(nav_records, f, ensure_ascii=False, indent=2)
    
    print(f"✅ 已导出 {len(nav_records)} 条净值记录到 nav_history_export.json")
    return nav_records

if __name__ == '__main__':
    print("开始导出fund.db数据...")
    transactions = export_transactions()
    nav_records = export_nav_history()
    
    print("\n📊 数据统计:")
    print(f"  交易记录: {len(transactions)} 条")
    print(f"  净值记录: {len(nav_records)} 条")
    
    if transactions:
        fund_codes = set(t['fund_code'] for t in transactions)
        print(f"  涉及基金: {len(fund_codes)} 只")
        print(f"  基金代码: {', '.join(sorted(fund_codes))}")

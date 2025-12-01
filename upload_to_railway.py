"""上传本地fund.db数据到Railway"""
import requests
import json
import sys

# Railway后端URL
BACKEND_URL = "https://ndx-production.up.railway.app"

def login():
    """登录获取token"""
    response = requests.post(f"{BACKEND_URL}/auth/login", json={
        "email": "1712008344@qq.com",
        "password": "Lzy171200"
    })
    
    if response.status_code == 200:
        data = response.json()
        print("✅ 登录成功")
        return data['access_token']
    else:
        print(f"❌ 登录失败: {response.text}")
        sys.exit(1)

def upload_transactions(token):
    """上传交易记录"""
    with open('transactions_export.json', 'r', encoding='utf-8') as f:
        transactions = json.load(f)
    
    headers = {"Authorization": f"Bearer {token}"}
    
    print(f"\n开始上传 {len(transactions)} 条交易记录...")
    success = 0
    failed = 0
    
    for trans in transactions:
        response = requests.post(
            f"{BACKEND_URL}/funds/transactions",
            headers=headers,
            json=trans
        )
        
        if response.status_code in [200, 201]:
            success += 1
            print(f"✓ {trans['transaction_date']} {trans['fund_code']} {trans['transaction_type']} ¥{trans['amount']}")
        else:
            failed += 1
            print(f"✗ 失败: {response.text}")
    
    print(f"\n交易记录上传完成: 成功{success}条, 失败{failed}条")

def upload_nav_history(token):
    """上传净值历史"""
    with open('nav_history_export.json', 'r', encoding='utf-8') as f:
        nav_records = json.load(f)
    
    headers = {"Authorization": f"Bearer {token}"}
    
    print(f"\n开始上传 {len(nav_records)} 条净值记录...")
    
    # 批量上传
    response = requests.post(
        f"{BACKEND_URL}/funds/nav-history/batch",
        headers=headers,
        json=nav_records
    )
    
    if response.status_code in [200, 201]:
        print(f"✅ 净值历史上传成功")
    else:
        print(f"❌ 净值历史上传失败: {response.text}")

if __name__ == '__main__':
    print("=" * 60)
    print("上传本地fund.db数据到Railway")
    print("=" * 60)
    
    token = login()
    upload_transactions(token)
    upload_nav_history(token)
    
    print("\n🎉 数据上传完成!")

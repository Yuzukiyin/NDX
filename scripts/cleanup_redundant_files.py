"""
清理脚本 - 移除根目录的冗余文件
这些文件的功能已被Web应用取代或移至scripts目录
"""
import os
import shutil

# 要删除的冗余文件
FILES_TO_REMOVE = [
    'AAAfund_manager.py',  # 已被scripts/local_manager.py取代
    'check_db.py',  # 已过时
    'check_fund_db.py',  # 已过时
    'export_fund_data.py',  # 已过时
    'fetch_history_nav.py',  # Web/backend已有
    'import_transactions.py',  # Web/backend已有
    'import_auto_invest.py',  # 功能已集成到后端
    'init_database.py',  # Web/backend已有
    'nav_plot.py',  # 已过时
    'tradeDate.py',  # Web/backend已有
    'update_pending_transactions.py',  # Web/backend已有
    'upload_to_railway.py',  # 已过时（Railway自动部署）
    
    # 导出的数据文件（可重新生成）
    'bought.sql',
    'nav_history_export.json',
    'transactions_export.json',
    'transactions_new.csv',
    'transactions_old.csv',
    
    # 数据库文件（本地开发用，生产用PostgreSQL）
    'fund.db',
    'ndx_users.db',
    
    # 旧的requirements（Web/backend已有）
    'requirements.txt',
]

def main():
    """清理冗余文件"""
    root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    
    print("=" * 60)
    print("NDX项目清理 - 移除冗余文件")
    print("=" * 60)
    print(f"\n项目根目录: {root_dir}\n")
    print("将要删除以下文件：")
    
    files_found = []
    for filename in FILES_TO_REMOVE:
        filepath = os.path.join(root_dir, filename)
        if os.path.exists(filepath):
            files_found.append((filename, filepath))
            size = os.path.getsize(filepath)
            print(f"  - {filename} ({size:,} bytes)")
    
    if not files_found:
        print("  (没有找到需要删除的文件)")
        return
    
    print(f"\n共 {len(files_found)} 个文件")
    print("\n注意：")
    print("  1. 这些文件的功能已被Web应用或scripts目录取代")
    print("  2. 删除前建议先提交当前更改到Git")
    print("  3. .db文件会被删除，但数据已迁移到PostgreSQL")
    print("  4. 导出文件可以随时重新生成")
    
    confirm = input("\n确认删除？(yes/no): ").strip().lower()
    
    if confirm != 'yes':
        print("已取消删除")
        return
    
    print("\n开始删除...")
    success_count = 0
    error_count = 0
    
    for filename, filepath in files_found:
        try:
            os.remove(filepath)
            print(f"  ✓ 已删除: {filename}")
            success_count += 1
        except Exception as e:
            print(f"  ✗ 删除失败: {filename} - {e}")
            error_count += 1
    
    print(f"\n完成！成功: {success_count}, 失败: {error_count}")
    
    if success_count > 0:
        print("\n建议执行：")
        print("  git add .")
        print("  git commit -m 'refactor: 清理冗余文件，统一使用Web应用'")

if __name__ == '__main__':
    main()

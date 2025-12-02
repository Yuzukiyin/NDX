"""
统一的数据库管理脚本
用于初始化、备份、恢复数据库
"""
import sys
import os
import asyncio
from datetime import datetime
from pathlib import Path

# 添加项目路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'Web', 'backend'))

async def init_database():
    """初始化数据库结构"""
    print("初始化数据库...")
    from app.utils.database import init_db
    
    try:
        await init_db()
        print("✓ 数据库初始化完成")
        return True
    except Exception as e:
        print(f"✗ 初始化失败: {e}")
        import traceback
        traceback.print_exc()
        return False

async def create_admin():
    """创建管理员账户"""
    print("\n创建管理员账户...")
    
    from app.utils.database import async_session_factory
    from app.models.user import User
    from app.utils.auth import get_password_hash
    from sqlalchemy import select
    
    email = input("管理员邮箱: ").strip()
    username = input("管理员用户名: ").strip()
    password = input("管理员密码: ").strip()
    
    if not email or not username or not password:
        print("✗ 所有字段都必须填写")
        return False
    
    try:
        async with async_session_factory() as session:
            # 检查是否已存在
            result = await session.execute(
                select(User).where(User.email == email)
            )
            if result.scalar_one_or_none():
                print(f"✗ 邮箱 {email} 已存在")
                return False
            
            # 创建管理员
            admin = User(
                email=email,
                username=username,
                hashed_password=get_password_hash(password),
                is_active=True,
                is_verified=True
            )
            session.add(admin)
            await session.commit()
            
            print(f"✓ 管理员账户创建成功: {username} ({email})")
            return True
    except Exception as e:
        print(f"✗ 创建失败: {e}")
        import traceback
        traceback.print_exc()
        return False

async def backup_database():
    """备份数据库（PostgreSQL）"""
    print("\n备份数据库...")
    
    db_url = os.getenv('DATABASE_URL')
    if not db_url:
        print("✗ 未设置DATABASE_URL环境变量")
        return False
    
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    backup_file = f"backup_{timestamp}.sql"
    
    print(f"备份文件: {backup_file}")
    
    try:
        import subprocess
        # 使用pg_dump备份
        subprocess.run(
            ['pg_dump', db_url, '-f', backup_file],
            check=True
        )
        
        file_size = os.path.getsize(backup_file)
        print(f"✓ 备份完成: {backup_file} ({file_size:,} bytes)")
        return True
    except subprocess.CalledProcessError as e:
        print(f"✗ 备份失败: {e}")
        return False
    except FileNotFoundError:
        print("✗ pg_dump未安装，请安装PostgreSQL客户端工具")
        return False

async def show_stats():
    """显示数据库统计信息"""
    print("\n数据库统计...")
    
    from app.utils.database import async_session_factory
    from sqlalchemy import text
    
    try:
        async with async_session_factory() as session:
            # 用户数
            result = await session.execute(text("SELECT COUNT(*) FROM users"))
            users_count = result.scalar()
            
            # 定投计划数
            result = await session.execute(text("SELECT COUNT(*) FROM auto_invest_plans"))
            plans_count = result.scalar()
            
            # 交易记录数
            result = await session.execute(text("SELECT COUNT(*) FROM transactions"))
            trans_count = result.scalar()
            
            # 净值记录数
            result = await session.execute(text("SELECT COUNT(*) FROM fund_nav_history"))
            nav_count = result.scalar()
            
            print("\n" + "=" * 40)
            print(f"用户数:        {users_count:>10,}")
            print(f"定投计划:      {plans_count:>10,}")
            print(f"交易记录:      {trans_count:>10,}")
            print(f"净值记录:      {nav_count:>10,}")
            print("=" * 40)
            
            return True
    except Exception as e:
        print(f"✗ 查询失败: {e}")
        return False

async def reset_database():
    """重置数据库（危险操作）"""
    print("\n⚠️  警告：此操作将删除所有数据！")
    confirm1 = input("确认重置数据库？(yes/no): ").strip().lower()
    if confirm1 != 'yes':
        print("已取消")
        return False
    
    confirm2 = input("再次确认，输入 'DELETE ALL DATA': ").strip()
    if confirm2 != 'DELETE ALL DATA':
        print("已取消")
        return False
    
    from app.utils.database import engine, Base
    from app.models.user import Base as UserBase
    
    try:
        async with engine.begin() as conn:
            await conn.run_sync(UserBase.metadata.drop_all)
            print("✓ 表已删除")
            
            await conn.run_sync(UserBase.metadata.create_all)
            print("✓ 表已重建")
        
        print("✓ 数据库重置完成")
        return True
    except Exception as e:
        print(f"✗ 重置失败: {e}")
        return False

def main():
    """主菜单"""
    print("=" * 50)
    print("NDX 数据库管理工具")
    print("=" * 50)
    
    # 检查环境变量
    if not os.getenv('DATABASE_URL'):
        print("\n⚠️  警告：未设置DATABASE_URL环境变量")
        print("请设置后再使用本工具")
        return
    
    while True:
        print("\n操作选项：")
        print("1. 初始化数据库（创建表结构）")
        print("2. 创建管理员账户")
        print("3. 显示数据库统计")
        print("4. 备份数据库")
        print("5. 重置数据库（危险）")
        print("0. 退出")
        
        choice = input("\n请选择 (0-5): ").strip()
        
        if choice == '0':
            print("退出程序")
            break
        elif choice == '1':
            asyncio.run(init_database())
        elif choice == '2':
            asyncio.run(create_admin())
        elif choice == '3':
            asyncio.run(show_stats())
        elif choice == '4':
            asyncio.run(backup_database())
        elif choice == '5':
            asyncio.run(reset_database())
        else:
            print("无效选择")

if __name__ == '__main__':
    main()

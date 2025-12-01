"""初始化管理员账户脚本"""
import asyncio
import sys
from pathlib import Path

# 添加父目录到路径
sys.path.insert(0, str(Path(__file__).parent))

from app.utils.database import init_db, async_session_factory
from app.models.user import User
from app.utils.auth import get_password_hash
from sqlalchemy import select


async def create_admin_user():
    """创建初始管理员账户"""
    # 初始化数据库
    await init_db()
    
    async with async_session_factory() as session:
        # 检查用户是否已存在
        result = await session.execute(
            select(User).where(User.email == "1712008344@qq.com")
        )
        existing_user = result.scalar_one_or_none()
        
        if existing_user:
            print("✅ 管理员账户已存在")
            print(f"   邮箱: {existing_user.email}")
            print(f"   用户名: {existing_user.username}")
            return
        
        # 创建新用户
        admin_user = User(
            email="1712008344@qq.com",
            username="admin",
            hashed_password=get_password_hash("Lzy171200"),
            is_active=True,
            is_verified=True
        )
        
        session.add(admin_user)
        await session.commit()
        await session.refresh(admin_user)
        
        print("✅ 管理员账户创建成功!")
        print(f"   邮箱: {admin_user.email}")
        print(f"   用户名: {admin_user.username}")
        print(f"   密码: Lzy171200")
        print(f"   用户ID: {admin_user.id}")


if __name__ == "__main__":
    print("🚀 初始化管理员账户...")
    asyncio.run(create_admin_user())
    print("✨ 完成!")

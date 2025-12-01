"""一键启动脚本 - 创建管理员账户并启动服务"""
import asyncio
import subprocess
import sys
import os
from pathlib import Path

async def main():
    """主函数"""
    print("=" * 60)
    print("🚀 NDX基金管理系统 - 启动脚本")
    print("=" * 60)
    
    # 1. 创建管理员账户
    print("\n📝 步骤1: 初始化管理员账户...")
    from init_admin import create_admin_user
    await create_admin_user()
    
    # 2. 同步定投配置
    print("\n📊 步骤2: 同步定投配置...")
    try:
        from sync_auto_invest_config import sync_config_to_db
        backend_dir = Path(__file__).parent
        sync_config_to_db(
            config_path=str(backend_dir / 'auto_invest_setting.json'),
            db_path=str(backend_dir / 'ndx_users.db'),
            user_id=1
        )
    except Exception as e:
        print(f"⚠ 同步定投配置失败: {e}")
    
    # 3. 启动服务
    print("\n🌐 步骤3: 启动后端服务...")
    print("   访问地址: http://localhost:8000")
    print("   API文档: http://localhost:8000/docs")
    print("\n   管理员账户:")
    print("   邮箱: 1712008344@qq.com")
    print("   密码: Lzy171200")
    print("\n" + "=" * 60)
    print("按 Ctrl+C 停止服务")
    print("=" * 60 + "\n")
    
    # 启动uvicorn
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=int(os.environ.get("PORT", 8000)),
        reload=True if os.environ.get("RAILWAY_ENVIRONMENT") is None else False,
        log_level="info"
    )

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n\n👋 服务已停止")
        sys.exit(0)

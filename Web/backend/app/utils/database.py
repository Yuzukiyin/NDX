"""数据库连接与会话管理"""
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import declarative_base
from ..config import settings
from pathlib import Path

# 创建异步引擎
engine = create_async_engine(
    settings.database_url_async,
    echo=settings.DEBUG,
    future=True
)

# 创建会话工厂
async_session_factory = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False
)

Base = declarative_base()


async def get_db():
    """获取数据库会话的依赖"""
    async with async_session_factory() as session:
        try:
            yield session
        finally:
            await session.close()


async def init_db():
    """初始化数据库表"""
    from ..models.user import Base
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
        # 基金相关表初始化（支持 SQLite / PostgreSQL）
        try:
            db_url = settings.database_url_async.lower()
            schema_dir = Path(__file__).parent.parent / 'db'
            if 'sqlite' in db_url:
                res = await conn.exec_driver_sql(
                    "SELECT name FROM sqlite_master WHERE type='table' AND name='fund_overview'"
                )
                if res.fetchone() is None:
                    schema_path = schema_dir / 'fund_multitenant.sql'
                    sql = schema_path.read_text(encoding='utf-8')
                    await conn.exec_driver_sql(sql)
                    print("✅ Fund schema initialized (SQLite)")
            elif 'postgresql' in db_url:
                schema_path = schema_dir / 'fund_multitenant_postgres.sql'
                sql = schema_path.read_text(encoding='utf-8')
                await conn.exec_driver_sql(sql)
                print("✅ Fund schema initialized (PostgreSQL)")
            else:
                print("⚠️ Unsupported database for fund schema initialization")
        except Exception as e:
            print(f"⚠️ Fund schema init error: {e}")

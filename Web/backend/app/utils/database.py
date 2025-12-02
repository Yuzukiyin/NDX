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
    """初始化数据库表（仅支持PostgreSQL）"""
    from ..models.user import Base
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
        # 基金相关表初始化（PostgreSQL）
        try:
            from sqlalchemy import create_engine
            sync_engine = create_engine(settings.database_url_sync, future=True)
            schema_dir = Path(__file__).parent.parent / 'db'
            schema_path = schema_dir / 'fund_multitenant_postgres.sql'
            sql = schema_path.read_text(encoding='utf-8')
            
            with sync_engine.connect() as sync_conn:
                # 使用 psycopg2 的 raw connection 执行多语句 SQL
                raw_conn = sync_conn.connection
                cursor = raw_conn.cursor()
                cursor.execute(sql)
                raw_conn.commit()
                cursor.close()
            print("✅ Fund schema initialized (PostgreSQL)")
        except Exception as e:
            print(f"⚠️ Fund schema init error: {e}")

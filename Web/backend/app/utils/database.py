"""Database connection and session management"""
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import declarative_base
from ..config import settings
from pathlib import Path

# Create async engine
engine = create_async_engine(
    settings.database_url_async,
    echo=settings.DEBUG,
    future=True
)

# Create session factory
async_session_factory = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False
)

Base = declarative_base()


async def get_db():
    """Dependency to get database session"""
    async with async_session_factory() as session:
        try:
            yield session
        finally:
            await session.close()


async def init_db():
    """Initialize database tables"""
    from ..models.user import Base
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
        # Fund tables initialization - only for SQLite
        # PostgreSQL will skip this since SQL file contains SQLite-specific syntax
        try:
            db_url = settings.database_url_async.lower()
            if 'sqlite' in db_url:
                # Only initialize fund tables for SQLite
                res = await conn.exec_driver_sql(
                    "SELECT name FROM sqlite_master WHERE type='table' AND name='fund_overview'"
                )
                if res.fetchone() is None:
                    schema_path = Path(__file__).parent.parent / 'db' / 'fund_multitenant.sql'
                    sql = schema_path.read_text(encoding='utf-8')
                    await conn.exec_driver_sql(sql)
                    print("✅ Fund schema initialized (SQLite)")
            else:
                # PostgreSQL: skip fund table initialization for now
                # TODO: Create PostgreSQL-compatible fund schema
                print("⚠️ Fund schema skipped for PostgreSQL (not implemented yet)")
        except Exception as e:
            print(f"⚠️ Fund schema init error: {e}")

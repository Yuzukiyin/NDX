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
        # Ensure fund tables exist in the same SQLite file
        try:
            # Detect if fund_overview exists; if not, apply schema
            res = await conn.exec_driver_sql("SELECT name FROM sqlite_master WHERE type='table' AND name='fund_overview'")
            if res.fetchone() is None:
                schema_path = Path(__file__).parent.parent / 'db' / 'fund_multitenant.sql'
                sql = schema_path.read_text(encoding='utf-8')
                await conn.exec_driver_sql(sql)
        except Exception as e:
            # Log and continue. FundService can also initialize on demand if needed.
            print(f"⚠️ Fund schema init skipped: {e}")

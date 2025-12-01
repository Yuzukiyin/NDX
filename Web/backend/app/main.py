"""Main FastAPI application"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from .config import settings
from .utils.database import init_db, async_session_factory
from .routes import auth, funds


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan - startup and shutdown events"""
    # Startup
    await init_db()
    print("✅ Database initialized")
    # Auto-create admin on first boot if env provided and no users yet
    try:
        from sqlalchemy import select, func
        from .models.user import User
        from .utils.auth import get_password_hash
        from .config import settings as _settings

        if _settings.ADMIN_EMAIL and _settings.ADMIN_PASSWORD:
            async with async_session_factory() as session:
                res = await session.execute(select(func.count(User.id)))
                count = res.scalar_one() or 0
                if count == 0:
                    user = User(
                        email=_settings.ADMIN_EMAIL,
                        username=_settings.ADMIN_USERNAME or "admin",
                        hashed_password=get_password_hash(_settings.ADMIN_PASSWORD),
                        is_active=True,
                        is_verified=True,
                    )
                    session.add(user)
                    await session.commit()
                    print("✅ Admin user auto-created on startup")
    except Exception as e:
        print(f"⚠️ Admin bootstrap skipped: {e}")
    yield
    # Shutdown
    print("👋 Shutting down...")


# Create FastAPI app
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.VERSION,
    description="NDX基金管理系统 Web API",
    lifespan=lifespan
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://localhost:3001",
        "http://localhost:5173",
        "http://127.0.0.1:3000",
        "http://127.0.0.1:3001",
        "http://127.0.0.1:5173",
    ],
    allow_origin_regex=r"https://.*\.vercel\.app",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth.router)
app.include_router(funds.router)


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "app": settings.APP_NAME,
        "version": settings.VERSION,
        "status": "running"
    }


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy"}

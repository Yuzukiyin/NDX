"""Auto-invest plan routes"""
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
from ..models.auto_invest_schemas import AutoInvestPlan, AutoInvestPlanCreate, AutoInvestPlanUpdate
from ..services.auth_service import AuthService
from ..services.auto_invest_service import AutoInvestService
from ..utils.database import get_db
from ..config import settings

router = APIRouter(prefix="/auto-invest", tags=["Auto Invest"])
security = HTTPBearer()


async def get_auto_invest_service(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: AsyncSession = Depends(get_db)
) -> AutoInvestService:
    """Dependency to get auto-invest service for current user"""
    user = await AuthService.get_current_user(db, credentials.credentials)
    
    # Parse database path
    db_url = settings.database_url_async
    if db_url.startswith("sqlite+aiosqlite:///"):
        db_path = db_url.replace("sqlite+aiosqlite:///", "")
    elif db_url.startswith("sqlite:///"):
        db_path = db_url.replace("sqlite:///", "")
    else:
        db_path = "./ndx_users.db"
    
    return AutoInvestService(user.id, db_path)


@router.get("/plans", response_model=List[AutoInvestPlan])
async def get_all_plans(
    service: AutoInvestService = Depends(get_auto_invest_service)
):
    """Get all auto-invest plans"""
    try:
        return service.get_all_plans()
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取定投计划失败: {str(e)}"
        )


@router.get("/plans/{plan_id}", response_model=AutoInvestPlan)
async def get_plan(
    plan_id: int,
    service: AutoInvestService = Depends(get_auto_invest_service)
):
    """Get specific auto-invest plan"""
    plan = service.get_plan(plan_id)
    if not plan:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="定投计划不存在"
        )
    return plan


@router.post("/plans", response_model=AutoInvestPlan, status_code=status.HTTP_201_CREATED)
async def create_plan(
    plan: AutoInvestPlanCreate,
    service: AutoInvestService = Depends(get_auto_invest_service)
):
    """Create new auto-invest plan"""
    try:
        return service.create_plan(plan)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"创建定投计划失败: {str(e)}"
        )


@router.patch("/plans/{plan_id}", response_model=AutoInvestPlan)
async def update_plan(
    plan_id: int,
    update: AutoInvestPlanUpdate,
    service: AutoInvestService = Depends(get_auto_invest_service)
):
    """Update auto-invest plan"""
    try:
        plan = service.update_plan(plan_id, update)
        if not plan:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="定投计划不存在"
            )
        return plan
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"更新定投计划失败: {str(e)}"
        )


@router.delete("/plans/{plan_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_plan(
    plan_id: int,
    service: AutoInvestService = Depends(get_auto_invest_service)
):
    """Delete auto-invest plan"""
    if not service.delete_plan(plan_id):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="定投计划不存在"
        )


@router.post("/plans/{plan_id}/toggle", response_model=AutoInvestPlan)
async def toggle_plan(
    plan_id: int,
    service: AutoInvestService = Depends(get_auto_invest_service)
):
    """Toggle plan enabled status"""
    plan = service.toggle_plan(plan_id)
    if not plan:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="定投计划不存在"
        )
    return plan

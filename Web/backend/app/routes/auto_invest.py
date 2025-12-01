"""Auto-invest plan routes"""
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
from datetime import datetime, timedelta
from pathlib import Path
from ..models.auto_invest_schemas import AutoInvestPlan, AutoInvestPlanCreate, AutoInvestPlanUpdate
from ..services.auth_service import AuthService
from ..services.auto_invest_service import AutoInvestService
from ..utils.database import get_db
from ..config import settings
import sys

# Add parent directory to path for original modules
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))

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


@router.post("/execute-today")
async def execute_today_plans(
    service: AutoInvestService = Depends(get_auto_invest_service)
):
    """Execute auto-invest plans for today"""
    try:
        # Get today's date
        today = datetime.now().strftime('%Y-%m-%d')
        today_dt = datetime.now()
        
        # Simple trading day check (weekdays only)
        is_weekend = today_dt.weekday() >= 5
        if is_weekend:
            return {"message": f"{today} 是周末，非交易日", "transactions_created": 0}
        
        # Get database path
        db_url = settings.database_url_async
        if db_url.startswith("sqlite+aiosqlite:///"):
            db_path = db_url.replace("sqlite+aiosqlite:///", "")
        elif db_url.startswith("sqlite:///"):
            db_path = db_url.replace("sqlite:///", "")
        else:
            db_path = "./ndx_users.db"
        
        # Get all enabled plans from database
        enabled_plans = service.get_all_plans()
        enabled_plans = [p for p in enabled_plans if p.enabled]
        
        if not enabled_plans:
            return {"message": "没有启用的定投计划", "transactions_created": 0}
        
        # Generate transactions for enabled plans
        import sqlite3
        transactions_created = 0
        
        conn = sqlite3.connect(db_path)
        cur = conn.cursor()
        
        for plan in enabled_plans:
            # Check if plan should execute today based on frequency
            start_date = datetime.strptime(plan.start_date, '%Y-%m-%d')
            end_date = datetime.strptime(plan.end_date, '%Y-%m-%d')
            
            if not (start_date <= today_dt <= end_date):
                continue
            
            should_execute = False
            if plan.frequency == 'daily':
                should_execute = True
            elif plan.frequency == 'weekly':
                should_execute = (today_dt.weekday() == start_date.weekday())
            elif plan.frequency == 'monthly':
                should_execute = (today_dt.day == start_date.day)
            
            if should_execute:
                # Calculate T+1 confirm date (next weekday)
                confirm_dt = today_dt + timedelta(days=1)
                while confirm_dt.weekday() >= 5:
                    confirm_dt += timedelta(days=1)
                confirm_date = confirm_dt.strftime('%Y-%m-%d')
                
                # Check if transaction already exists
                cur.execute("""
                    SELECT COUNT(*) FROM transactions
                    WHERE user_id = ? AND fund_code = ? AND transaction_date = ?
                """, (service.user_id, plan.fund_code, today))
                
                if cur.fetchone()[0] == 0:
                    cur.execute("""
                        INSERT INTO transactions (
                            user_id, fund_code, fund_name, transaction_date, 
                            nav_date, transaction_type, target_amount, note
                        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                    """, (
                        service.user_id,
                        plan.fund_code,
                        plan.fund_name,
                        today,
                        confirm_date,
                        '买入',
                        plan.amount,
                        f"[待确认] {plan.plan_name}"
                    ))
                    transactions_created += 1
        
        conn.commit()
        conn.close()
        
        return {
            "message": f"成功创建 {transactions_created} 条定投交易记录",
            "transactions_created": transactions_created,
            "date": today
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"执行定投计划失败: {str(e)}"
        )

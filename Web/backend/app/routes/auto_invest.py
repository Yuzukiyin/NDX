"""Auto-invest plan routes"""
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
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
    return AutoInvestService(user.id)


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
    """Execute auto-invest plans from start date to today (补齐所有缺失记录)"""
    try:
        from sqlalchemy import create_engine, text
        from sqlalchemy.orm import sessionmaker
        import sys
        backend_dir = Path(__file__).parent.parent.parent
        if str(backend_dir) not in sys.path:
            sys.path.insert(0, str(backend_dir))
        from tradeDate import TradeDateChecker
        
        # Get today's date
        today = datetime.now().strftime('%Y-%m-%d')
        today_dt = datetime.now()
        
        # 初始化交易日检查器
        trade_checker = TradeDateChecker(user_id=service.user_id, db_url=settings.database_url_sync)
        
        print(f"[DEBUG] 用户ID: {service.user_id}")
        
        # Get all enabled plans from database
        enabled_plans = service.get_all_plans()
        enabled_plans = [p for p in enabled_plans if p.enabled]
        
        print(f"[DEBUG] 启用的计划数: {len(enabled_plans)}")
        
        if not enabled_plans:
            return {"message": "没有启用的定投计划", "transactions_created": 0}
        
        # Use PostgreSQL connection for transaction creation
        engine = create_engine(settings.database_url_sync, future=True)
        Session = sessionmaker(bind=engine)
        
        transactions_created = 0
        skipped_count = 0
        
        with Session() as session:
            with session.begin():
                for plan in enabled_plans:
                    print(f"\n[DEBUG] 处理计划: {plan.plan_name}")
                    print(f"[DEBUG] 基金: {plan.fund_code}, 频率: {plan.frequency}")
                    
                    start_date = datetime.strptime(plan.start_date, '%Y-%m-%d')
                    end_date = datetime.strptime(plan.end_date, '%Y-%m-%d')
                    
                    # 确保不超过今天
                    if end_date > today_dt:
                        end_date = today_dt
                    
                    print(f"[DEBUG] 计划日期范围: {plan.start_date} ~ {end_date.strftime('%Y-%m-%d')}")
                    
                    # 生成所有应该定投的日期
                    plan_dates = []
                    current_date = start_date
                    
                    while current_date <= end_date:
                        # 使用交易日检查器判断是否为交易日(跳过周末和节假日)
                        if trade_checker.is_trading_day(current_date):
                            plan_dates.append(current_date)
                        
                        # 根据频率递增
                        if plan.frequency == 'daily':
                            current_date += timedelta(days=1)
                        elif plan.frequency == 'weekly':
                            current_date += timedelta(weeks=1)
                        elif plan.frequency == 'monthly':
                            current_date += relativedelta(months=1)
                        elif plan.frequency == 'quarterly':
                            current_date += relativedelta(months=3)
                        else:
                            break
                    
                    print(f"[DEBUG] 生成了 {len(plan_dates)} 个潜在定投日期")
                    
                    # 检查每个日期是否已存在交易记录
                    for trans_date in plan_dates:
                        trans_date_str = trans_date.strftime('%Y-%m-%d')
                        
                        # 检查是否已存在
                        result = session.execute(
                            text("""
                                SELECT COUNT(*) FROM transactions
                                WHERE user_id = :user_id AND fund_code = :fund_code AND transaction_date = :trans_date
                            """),
                            {"user_id": service.user_id, "fund_code": plan.fund_code, "trans_date": trans_date_str}
                        )
                        
                        exists = result.scalar()
                        
                        if exists == 0:
                            # 计算T+1确认日期(下一个交易日)
                            confirm_date = trade_checker.get_next_trading_day(trans_date, 1).strftime('%Y-%m-%d')
                            
                            session.execute(
                                text("""
                                    INSERT INTO transactions (
                                        user_id, fund_code, fund_name, transaction_date, 
                                        nav_date, transaction_type, target_amount, note
                                    ) VALUES (
                                        :user_id, :fund_code, :fund_name, :trans_date,
                                        :nav_date, :trans_type, :target_amount, :note
                                    )
                                """),
                                {
                                    "user_id": service.user_id,
                                    "fund_code": plan.fund_code,
                                    "fund_name": plan.fund_name,
                                    "trans_date": trans_date_str,
                                    "nav_date": confirm_date,
                                    "trans_type": "买入",
                                    "target_amount": plan.amount,
                                    "note": f"[待确认] {plan.plan_name}"
                                }
                            )
                            transactions_created += 1
                        else:
                            skipped_count += 1
        
        print(f"\n[DEBUG] 执行完成: 新建 {transactions_created} 条, 跳过 {skipped_count} 条")
        
        return {
            "message": f"定投计划执行完成: 新建 {transactions_created} 条记录, 跳过已存在 {skipped_count} 条",
            "transactions_created": transactions_created,
            "skipped": skipped_count,
            "date": today
        }
        
    except Exception as e:
        import traceback
        error_detail = f"执行定投计划失败: {str(e)}\n{traceback.format_exc()}"
        print(f"[ERROR] {error_detail}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=error_detail
        )

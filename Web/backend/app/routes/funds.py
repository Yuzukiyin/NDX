"""Fund data routes"""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional
from ..models.schemas import FundOverview, Transaction, NavHistory, ProfitSummary
from ..services.auth_service import AuthService
from ..services.fund_service import FundService
from ..utils.database import get_db

router = APIRouter(prefix="/funds", tags=["Funds"])
security = HTTPBearer()


async def get_current_fund_service(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: AsyncSession = Depends(get_db)
) -> FundService:
    """Dependency to get fund service for current user"""
    user = await AuthService.get_current_user(db, credentials.credentials)
    return FundService(user.id)


@router.get("/overview", response_model=List[FundOverview])
async def get_funds_overview(
    fund_service: FundService = Depends(get_current_fund_service)
):
    """Get overview of all funds"""
    try:
        return fund_service.get_fund_overview()
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取基金概览失败: {str(e)}"
        )


@router.get("/overview/{fund_code}", response_model=FundOverview)
async def get_fund_detail(
    fund_code: str,
    fund_service: FundService = Depends(get_current_fund_service)
):
    """Get detail of specific fund"""
    try:
        fund = fund_service.get_fund_detail(fund_code)
        if not fund:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="基金不存在"
            )
        return fund
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取基金详情失败: {str(e)}"
        )


@router.get("/transactions", response_model=List[Transaction])
async def get_transactions(
    fund_code: Optional[str] = Query(None, description="基金代码"),
    limit: int = Query(100, ge=1, le=1000, description="返回记录数"),
    offset: int = Query(0, ge=0, description="偏移量"),
    fund_service: FundService = Depends(get_current_fund_service)
):
    """Get transaction records"""
    try:
        return fund_service.get_transactions(fund_code, limit, offset)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取交易记录失败: {str(e)}"
        )


@router.get("/nav-history/{fund_code}", response_model=List[NavHistory])
async def get_nav_history(
    fund_code: str,
    start_date: Optional[str] = Query(None, description="开始日期 (YYYY-MM-DD)"),
    end_date: Optional[str] = Query(None, description="结束日期 (YYYY-MM-DD)"),
    fund_service: FundService = Depends(get_current_fund_service)
):
    """Get historical NAV data"""
    try:
        return fund_service.get_nav_history(fund_code, start_date, end_date)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取历史净值失败: {str(e)}"
        )


@router.get("/profit-summary", response_model=ProfitSummary)
async def get_profit_summary(
    fund_service: FundService = Depends(get_current_fund_service)
):
    """Get overall profit summary"""
    try:
        summary = fund_service.get_profit_summary()
        if not summary:
            # Return empty summary if no data
            return ProfitSummary(
                total_funds=0,
                total_shares=0,
                total_cost=0,
                total_value=0,
                total_profit=0,
                total_return_rate=0
            )
        return summary
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取收益汇总失败: {str(e)}"
        )


@router.post("/initialize-database")
async def initialize_database(
    fund_service: FundService = Depends(get_current_fund_service)
):
    """Initialize user's fund database"""
    try:
        fund_service.initialize_user_database()
        return {"message": "数据库初始化成功"}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"初始化数据库失败: {str(e)}"
        )


@router.post("/fetch-nav")
async def fetch_nav(
    fund_codes: Optional[List[str]] = None,
    fund_service: FundService = Depends(get_current_fund_service)
):
    """Fetch historical NAV data"""
    try:
        fund_service.fetch_history_nav(fund_codes)
        return {"message": "历史净值抓取完成"}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"抓取历史净值失败: {str(e)}"
        )


@router.post("/update-pending")
async def update_pending(
    fund_service: FundService = Depends(get_current_fund_service)
):
    """Update pending transactions"""
    try:
        fund_service.update_pending_transactions()
        return {"message": "待确认交易更新完成"}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"更新待确认交易失败: {str(e)}"
        )

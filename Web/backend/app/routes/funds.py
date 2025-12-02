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
    return FundService(user.id, db)


@router.get("/overview", response_model=List[FundOverview])
async def get_funds_overview(
    fund_service: FundService = Depends(get_current_fund_service)
):
    """Get overview of all funds"""
    try:
        return await fund_service.get_fund_overview()
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
        fund = await fund_service.get_fund_detail(fund_code)
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
        return await fund_service.get_transactions(fund_code, limit, offset)
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
        return await fund_service.get_nav_history(fund_code, start_date, end_date)
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
        summary = await fund_service.get_profit_summary()
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
        result = await fund_service.initialize_user_database()
        return result
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"初始化数据库失败: {str(e)}"
        )


@router.post("/fetch-nav")
async def fetch_nav(
    force_recent_days: int = 0,
    fund_service: FundService = Depends(get_current_fund_service)
):
    """Fetch historical NAV data for all enabled plans
    
    Args:
        force_recent_days: 强制重新抓取最近N天净值（0=仅抓缺失，7=强制抓最近7天）
    """
    try:
        details = await fund_service.fetch_history_nav(fund_codes=None, force_recent_days=force_recent_days)
        
        if not details:
            return {
                "message": "没有启用的定投计划需要抓取",
                "success": False,
                "details": []
            }
        
        success_count = sum(1 for d in details if d.get('success', False))
        total_rows = sum(d.get('rows_written', 0) for d in details)
        
        return {
            "message": f"抓取完成: 成功 {success_count}/{len(details)} 个基金，共导入 {total_rows} 条记录",
            "success": success_count > 0,
            "total_plans": len(details),
            "success_count": success_count,
            "total_rows_written": total_rows,
            "details": details
        }
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
        result = await fund_service.update_pending_transactions()
        
        # update_pending_transactions现在返回处理结果字典
        if result:
            return {
                "message": result.get('message', '待确认交易更新完成'),
                "success": result.get('success', True),
                "pending_count": result.get('pending_count', 0),
                "success_count": result.get('success_count', 0),
                "skip_count": result.get('skip_count', 0),
                "deleted_count": result.get('deleted_count', 0)
            }
        else:
            return {
                "message": "没有待确认的交易记录",
                "success": False,
                "pending_count": 0
            }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"更新待确认交易失败: {str(e)}"
        )


@router.post("/transactions", status_code=status.HTTP_201_CREATED)
async def create_transaction(
    transaction: dict,
    fund_service: FundService = Depends(get_current_fund_service)
):
    """Create a new transaction"""
    try:
        await fund_service.add_transaction(
            fund_code=transaction['fund_code'],
            fund_name=transaction.get('fund_name', ''),
            transaction_date=transaction['transaction_date'],
            transaction_type=transaction['transaction_type'],
            amount=transaction.get('amount'),
            shares=transaction.get('shares'),
            unit_nav=transaction.get('unit_nav'),
            note=transaction.get('note', ''),
            nav_date=transaction.get('nav_date'),
            target_amount=transaction.get('target_amount')
        )
        return {"message": "交易记录创建成功"}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"创建交易记录失败: {str(e)}"
        )


@router.post("/transactions/batch", status_code=status.HTTP_201_CREATED)
async def batch_create_transactions(
    transactions: List[dict],
    fund_service: FundService = Depends(get_current_fund_service)
):
    """Batch create transactions"""
    try:
        success_count = 0
        for trans in transactions:
            await fund_service.add_transaction(
                fund_code=trans['fund_code'],
                fund_name=trans.get('fund_name', ''),
                transaction_date=trans['transaction_date'],
                transaction_type=trans['transaction_type'],
                amount=trans.get('amount'),
                shares=trans.get('shares'),
                unit_nav=trans.get('unit_nav'),
                note=trans.get('note', ''),
                nav_date=trans.get('nav_date'),
                target_amount=trans.get('target_amount')
            )
            success_count += 1
        return {"message": f"成功导入{success_count}条交易记录"}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"批量导入失败: {str(e)}"
        )


@router.post("/nav-history/batch", status_code=status.HTTP_201_CREATED)
async def batch_create_nav_history(
    nav_records: List[dict],
    fund_service: FundService = Depends(get_current_fund_service)
):
    """Batch create NAV history records"""
    try:
        await fund_service.add_nav_history_batch(nav_records)
        return {"message": f"成功导入{len(nav_records)}条净值记录"}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"批量导入净值失败: {str(e)}"
        )


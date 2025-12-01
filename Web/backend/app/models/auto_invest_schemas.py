"""Auto-invest plan schemas"""
from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


class AutoInvestPlan(BaseModel):
    """Auto-invest plan schema"""
    plan_id: Optional[int] = None
    plan_name: str = Field(..., min_length=1, max_length=100)
    fund_code: str = Field(..., min_length=6, max_length=6)
    fund_name: str
    amount: float = Field(..., gt=0)
    frequency: str = Field(..., pattern="^(daily|weekly|monthly)$")
    start_date: str
    end_date: str
    enabled: bool = True
    created_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


class AutoInvestPlanCreate(BaseModel):
    """Create auto-invest plan request"""
    plan_name: str = Field(..., min_length=1, max_length=100)
    fund_code: str = Field(..., min_length=6, max_length=6)
    fund_name: str
    amount: float = Field(..., gt=0)
    frequency: str = Field(..., pattern="^(daily|weekly|monthly)$")
    start_date: str
    end_date: str
    enabled: bool = True


class AutoInvestPlanUpdate(BaseModel):
    """Update auto-invest plan request"""
    plan_name: Optional[str] = None
    fund_code: Optional[str] = None
    fund_name: Optional[str] = None
    amount: Optional[float] = None
    frequency: Optional[str] = None
    start_date: Optional[str] = None
    end_date: Optional[str] = None
    enabled: Optional[bool] = None

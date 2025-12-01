"""Pydantic schemas for request/response validation"""
from pydantic import BaseModel, EmailStr, Field, field_validator
from datetime import datetime
from typing import Optional
import re


class UserRegister(BaseModel):
    """User registration schema"""
    email: EmailStr
    username: str = Field(..., min_length=3, max_length=50)
    password: str = Field(..., min_length=8)
    
    @field_validator('password')
    @classmethod
    def validate_password(cls, v):
        """Validate password requirements: 
        - At least 8 characters
        - Contains uppercase letter
        - Contains lowercase letter
        - Contains number
        """
        if len(v) < 8:
            raise ValueError('密码必须至少8个字符')
        if not re.search(r'[A-Z]', v):
            raise ValueError('密码必须包含至少一个大写字母')
        if not re.search(r'[a-z]', v):
            raise ValueError('密码必须包含至少一个小写字母')
        if not re.search(r'[0-9]', v):
            raise ValueError('密码必须包含至少一个数字')
        return v


class UserLogin(BaseModel):
    """User login schema"""
    email: EmailStr
    password: str


class UserResponse(BaseModel):
    """User response schema"""
    id: int
    email: str
    username: str
    is_active: bool
    is_verified: bool
    created_at: datetime
    last_login: Optional[datetime] = None
    
    class Config:
        from_attributes = True


class Token(BaseModel):
    """Token response schema"""
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class TokenRefresh(BaseModel):
    """Token refresh request"""
    refresh_token: str


class FundOverview(BaseModel):
    """Fund overview response"""
    fund_code: str
    fund_name: str
    total_shares: float
    total_cost: float
    average_buy_nav: float
    current_nav: float
    current_value: float
    profit: float
    profit_rate: float
    first_buy_date: Optional[str]
    last_transaction_date: Optional[str]
    last_nav_date: Optional[str]
    daily_growth_rate: float


class Transaction(BaseModel):
    """Transaction record"""
    transaction_id: int
    fund_code: str
    fund_name: str
    transaction_date: str
    nav_date: Optional[str]
    transaction_type: str
    target_amount: Optional[float]
    shares: Optional[float]
    unit_nav: Optional[float]
    amount: float
    note: Optional[str]
    created_at: datetime


class NavHistory(BaseModel):
    """Historical NAV data point"""
    price_date: str
    unit_nav: float
    cumulative_nav: Optional[float]
    daily_growth_rate: Optional[float]


class ProfitSummary(BaseModel):
    """Overall profit summary"""
    total_funds: int
    total_shares: float
    total_cost: float
    total_value: float
    total_profit: float
    total_return_rate: float

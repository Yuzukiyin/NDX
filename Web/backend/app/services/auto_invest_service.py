"""Auto-invest plan service"""
from typing import List, Optional
from ..models.auto_invest_schemas import AutoInvestPlan, AutoInvestPlanCreate, AutoInvestPlanUpdate
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from ..config import settings


class AutoInvestService:
    """Service for managing auto-invest plans"""
    
    def __init__(self, user_id: int, db_path: str = None):
        self.user_id = user_id
        # 使用 PostgreSQL 连接
        self.engine = create_engine(settings.database_url_sync, future=True)
        self.Session = sessionmaker(bind=self.engine)
    
    def get_all_plans(self) -> List[AutoInvestPlan]:
        """Get all auto-invest plans for user"""
        with self.Session() as session:
            result = session.execute(
                text("""
                    SELECT * FROM auto_invest_plans 
                    WHERE user_id = :user_id 
                    ORDER BY enabled DESC, created_at DESC
                """),
                {"user_id": self.user_id}
            )
            rows = result.mappings().all()
            return [AutoInvestPlan(**dict(row)) for row in rows]
    
    def get_plan(self, plan_id: int) -> Optional[AutoInvestPlan]:
        """Get specific auto-invest plan"""
        with self.Session() as session:
            result = session.execute(
                text("""
                    SELECT * FROM auto_invest_plans 
                    WHERE user_id = :user_id AND plan_id = :plan_id
                """),
                {"user_id": self.user_id, "plan_id": plan_id}
            )
            row = result.mappings().first()
            return AutoInvestPlan(**dict(row)) if row else None
    
    def create_plan(self, plan: AutoInvestPlanCreate) -> AutoInvestPlan:
        """Create new auto-invest plan"""
        with self.Session() as session:
            with session.begin():
                result = session.execute(
                    text("""
                        INSERT INTO auto_invest_plans (
                            user_id, plan_name, fund_code, fund_name, 
                            amount, frequency, start_date, end_date, enabled
                        ) VALUES (
                            :user_id, :plan_name, :fund_code, :fund_name,
                            :amount, :frequency, :start_date, :end_date, :enabled
                        )
                        RETURNING plan_id
                    """),
                    {
                        "user_id": self.user_id,
                        "plan_name": plan.plan_name,
                        "fund_code": plan.fund_code,
                        "fund_name": plan.fund_name,
                        "amount": plan.amount,
                        "frequency": plan.frequency,
                        "start_date": plan.start_date,
                        "end_date": plan.end_date,
                        "enabled": plan.enabled
                    }
                )
                plan_id = result.scalar()
            return self.get_plan(plan_id)
    
    def update_plan(self, plan_id: int, update: AutoInvestPlanUpdate) -> Optional[AutoInvestPlan]:
        """Update auto-invest plan"""
        updates = []
        params = {"user_id": self.user_id, "plan_id": plan_id}
        
        if update.plan_name is not None:
            updates.append("plan_name = :plan_name")
            params["plan_name"] = update.plan_name
        if update.fund_code is not None:
            updates.append("fund_code = :fund_code")
            params["fund_code"] = update.fund_code
        if update.fund_name is not None:
            updates.append("fund_name = :fund_name")
            params["fund_name"] = update.fund_name
        if update.amount is not None:
            updates.append("amount = :amount")
            params["amount"] = update.amount
        if update.frequency is not None:
            updates.append("frequency = :frequency")
            params["frequency"] = update.frequency
        if update.start_date is not None:
            updates.append("start_date = :start_date")
            params["start_date"] = update.start_date
        if update.end_date is not None:
            updates.append("end_date = :end_date")
            params["end_date"] = update.end_date
        if update.enabled is not None:
            updates.append("enabled = :enabled")
            params["enabled"] = update.enabled
        
        if not updates:
            return self.get_plan(plan_id)
        
        updates.append("updated_at = CURRENT_TIMESTAMP")
        
        with self.Session() as session:
            with session.begin():
                session.execute(
                    text(f"""
                        UPDATE auto_invest_plans 
                        SET {', '.join(updates)}
                        WHERE user_id = :user_id AND plan_id = :plan_id
                    """),
                    params
                )
        
        return self.get_plan(plan_id)
    
    def delete_plan(self, plan_id: int) -> bool:
        """Delete auto-invest plan"""
        with self.Session() as session:
            with session.begin():
                result = session.execute(
                    text("""
                        DELETE FROM auto_invest_plans 
                        WHERE user_id = :user_id AND plan_id = :plan_id
                    """),
                    {"user_id": self.user_id, "plan_id": plan_id}
                )
                return result.rowcount > 0
    
    def toggle_plan(self, plan_id: int) -> Optional[AutoInvestPlan]:
        """Toggle plan enabled status"""
        plan = self.get_plan(plan_id)
        if not plan:
            return None
        
        return self.update_plan(plan_id, AutoInvestPlanUpdate(enabled=not plan.enabled))

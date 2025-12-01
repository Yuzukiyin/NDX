"""Auto-invest plan service"""
import sqlite3
from typing import List, Optional
from ..models.auto_invest_schemas import AutoInvestPlan, AutoInvestPlanCreate, AutoInvestPlanUpdate
from pathlib import Path


class AutoInvestService:
    """Service for managing auto-invest plans"""
    
    def __init__(self, user_id: int, db_path: str):
        self.user_id = user_id
        self.db_path = db_path
        self._ensure_table_exists()
    
    def _ensure_table_exists(self):
        """Ensure auto_invest_plans table exists"""
        schema_file = Path(__file__).parent.parent / 'db' / 'auto_invest_plans.sql'
        if schema_file.exists():
            conn = sqlite3.connect(self.db_path)
            conn.executescript(schema_file.read_text(encoding='utf-8'))
            conn.close()
    
    def get_connection(self) -> sqlite3.Connection:
        """Get database connection"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn
    
    def get_all_plans(self) -> List[AutoInvestPlan]:
        """Get all auto-invest plans for user"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT * FROM auto_invest_plans 
            WHERE user_id = ? 
            ORDER BY enabled DESC, created_at DESC
        """, (self.user_id,))
        
        rows = cursor.fetchall()
        conn.close()
        
        return [AutoInvestPlan(**dict(row)) for row in rows]
    
    def get_plan(self, plan_id: int) -> Optional[AutoInvestPlan]:
        """Get specific auto-invest plan"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT * FROM auto_invest_plans 
            WHERE user_id = ? AND plan_id = ?
        """, (self.user_id, plan_id))
        
        row = cursor.fetchone()
        conn.close()
        
        return AutoInvestPlan(**dict(row)) if row else None
    
    def create_plan(self, plan: AutoInvestPlanCreate) -> AutoInvestPlan:
        """Create new auto-invest plan"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT INTO auto_invest_plans (
                user_id, plan_name, fund_code, fund_name, 
                amount, frequency, start_date, end_date, enabled
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            self.user_id, plan.plan_name, plan.fund_code, plan.fund_name,
            plan.amount, plan.frequency, plan.start_date, plan.end_date, plan.enabled
        ))
        
        plan_id = cursor.lastrowid
        conn.commit()
        conn.close()
        
        return self.get_plan(plan_id)
    
    def update_plan(self, plan_id: int, update: AutoInvestPlanUpdate) -> Optional[AutoInvestPlan]:
        """Update auto-invest plan"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # Build update query dynamically
        updates = []
        params = []
        
        if update.plan_name is not None:
            updates.append("plan_name = ?")
            params.append(update.plan_name)
        if update.fund_code is not None:
            updates.append("fund_code = ?")
            params.append(update.fund_code)
        if update.fund_name is not None:
            updates.append("fund_name = ?")
            params.append(update.fund_name)
        if update.amount is not None:
            updates.append("amount = ?")
            params.append(update.amount)
        if update.frequency is not None:
            updates.append("frequency = ?")
            params.append(update.frequency)
        if update.start_date is not None:
            updates.append("start_date = ?")
            params.append(update.start_date)
        if update.end_date is not None:
            updates.append("end_date = ?")
            params.append(update.end_date)
        if update.enabled is not None:
            updates.append("enabled = ?")
            params.append(update.enabled)
        
        if not updates:
            conn.close()
            return self.get_plan(plan_id)
        
        updates.append("updated_at = CURRENT_TIMESTAMP")
        params.extend([self.user_id, plan_id])
        
        cursor.execute(f"""
            UPDATE auto_invest_plans 
            SET {', '.join(updates)}
            WHERE user_id = ? AND plan_id = ?
        """, params)
        
        conn.commit()
        conn.close()
        
        return self.get_plan(plan_id)
    
    def delete_plan(self, plan_id: int) -> bool:
        """Delete auto-invest plan"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            DELETE FROM auto_invest_plans 
            WHERE user_id = ? AND plan_id = ?
        """, (self.user_id, plan_id))
        
        deleted = cursor.rowcount > 0
        conn.commit()
        conn.close()
        
        return deleted
    
    def toggle_plan(self, plan_id: int) -> Optional[AutoInvestPlan]:
        """Toggle plan enabled status"""
        plan = self.get_plan(plan_id)
        if not plan:
            return None
        
        return self.update_plan(plan_id, AutoInvestPlanUpdate(enabled=not plan.enabled))

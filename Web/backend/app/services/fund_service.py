"""Fund data service - interfaces with original NDX fund database"""
import sqlite3
import sys
from pathlib import Path
from typing import List, Optional, Dict
from datetime import datetime
from ..models.schemas import FundOverview, Transaction, NavHistory, ProfitSummary
from ..config import settings

# Add parent directory to path to import original modules
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))


class FundService:
    """Service for accessing fund data"""
    
    def __init__(self, user_id: int):
        """Initialize with user-specific database"""
        self.user_id = user_id
        # Each user has their own fund database
        self.db_path = f"./user_data/user_{user_id}_fund.db"
        Path("./user_data").mkdir(exist_ok=True)
    
    def get_connection(self) -> sqlite3.Connection:
        """Get database connection"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn
    
    def get_fund_overview(self) -> List[FundOverview]:
        """Get all funds overview"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute("SELECT * FROM fund_realtime_overview ORDER BY fund_code")
        rows = cursor.fetchall()
        conn.close()
        
        return [FundOverview(**dict(row)) for row in rows]
    
    def get_fund_detail(self, fund_code: str) -> Optional[FundOverview]:
        """Get specific fund detail"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute(
            "SELECT * FROM fund_realtime_overview WHERE fund_code = ?",
            (fund_code,)
        )
        row = cursor.fetchone()
        conn.close()
        
        return FundOverview(**dict(row)) if row else None
    
    def get_transactions(
        self,
        fund_code: Optional[str] = None,
        limit: int = 100,
        offset: int = 0
    ) -> List[Transaction]:
        """Get transaction records"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        if fund_code:
            cursor.execute(
                """SELECT * FROM transactions 
                WHERE fund_code = ? 
                ORDER BY transaction_date DESC, transaction_id DESC 
                LIMIT ? OFFSET ?""",
                (fund_code, limit, offset)
            )
        else:
            cursor.execute(
                """SELECT * FROM transactions 
                ORDER BY transaction_date DESC, transaction_id DESC 
                LIMIT ? OFFSET ?""",
                (limit, offset)
            )
        
        rows = cursor.fetchall()
        conn.close()
        
        return [Transaction(**dict(row)) for row in rows]
    
    def get_nav_history(
        self,
        fund_code: str,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None
    ) -> List[NavHistory]:
        """Get historical NAV data"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        query = "SELECT price_date, unit_nav, cumulative_nav, daily_growth_rate FROM fund_nav_history WHERE fund_code = ?"
        params = [fund_code]
        
        if start_date:
            query += " AND price_date >= ?"
            params.append(start_date)
        
        if end_date:
            query += " AND price_date <= ?"
            params.append(end_date)
        
        query += " ORDER BY price_date ASC"
        
        cursor.execute(query, params)
        rows = cursor.fetchall()
        conn.close()
        
        return [NavHistory(**dict(row)) for row in rows]
    
    def get_profit_summary(self) -> Optional[ProfitSummary]:
        """Get overall profit summary"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute("SELECT * FROM profit_summary")
        row = cursor.fetchone()
        conn.close()
        
        return ProfitSummary(**dict(row)) if row else None
    
    def initialize_user_database(self):
        """Initialize user's fund database with schema"""
        if not Path(self.db_path).exists():
            # Import original init function
            from init_database import InitDatabase
            InitDatabase(db_path=self.db_path)
    
    def fetch_history_nav(self, fund_codes: Optional[List[str]] = None):
        """Fetch historical NAV data"""
        from fetch_history_nav import HistoryNavFetcher
        
        fetcher = HistoryNavFetcher(db_path=self.db_path)
        if fund_codes:
            for code in fund_codes:
                fetcher.fetch_and_save(code)
        else:
            fetcher.import_enabled_plans()
    
    def import_transactions_from_csv(self, csv_path: str):
        """Import transactions from CSV"""
        from import_transactions import TransactionImporter
        
        importer = TransactionImporter(db_path=self.db_path)
        importer.import_from_csv(csv_path)
    
    def update_pending_transactions(self):
        """Update pending transactions"""
        from update_pending_transactions import PendingTransactionUpdater
        
        updater = PendingTransactionUpdater(db_path=self.db_path)
        updater.process_pending_records()

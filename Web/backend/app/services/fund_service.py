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
        """Initialize with user-specific context.
        Now all fund data is stored in the unified ndx_users.db.
        """
        self.user_id = user_id
        # Parse sqlite path from DATABASE_URL (sqlite+aiosqlite:///./ndx_users.db)
        db_url = settings.database_url_async
        if db_url.startswith("sqlite+aiosqlite:///"):
            self.db_path = db_url.replace("sqlite+aiosqlite:///", "")
        elif db_url.startswith("sqlite:///"):
            self.db_path = db_url.replace("sqlite:///", "")
        else:
            # Fallback to default relative file
            self.db_path = "./ndx_users.db"
    
    def get_connection(self) -> sqlite3.Connection:
        """Get database connection"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn
    
    def get_fund_overview(self) -> List[FundOverview]:
        """Get all funds overview"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute(
            "SELECT * FROM fund_realtime_overview WHERE user_id = ? ORDER BY fund_code",
            (self.user_id,)
        )
        rows = cursor.fetchall()
        conn.close()
        
        return [FundOverview(**dict(row)) for row in rows]
    
    def get_fund_detail(self, fund_code: str) -> Optional[FundOverview]:
        """Get specific fund detail"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute(
            "SELECT * FROM fund_realtime_overview WHERE user_id = ? AND fund_code = ?",
            (self.user_id, fund_code)
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
                WHERE user_id = ? AND fund_code = ? 
                ORDER BY transaction_date DESC, transaction_id DESC 
                LIMIT ? OFFSET ?""",
                (self.user_id, fund_code, limit, offset)
            )
        else:
            cursor.execute(
                """SELECT * FROM transactions 
                WHERE user_id = ?
                ORDER BY transaction_date DESC, transaction_id DESC 
                LIMIT ? OFFSET ?""",
                (self.user_id, limit, offset)
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
        """Get historical NAV data (shared globally across all users)"""
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
        
        cursor.execute("SELECT * FROM profit_summary WHERE user_id = ?", (self.user_id,))
        row = cursor.fetchone()
        conn.close()
        
        return ProfitSummary(**dict(row)) if row else None
    
    def initialize_user_database(self):
        """Ensure fund tables exist in unified database"""
        schema_file = Path(__file__).parent.parent / 'db' / 'fund_multitenant.sql'
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='fund_overview'")
        if cursor.fetchone() is None and schema_file.exists():
            conn.executescript(schema_file.read_text(encoding='utf-8'))
        conn.close()
    
    def fetch_history_nav(self, fund_codes: Optional[List[str]] = None):
        """Fetch historical NAV data"""
        try:
            # 导入时添加路径
            import sys
            backend_dir = Path(__file__).parent.parent.parent
            if str(backend_dir) not in sys.path:
                sys.path.insert(0, str(backend_dir))
            
            from fetch_history_nav import HistoryNavFetcher
            
            # 使用settings中的配置文件路径
            config_path = settings.auto_invest_config_resolved
            
            fetcher = HistoryNavFetcher(
                config_path=config_path,
                db_path=self.db_path
            )
            
            # 调用正确的方法
            fetcher.import_enabled_plans()
        except ImportError as e:
            raise Exception(f"无法导入历史净值模块: {e}")
        except Exception as e:
            raise Exception(f"抓取历史净值失败: {e}")
    
    def import_transactions_from_csv(self, csv_path: str):
        """Import transactions from CSV"""
        from import_transactions import TransactionImporter
        
        importer = TransactionImporter(db_path=self.db_path)
        importer.import_from_csv(csv_path)
    
    def update_pending_transactions(self):
        """Update pending transactions"""
        try:
            # 导入时添加路径
            import sys
            backend_dir = Path(__file__).parent.parent.parent
            if str(backend_dir) not in sys.path:
                sys.path.insert(0, str(backend_dir))
            
            from update_pending_transactions import PendingTransactionUpdater
            
            # 使用settings中的配置文件路径
            config_path = settings.auto_invest_config_resolved
            
            updater = PendingTransactionUpdater(
                db_path=self.db_path,
                config_file=config_path,
                user_id=self.user_id
            )
            updater.process_pending_records()
        except ImportError as e:
            raise Exception(f"无法导入待确认交易更新模块: {e}")
        except Exception as e:
            raise Exception(f"更新待确认交易失败: {e}")
    
    def add_transaction(
        self,
        fund_code: str,
        fund_name: str,
        transaction_date: str,
        transaction_type: str,
        amount: Optional[float] = None,
        shares: Optional[float] = None,
        unit_nav: Optional[float] = None,
        note: str = '',
        nav_date: Optional[str] = None,
        target_amount: Optional[float] = None
    ):
        """Add a new transaction"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # Calculate amount if shares and unit_nav provided
        if shares and unit_nav:
            amount = round(shares * unit_nav, 2)
        
        cursor.execute("""
            INSERT INTO transactions (
                user_id, fund_code, fund_name, transaction_date, nav_date,
                transaction_type, target_amount, shares, unit_nav, amount, note
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            self.user_id, fund_code, fund_name, transaction_date, nav_date,
            transaction_type, target_amount, shares, unit_nav, amount, note
        ))
        
        conn.commit()
        conn.close()
    
    def add_nav_history_batch(self, nav_records: List[dict]):
        """Batch add NAV history records (shared globally)"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        for record in nav_records:
            # Check if record already exists
            cursor.execute("""
                SELECT 1 FROM fund_nav_history 
                WHERE fund_code = ? AND price_date = ?
            """, (record['fund_code'], record['price_date']))
            
            if not cursor.fetchone():
                cursor.execute("""
                    INSERT INTO fund_nav_history (
                        fund_code, fund_name, price_date, unit_nav, fetched_at
                    ) VALUES (?, ?, ?, ?, ?)
                """, (
                    record['fund_code'],
                    record.get('fund_name', ''),
                    record['price_date'],
                    record['unit_nav'],
                    record.get('fetched_at', datetime.now().isoformat())
                ))
        
        conn.commit()
        conn.close()

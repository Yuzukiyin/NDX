"""Fund data service backed by SQLAlchemy/AsyncSession"""
from typing import List, Optional
import asyncio
import sys
from pathlib import Path

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from ..models.schemas import FundOverview, Transaction, NavHistory, ProfitSummary
from ..config import settings

sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))


class FundService:
    """提供基金及交易相关的数据服务"""

    def __init__(self, user_id: int, db: AsyncSession):
        self.user_id = user_id
        self.db: AsyncSession = db

    async def get_fund_overview(self) -> List[FundOverview]:
        result = await self.db.execute(
            text(
                """
                SELECT fund_code, fund_name, total_shares::float, total_cost::float, average_buy_nav::float,
                       current_nav::float, current_value::float, profit::float, profit_rate::float,
                       first_buy_date, last_transaction_date, last_nav_date, daily_growth_rate::float
                FROM fund_realtime_overview
                WHERE user_id = :user_id
                ORDER BY fund_code
                """
            ),
            {"user_id": self.user_id},
        )
        rows = result.mappings().all()
        return [FundOverview(**dict(row)) for row in rows]

    async def get_fund_detail(self, fund_code: str) -> Optional[FundOverview]:
        result = await self.db.execute(
            text(
                """
                SELECT fund_code, fund_name, total_shares::float, total_cost::float, average_buy_nav::float,
                       current_nav::float, current_value::float, profit::float, profit_rate::float,
                       first_buy_date, last_transaction_date, last_nav_date, daily_growth_rate::float
                FROM fund_realtime_overview
                WHERE user_id = :user_id AND fund_code = :fund_code
                LIMIT 1
                """
            ),
            {"user_id": self.user_id, "fund_code": fund_code},
        )
        row = result.mappings().first()
        return FundOverview(**dict(row)) if row else None

    async def get_transactions(
        self,
        fund_code: Optional[str] = None,
        limit: int = 100,
        offset: int = 0,
    ) -> List[Transaction]:
        base_query = """
            SELECT transaction_id, fund_code, fund_name, transaction_date, nav_date,
                   transaction_type, target_amount::float, shares::float, unit_nav::float, amount::float, note, created_at
            FROM transactions
            WHERE user_id = :user_id
        """

        params = {"user_id": self.user_id, "limit": limit, "offset": offset}
        if fund_code:
            base_query += " AND fund_code = :fund_code"
            params["fund_code"] = fund_code

        base_query += " ORDER BY transaction_date DESC, transaction_id DESC LIMIT :limit OFFSET :offset"

        result = await self.db.execute(text(base_query), params)
        rows = result.mappings().all()
        return [Transaction(**dict(row)) for row in rows]

    async def get_nav_history(
        self,
        fund_code: str,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
    ) -> List[NavHistory]:
        query = """
            SELECT price_date, unit_nav, cumulative_nav, daily_growth_rate
            FROM fund_nav_history
            WHERE fund_code = :fund_code
        """
        params = {"fund_code": fund_code}

        if start_date:
            query += " AND price_date >= :start_date"
            params["start_date"] = start_date

        if end_date:
            query += " AND price_date <= :end_date"
            params["end_date"] = end_date

        query += " ORDER BY price_date ASC"

        result = await self.db.execute(text(query), params)
        rows = result.mappings().all()
        return [NavHistory(**dict(row)) for row in rows]

    async def get_profit_summary(self) -> Optional[ProfitSummary]:
        result = await self.db.execute(
            text(
                "SELECT total_funds, total_shares::float, total_cost::float, total_value::float, total_profit::float, total_return_rate::float "
                "FROM profit_summary WHERE user_id = :user_id"
            ),
            {"user_id": self.user_id},
        )
        row = result.mappings().first()
        return ProfitSummary(**dict(row)) if row else None

    async def initialize_user_database(self):
        """PostgreSQL 由 init_db 自动创建结构，此处保留占位"""
        return {"message": "PostgreSQL schema is managed automatically"}

    async def fetch_history_nav(self, fund_codes: Optional[List[str]] = None, force_recent_days: int = 0):
        """抓取历史净值
        
        Args:
            fund_codes: 指定基金代码列表（暂未使用）
            force_recent_days: 强制重新抓取最近 N 天的净值（0=仅抓取缺失日期，7=强制抓最近7天）
        """
        try:
            import sys
            from datetime import datetime, timedelta
            backend_dir = Path(__file__).parent.parent.parent
            if str(backend_dir) not in sys.path:
                sys.path.insert(0, str(backend_dir))

            from fetch_history_nav import HistoryNavFetcher

            config_path = settings.auto_invest_config_resolved
            fetcher = HistoryNavFetcher(
                config_path=config_path,
                db_url=settings.database_url_sync,
                data_source='fundSpider',
            )

            # 如果设置了强制抓取最近 N 天，计算起始日期
            start_override = None
            if force_recent_days > 0:
                start_override = (datetime.now() - timedelta(days=force_recent_days)).strftime('%Y-%m-%d')

            # 运行阻塞任务到线程池，避免阻塞事件循环
            return await asyncio.to_thread(fetcher.import_enabled_plans, start_override, None)
        except ImportError as e:
            raise Exception(f"无法导入历史净值模块: {e}")
        except Exception as e:
            raise Exception(f"抓取历史净值失败: {e}")

    async def update_pending_transactions(self, use_target_amount: bool = True, auto_remove_non_trading: bool = True):
        try:
            import sys
            backend_dir = Path(__file__).parent.parent.parent
            if str(backend_dir) not in sys.path:
                sys.path.insert(0, str(backend_dir))

            from update_pending_transactions import PendingTransactionUpdater

            config_path = settings.auto_invest_config_resolved
            updater = PendingTransactionUpdater(
                db_path=settings.FUND_DB_PATH,
                config_file=config_path,
                user_id=self.user_id,
                db_url=settings.database_url_sync,
            )
            return await asyncio.to_thread(
                updater.process_pending_records,
                use_target_amount,
                auto_remove_non_trading,
            )
        except ImportError as e:
            raise Exception(f"无法导入待确认交易更新模块: {e}")
        except Exception as e:
            raise Exception(f"更新待确认交易失败: {e}")

    async def add_transaction(
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
        target_amount: Optional[float] = None,
    ):
        if shares and unit_nav and amount is None:
            amount = round(shares * unit_nav, 2)

        await self.db.execute(
            text(
                """
                INSERT INTO transactions (
                    user_id, fund_code, fund_name, transaction_date, nav_date,
                    transaction_type, target_amount, shares, unit_nav, amount, note
                ) VALUES (
                    :user_id, :fund_code, :fund_name, :transaction_date, :nav_date,
                    :transaction_type, :target_amount, :shares, :unit_nav, :amount, :note
                )
                """
            ),
            {
                "user_id": self.user_id,
                "fund_code": fund_code,
                "fund_name": fund_name,
                "transaction_date": transaction_date,
                "nav_date": nav_date,
                "transaction_type": transaction_type,
                "target_amount": target_amount,
                "shares": shares,
                "unit_nav": unit_nav,
                "amount": amount,
                "note": note,
            },
        )
        await self.db.commit()

    async def add_nav_history_batch(self, nav_records: List[dict]):
        if not nav_records:
            return

        sql = text(
            """
            INSERT INTO fund_nav_history (
                fund_code, fund_name, price_date, unit_nav, cumulative_nav, daily_growth_rate, data_source
            ) VALUES (
                :fund_code, :fund_name, :price_date, :unit_nav, :cumulative_nav, :daily_growth_rate, :data_source
            )
            ON CONFLICT (fund_code, price_date, data_source) DO UPDATE SET
                unit_nav = EXCLUDED.unit_nav,
                cumulative_nav = EXCLUDED.cumulative_nav,
                daily_growth_rate = EXCLUDED.daily_growth_rate,
                fetched_at = CURRENT_TIMESTAMP
            """
        )

        for record in nav_records:
            payload = {
                "fund_code": record["fund_code"],
                "fund_name": record.get("fund_name", ""),
                "price_date": record["price_date"],
                "unit_nav": record["unit_nav"],
                "cumulative_nav": record.get("cumulative_nav"),
                "daily_growth_rate": record.get("daily_growth_rate"),
                "data_source": record.get("data_source", "fundSpider"),
            }
            await self.db.execute(sql, payload)

        await self.db.commit()

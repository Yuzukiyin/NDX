'''
判断是否为定投交易日期的模块（PostgreSQL）
'''

import os
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
from sqlalchemy import create_engine, text

class TradeDateChecker:
    def __init__(self, user_id: int = 1, db_url: str | None = None):
        '''初始化交易日检查器（仅支持PostgreSQL）'''
        self.user_id = user_id
        
        # 获取数据库URL
        if db_url:
            self.db_url = self._resolve_db_url(db_url)
        else:
            self.db_url = os.getenv('DATABASE_URL', 'postgresql://localhost:5432/ndx')
            self.db_url = self._resolve_db_url(self.db_url)
        
        self.engine = create_engine(self.db_url, future=True)
        self.plans = self.load_plans()
        self.holidays = self._load_holidays()

    def _resolve_db_url(self, raw: str) -> str:
        """将数据库URL转换为同步PostgreSQL格式"""
        if not raw:
            return 'postgresql://localhost:5432/ndx'
        
        # Railway等平台可能使用postgres://前缀
        if raw.startswith('postgres://'):
            raw = raw.replace('postgres://', 'postgresql://', 1)
        
        # 确保使用psycopg2驱动（同步）
        if raw.startswith('postgresql+asyncpg://'):
            raw = raw.replace('postgresql+asyncpg://', 'postgresql+psycopg2://', 1)
        elif raw.startswith('postgresql://') and '+' not in raw:
            raw = raw.replace('postgresql://', 'postgresql+psycopg2://', 1)
        
        return raw

    def load_plans(self):
        '''从数据库加载启用的定投计划（仅PostgreSQL）'''
        try:
            with self.engine.connect() as conn:
                result = conn.execute(
                    text("""
                        SELECT plan_name, fund_code, fund_name, amount, frequency, 
                               start_date::text, end_date::text
                        FROM auto_invest_plans
                        WHERE user_id = :user_id AND enabled = true
                    """),
                    {"user_id": self.user_id}
                )
                rows = result.fetchall()
                plans = []
                for row in rows:
                    plans.append({
                        'plan_name': row[0],
                        'fund_code': row[1],
                        'fund_name': row[2],
                        'amount': float(row[3]),
                        'frequency': row[4],
                        'start_date': row[5],
                        'end_date': row[6]
                    })
                print(f"从数据库加载了 {len(plans)} 个启用的定投计划")
                return {"plans": plans}
        except Exception as e:
            print(f"从数据库读取计划失败: {e}")
            return {"plans": []}

    def _load_holidays(self):
        '''导入2024-2026年中国法定节假日'''
        return {
            # 2024年
            '2024-01-01', '2024-02-10', '2024-02-11', '2024-02-12', '2024-02-13', '2024-02-14', '2024-02-15', '2024-02-16', '2024-02-17',
            '2024-04-04', '2024-04-05', '2024-04-06',
            '2024-05-01', '2024-05-02', '2024-05-03', '2024-05-04', '2024-05-05',
            '2024-06-10',
            '2024-09-15', '2024-09-16', '2024-09-17',
            '2024-10-01', '2024-10-02', '2024-10-03', '2024-10-04', '2024-10-05', '2024-10-06', '2024-10-07',
            
            # 2025年
            '2025-01-01', '2025-01-28', '2025-01-29', '2025-01-30', '2025-01-31', '2025-02-01', '2025-02-02', '2025-02-03', '2025-02-04',
            '2025-04-04', '2025-04-05', '2025-04-06',
            '2025-05-01', '2025-05-02', '2025-05-03', '2025-05-04', '2025-05-05',
            '2025-05-31', '2025-06-01', '2025-06-02',
            '2025-10-01', '2025-10-02', '2025-10-03', '2025-10-04', '2025-10-05', '2025-10-06', '2025-10-07', '2025-10-08',
            
            # 2026年（预估，实际以国务院公布为准）
            '2026-01-01', '2026-01-02', '2026-01-03',
            '2026-02-17', '2026-02-18', '2026-02-19', '2026-02-20', '2026-02-21', '2026-02-22', '2026-02-23',
            '2026-04-04', '2026-04-05', '2026-04-06',
            '2026-05-01', '2026-05-02', '2026-05-03', '2026-05-04', '2026-05-05',
            '2026-06-19', '2026-06-20', '2026-06-21',
            '2026-10-01', '2026-10-02', '2026-10-03', '2026-10-04', '2026-10-05', '2026-10-06', '2026-10-07',
        }
    
    def is_trading_day(self, date):
        """
        判断是否为交易日（工作日且非节假日）
        Args:
            date: datetime对象或字符串(YYYY-MM-DD)
        Returns:
            bool: True表示是交易日
        """
        if isinstance(date, str):
            date = datetime.strptime(date, '%Y-%m-%d')
        
        if date.weekday() >= 5: 
            return False
        
        date_str = date.strftime('%Y-%m-%d')
        if date_str in self.holidays:
            return False
        
        return True

    def _generate_dates(self, plan, start_date, end_date):
        """根据定投频率生成交易与确认日期 (确认日=T+1交易日)"""
        transactions = []
        anchor_date = start_date
        while anchor_date <= end_date:
            # 仅对每日频率跳过非交易日，其他频率按锚点生成（若锚点非交易日则跳过该期）
            if plan['frequency'] == 'daily' and not self.is_trading_day(anchor_date):
                anchor_date += timedelta(days=1)
                continue
            if plan['frequency'] != 'daily' and not self.is_trading_day(anchor_date):
                # 对 weekly/monthly/quarterly 若锚点不是交易日，直接跳到下一个周期
                if plan['frequency'] == 'weekly':
                    anchor_date += timedelta(weeks=1)
                elif plan['frequency'] == 'monthly':
                    anchor_date += relativedelta(months=1)
                elif plan['frequency'] == 'quarterly':
                    anchor_date += relativedelta(months=3)
                else:
                    break
                continue
            buy_date = anchor_date
            confirm_date = self.get_next_trading_day(buy_date, 1)
            transaction = {
                'plan_name': plan['plan_name'],
                'fund_code': plan['fund_code'],
                'fund_name': plan['fund_name'],
                'transaction_date': buy_date.strftime('%Y-%m-%d'),
                'confirm_date': confirm_date.strftime('%Y-%m-%d'),
                'current_date': confirm_date.strftime('%Y-%m-%d'),
                'amount': plan['amount'],
                'transaction_type': '买入'
            }
            transactions.append(transaction)
            if plan['frequency'] == 'daily':
                anchor_date += timedelta(days=1)
            elif plan['frequency'] == 'weekly':
                anchor_date += timedelta(weeks=1)
            elif plan['frequency'] == 'monthly':
                anchor_date += relativedelta(months=1)
            elif plan['frequency'] == 'quarterly':
                anchor_date += relativedelta(months=3)
            else:
                break
        return transactions
    
    def _get_previous_trading_day(self, date, days_before):
        """
        获取指定日期之前的第N个交易日
        
        Args:
            date: 目标日期
            days_before: 向前推移的交易日天数
        
        Returns:
            datetime: 提前N个交易日的日期
        """
        if days_before == 0:
            return date
        
        current = date
        count = 0
        
        while count < days_before:
            current -= timedelta(days=1)
            # 只有交易日才计数
            if self.is_trading_day(current):
                count += 1
        
        return current

    def get_next_trading_day(self, date, offset=1):
        """向后寻找第 offset 个交易日"""
        if offset == 0:
            return date
        current = date
        count = 0
        while count < offset:
            current += timedelta(days=1)
            if self.is_trading_day(current):
                count += 1
        return current









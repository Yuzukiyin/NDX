"""
更新待确认交易记录的脚本（PostgreSQL）
当历史净值抓取后,自动填充 shares/unit_nav/amount
从数据库的定投计划表(auto_invest_plans)获取金额配置
"""

import os
from datetime import datetime, timedelta
from sqlalchemy import create_engine, text
from tradeDate import TradeDateChecker


class PendingTransactionUpdater:
    def __init__(self, user_id=1, db_url: str | None = None):
        '''初始化待确认交易更新器（仅支持PostgreSQL）'''
        self.user_id = user_id
        
        # 获取数据库URL
        if db_url:
            self.db_url = self._resolve_db_url(db_url)
        else:
            self.db_url = os.getenv('DATABASE_URL', 'postgresql://localhost:5432/ndx')
            self.db_url = self._resolve_db_url(self.db_url)
        
        self.engine = create_engine(self.db_url, future=True)
        # 先尝试从数据库加载，失败则从配置文件加载
        self.plans = self._build_plan_map()

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
    
    def _build_plan_map(self):
        """从数据库加载启用的定投计划，构建 fund_code -> amount 映射（仅PostgreSQL）"""
        plan_map = {}
        
        # 从数据库读取定投计划
        try:
            with self.engine.connect() as conn:
                result = conn.execute(
                    text("""
                        SELECT fund_code, amount FROM auto_invest_plans
                        WHERE user_id = :user_id AND enabled = true
                    """),
                    {"user_id": self.user_id}
                )
                rows = result.fetchall()
                if rows:
                    for row in rows:
                        plan_map[row[0]] = float(row[1])
                    print(f"从数据库加载了 {len(plan_map)} 个启用的定投计划金额")
                    return plan_map
        except Exception as e:
            print(f"从数据库读取计划失败: {e}")
            return plan_map
    
    def get_pending_transactions(self):
        """查询当前用户所有待确认的交易记录（shares IS NULL）"""
        with self.engine.connect() as conn:
            result = conn.execute(
                text(
                    """SELECT transaction_id, fund_code, fund_name, transaction_date, nav_date, note
                         FROM transactions
                         WHERE user_id = :user_id AND shares IS NULL
                         ORDER BY transaction_date, transaction_id"""
                ),
                {"user_id": self.user_id},
            )
            return [tuple(row) for row in result.fetchall()]
    
    def update_transaction(self, transaction_id, fund_name, unit_nav, shares, amount, note_original):
        """
        更新交易记录的 shares/unit_nav/amount
        
        Args:
            transaction_id: 交易ID
            fund_name: 基金名称
            unit_nav: 单位净值
            shares: 份额
            amount: 金额
            note_original: 原始备注
        
        Returns:
            bool: 更新成功返回True
        """
        note_updated = note_original.replace('[待确认]', '').strip()
        with self.engine.begin() as conn:
            result = conn.execute(
                text(
                    """UPDATE transactions
                         SET fund_name = :fund_name,
                             shares = :shares,
                             unit_nav = :unit_nav,
                             amount = :amount,
                             note = :note
                         WHERE transaction_id = :transaction_id"""
                ),
                {
                    "fund_name": fund_name,
                    "shares": shares,
                    "unit_nav": unit_nav,
                    "amount": amount,
                    "note": note_updated,
                    "transaction_id": transaction_id,
                },
            )
            return bool(result.rowcount)

    def _auto_clean_non_trading_days(self):
        """
        自动检测并清理所有非交易日的待确认记录
        
        检查逻辑：遍历所有待确认记录的nav_date，如果该日期无净值但次日有净值，判定为非交易日并删除
        
        Returns:
            int: 删除的记录数量
        """
        # 将所有数据库操作放在一个事务内
        with self.engine.begin() as conn:
            pending_dates = [
                row[0]
                for row in conn.execute(
                    text(
                        """SELECT DISTINCT nav_date::text FROM transactions
                             WHERE user_id = :user_id AND shares IS NULL
                             ORDER BY nav_date"""
                    ),
                    {"user_id": self.user_id},
                ).fetchall()
            ]
            
            if not pending_dates:
                print("没有待确认记录需要检查")
                return
            
            print(f"检查 {len(pending_dates)} 个不同日期: {', '.join(pending_dates)}\n")
            
            total_deleted = 0
            
            for check_date in pending_dates:
                check_dt = datetime.strptime(check_date, '%Y-%m-%d')
                next_day = (check_dt + timedelta(days=1)).strftime('%Y-%m-%d')
                
                # 获取该日期的待确认基金代码
                affected_funds = [
                    row[0]
                    for row in conn.execute(
                        text(
                            """SELECT DISTINCT fund_code FROM transactions
                                 WHERE user_id = :user_id AND nav_date = :nav_date AND shares IS NULL"""
                        ),
                        {"user_id": self.user_id, "nav_date": check_date},
                    ).fetchall()
                ]
                
                # 检查每个基金是否符合非交易日条件
                non_trading_funds = []
                
                for fund_code in affected_funds:
                    # 检查check_date是否有净值
                    count_check = conn.execute(
                        text(
                            """SELECT COUNT(*) FROM fund_nav_history
                                 WHERE fund_code = :fund_code AND price_date = :price_date"""
                        ),
                        {"fund_code": fund_code, "price_date": check_date},
                    ).scalar() or 0
                    
                    # 检查next_day是否有净值
                    count_next = conn.execute(
                        text(
                            """SELECT COUNT(*) FROM fund_nav_history
                                 WHERE fund_code = :fund_code AND price_date = :price_date"""
                        ),
                        {"fund_code": fund_code, "price_date": next_day},
                    ).scalar() or 0
                    
                    if count_check == 0 and count_next > 0:
                        non_trading_funds.append(fund_code)
                
                # 删除非交易日的待确认记录
                if non_trading_funds:
                    print(f"  {check_date}: 检测到非交易日 (基金: {', '.join(non_trading_funds)})")
                    
                    for fund_code in non_trading_funds:
                        to_delete = conn.execute(
                            text(
                                """SELECT transaction_id, transaction_date, note FROM transactions
                                     WHERE user_id = :user_id AND fund_code = :fund_code AND nav_date = :nav_date AND shares IS NULL"""
                            ),
                            {"user_id": self.user_id, "fund_code": fund_code, "nav_date": check_date},
                        ).fetchall()

                        for tx_id, trans_date, note in to_delete:
                            print(f"    删除: ID={tx_id} {fund_code} 交易日={trans_date}")
                            conn.execute(
                                text("DELETE FROM transactions WHERE transaction_id = :transaction_id"),
                                {"transaction_id": tx_id},
                            )
                            total_deleted += 1
            
            if total_deleted > 0:
                print(f"\n共删除 {total_deleted} 条非交易日待确认记录")
            else:
                print("未发现非交易日待确认记录")
            
            return total_deleted

    def process_pending_records(self, use_target_amount=True, auto_remove_non_trading=True):
        """
        处理所有待确认记录
        
        Args:
            use_target_amount: True=使用数据库中的target_amount，False=从配置文件获取金额
            auto_remove_non_trading: True=自动检测并删除非交易日的待确认记录
        
        Returns:
            dict: 包含处理结果的字典
        """
        pending = self.get_pending_transactions()
        initial_count = len(pending)
        deleted_count = 0
        
        if not pending:
            print("没有待确认的交易记录")
            return {
                "success": False,
                "message": "没有待确认的交易记录",
                "pending_count": 0,
                "success_count": 0,
                "skip_count": 0,
                "deleted_count": 0
            }
        
        print(f"找到 {len(pending)} 条待确认记录\n")
        
        # 自动清理非交易日记录
        if auto_remove_non_trading:
            deleted_count = self._auto_clean_non_trading_days()
            print()
            
            # 重新获取待确认记录
            pending = self.get_pending_transactions()
            if not pending:
                print("清理后没有待确认的交易记录")
                return {
                    "success": True,
                    "message": f"清理了 {deleted_count} 条非交易日记录，无待确认记录需要更新",
                    "pending_count": initial_count,
                    "success_count": 0,
                    "skip_count": 0,
                    "deleted_count": deleted_count
                }
            print(f"清理后剩余 {len(pending)} 条待确认记录\n")
        
        success_count = 0
        skip_count = 0
        
        for tx_id, fund_code, fund_name_old, trans_date, nav_date, note in pending:
            print(f"交易ID {tx_id}: {fund_code} 交易日={trans_date} 净值日={nav_date}")
            
            # 获取金额
            if use_target_amount:
                # 从数据库读取target_amount
                with self.engine.connect() as conn:
                    result = conn.execute(
                        text("SELECT target_amount FROM transactions WHERE user_id = :user_id AND transaction_id = :transaction_id"),
                        {"user_id": self.user_id, "transaction_id": tx_id},
                    ).first()
                if not result or result[0] is None:
                    print(f"target_amount为空，跳过\n")
                    skip_count += 1
                    continue
                target_amount = result[0]
            else:
                # 从定投计划配置获取金额
                if fund_code not in self.plans:
                    print(f"未在定投计划中找到该基金，跳过\n")
                    skip_count += 1
                    continue
                target_amount = self.plans[fund_code]
            
            # 获取净值日净值
            nav_info = self._get_nav_for_date(fund_code, nav_date)
            
            if not nav_info:
                print(f"净值仍未抓取，跳过\n")
                skip_count += 1
                continue
            
            fund_name, unit_nav = nav_info
            shares = round(target_amount / unit_nav, 2)
            amount = round(shares * unit_nav, 2)
            
            print(f"金额: ¥{target_amount:.2f} 净值: ¥{unit_nav:.4f} 份额: {shares:.2f}")
            
            if self.update_transaction(tx_id, fund_name, unit_nav, shares, amount, note):
                print(f"  已更新\n")
                success_count += 1
            else:
                print(f"  更新失败\n")
                skip_count += 1
        
        print("=" * 50)
        print(f"更新完成: 成功 {success_count} 条，跳过 {skip_count} 条")
        print("=" * 50)
        
        # 返回详细结果
        return {
            "success": success_count > 0 or deleted_count > 0,
            "message": f"成功更新 {success_count} 条，跳过 {skip_count} 条，删除非交易日 {deleted_count} 条",
            "pending_count": initial_count,
            "success_count": success_count,
            "skip_count": skip_count,
            "deleted_count": deleted_count
        }

    def _get_nav_for_date(self, fund_code: str, nav_date: str):
        with self.engine.connect() as conn:
            row = conn.execute(
                text(
                    """SELECT fund_name, unit_nav FROM fund_nav_history
                         WHERE fund_code = :fund_code AND price_date = :price_date
                         ORDER BY fetched_at DESC LIMIT 1"""
                ),
                {"fund_code": fund_code, "price_date": nav_date},
            ).first()
        if not row:
            return None
        return row[0], float(row[1])


# 向后兼容的函数接口
def process_pending_records(use_target_amount=True, auto_remove_non_trading=True, db_url: str | None = None, user_id=1):
    """处理所有待确认记录（PostgreSQL）
    
    Args:
        use_target_amount: True=使用数据库中的target_amount，False=从数据库的定投计划获取金额
        auto_remove_non_trading: True=自动检测并删除非交易日的待确认记录
        db_url: PostgreSQL数据库URL
        user_id: 用户ID
    """
    updater = PendingTransactionUpdater(db_url=db_url, user_id=user_id)
    updater.process_pending_records(use_target_amount, auto_remove_non_trading)
    

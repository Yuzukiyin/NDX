"""
更新待确认交易记录的脚本
当历史净值抓取后,自动填充 shares/unit_nav/amount
支持从定投计划配置自动提取金额
"""
#fund.db
#auto_invest_setting.json

import sqlite3
from datetime import datetime, timedelta
from import_transactions import TransactionImporter
from tradeDate import TradeDateChecker

class PendingTransactionUpdater:
    def __init__(self, db_path='fund.db', config_file='auto_invest_setting.json'):
        self.db_path = db_path
        self.config_file = config_file
        self.checker = TradeDateChecker(config_file=config_file, db_path=db_path)
        self.plans = self._build_plan_map()
        self.importer = TransactionImporter(db_path=db_path)
    
    def _build_plan_map(self):
        """从 TradeDateChecker 加载的计划构建 fund_code -> amount 映射"""
        plan_map = {}
        for plan in self.checker.plans.get('plans', []):
            fund_code = plan.get('fund_code')
            amount = plan.get('amount')
            if fund_code and amount:
                plan_map[fund_code] = amount
        return plan_map
    
    def get_pending_transactions(self):
        """查询所有待确认的交易记录（shares IS NULL）"""
        conn = sqlite3.connect(self.db_path)
        cur = conn.cursor()
        cur.execute("""
            SELECT transaction_id, fund_code, fund_name, transaction_date, nav_date, note
            FROM transactions
            WHERE shares IS NULL
            ORDER BY transaction_date, transaction_id
        """)
        rows = cur.fetchall()
        conn.close()
        return rows
    
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
        conn = sqlite3.connect(self.db_path)
        cur = conn.cursor()
        # 移除备注中的 [待确认] 标记
        note_updated = note_original.replace('[待确认]', '').strip()
        cur.execute("""
            UPDATE transactions
            SET fund_name = ?,
                shares = ?,
                unit_nav = ?,
                amount = ?,
                note = ?
            WHERE transaction_id = ?
        """, (fund_name, shares, unit_nav, amount, note_updated, transaction_id))
        conn.commit()
        affected = cur.rowcount
        conn.close()
        return affected > 0

    def _auto_clean_non_trading_days(self):
        """
        自动检测并清理所有非交易日的待确认记录
        
        检查逻辑：遍历所有待确认记录的nav_date，如果该日期无净值但次日有净值，判定为非交易日并删除
        """
        conn = sqlite3.connect(self.db_path)
        cur = conn.cursor()
        
        # 获取所有待确认记录的不同nav_date
        cur.execute("""
            SELECT DISTINCT nav_date
            FROM transactions
            WHERE shares IS NULL
            ORDER BY nav_date
        """)
        
        pending_dates = [row[0] for row in cur.fetchall()]
        
        if not pending_dates:
            print("没有待确认记录需要检查")
            conn.close()
            return
        
        print(f"检查 {len(pending_dates)} 个不同日期: {', '.join(pending_dates)}\n")
        
        total_deleted = 0
        
        for check_date in pending_dates:
            check_dt = datetime.strptime(check_date, '%Y-%m-%d')
            next_day = (check_dt + timedelta(days=1)).strftime('%Y-%m-%d')
            
            # 获取该日期的待确认基金代码
            cur.execute("""
                SELECT DISTINCT fund_code
                FROM transactions
                WHERE nav_date = ? AND shares IS NULL
            """, (check_date,))
            
            affected_funds = [row[0] for row in cur.fetchall()]
            
            # 检查每个基金是否符合非交易日条件
            non_trading_funds = []
            
            for fund_code in affected_funds:
                # 检查check_date是否有净值
                cur.execute("""
                    SELECT COUNT(*) FROM fund_nav_history
                    WHERE fund_code = ? AND price_date = ?
                """, (fund_code, check_date))
                count_check = cur.fetchone()[0]
                
                # 检查next_day是否有净值
                cur.execute("""
                    SELECT COUNT(*) FROM fund_nav_history
                    WHERE fund_code = ? AND price_date = ?
                """, (fund_code, next_day))
                count_next = cur.fetchone()[0]
                
                if count_check == 0 and count_next > 0:
                    non_trading_funds.append(fund_code)
            
            # 删除非交易日的待确认记录
            if non_trading_funds:
                print(f"  {check_date}: 检测到非交易日 (基金: {', '.join(non_trading_funds)})")
                
                for fund_code in non_trading_funds:
                    cur.execute("""
                        SELECT transaction_id, transaction_date, note
                        FROM transactions
                        WHERE fund_code = ? AND nav_date = ? AND shares IS NULL
                    """, (fund_code, check_date))
                    
                    to_delete = cur.fetchall()
                    
                    for tx_id, trans_date, note in to_delete:
                        print(f"    删除: ID={tx_id} {fund_code} 交易日={trans_date}")
                        cur.execute("DELETE FROM transactions WHERE transaction_id = ?", (tx_id,))
                        total_deleted += 1
        
        conn.commit()
        conn.close()
        
        if total_deleted > 0:
            print(f"\n共删除 {total_deleted} 条非交易日待确认记录")
        else:
            print("未发现非交易日待确认记录")

    def process_pending_records(self, use_target_amount=True, auto_remove_non_trading=True):
        """
        处理所有待确认记录
        
        Args:
            use_target_amount: True=使用数据库中的target_amount，False=从配置文件获取金额
            auto_remove_non_trading: True=自动检测并删除非交易日的待确认记录
        """
        pending = self.get_pending_transactions()
        
        if not pending:
            print("没有待确认的交易记录")
            return
        
        print(f"找到 {len(pending)} 条待确认记录\n")
        
        # 自动清理非交易日记录
        if auto_remove_non_trading:
            self._auto_clean_non_trading_days()
            print()
            
            # 重新获取待确认记录
            pending = self.get_pending_transactions()
            if not pending:
                print("清理后没有待确认的交易记录")
                return
            print(f"清理后剩余 {len(pending)} 条待确认记录\n")
        
        success_count = 0
        skip_count = 0
        
        for tx_id, fund_code, fund_name_old, trans_date, nav_date, note in pending:
            print(f"交易ID {tx_id}: {fund_code} 交易日={trans_date} 净值日={nav_date}")
            
            # 获取金额
            if use_target_amount:
                # 从数据库读取target_amount
                conn = sqlite3.connect(self.db_path)
                cur = conn.cursor()
                cur.execute("SELECT target_amount FROM transactions WHERE transaction_id = ?", (tx_id,))
                result = cur.fetchone()
                conn.close()
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
            nav_info = self.importer._get_nav_for_date(fund_code, nav_date)
            
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


# 向后兼容的函数接口
def process_pending_records(use_target_amount=True, auto_remove_non_trading=True, db_path='fund.db', config_file='auto_invest_setting.json'):
    """处理所有待确认记录
    
    Args:
        use_target_amount: True=使用数据库中的target_amount，False=从配置文件获取金额
        auto_remove_non_trading: True=自动检测并删除非交易日的待确认记录
        db_path: 数据库路径
        config_file: 配置文件路径
    """
    updater = PendingTransactionUpdater(db_path=db_path, config_file=config_file)
    updater.process_pending_records(use_target_amount, auto_remove_non_trading)
    

"""
根据定投计划和历史净值，导入定投交易记录
自动计算买入份额并导入数据库
"""
#auto_invest_setting.json
#fund.db

import json
import os
from datetime import datetime
from tradeDate import TradeDateChecker
from import_transactions import TransactionImporter
from dateutil.relativedelta import relativedelta

class ImportAutoInvest:
    def __init__(self, config_file='auto_invest_setting.json', db_path='fund.db'):
        '''设置定投配置文件路径和数据库路径'''
        self.config_file = config_file
        self.db_path = db_path
        self.importer = TransactionImporter(db_path=db_path)
    
    def _transaction_exists(self, fund_code, transaction_date, plan_name):
        """
        检查某个基金在某天是否已有定投交易记录
        
        Args:
            fund_code: 基金代码
            transaction_date: 交易日期 'YYYY-MM-DD'
            plan_name: 计划名称
        
        Returns:
            bool: True表示已存在
        """
        import sqlite3
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("""
            SELECT COUNT(*) FROM transactions
            WHERE fund_code = ? 
            AND transaction_date = ? 
            AND note LIKE ?
        """, (fund_code, transaction_date, f"%定投-{plan_name}%"))
        count = cursor.fetchone()[0]
        conn.close()
        return count > 0

    def Import_invest_transactions(self, target_date_str):
        """
        根据定投计划导入指定日期的交易记录（单日）
        
        Args:
            target_date_str: 目标日期字符串 'YYYY-MM-DD'
        """
        print(f"根据定投计划导入交易记录 - {target_date_str}")
        
        # 加载定投配置
        if not os.path.exists(self.config_file):
            print(f"配置文件不存在: {self.config_file}")
            return
        
        with open(self.config_file, 'r', encoding='utf-8') as f:
            config = json.load(f)
        
        plans = config.get('plans', [])
        if not plans:
            print("没有定投计划")
            return
        
        # 解析交易日期
        trans_date = datetime.strptime(target_date_str, '%Y-%m-%d')
        checker = TradeDateChecker(self.config_file, db_path=self.db_path)
        
        # 净值日期：非交易日使用下一交易日
        if checker.is_trading_day(trans_date):
            nav_date_str = target_date_str
        else:
            nav_dt = checker.get_next_trading_day(trans_date, 1)
            nav_date_str = nav_dt.strftime('%Y-%m-%d')
        
        print(f"交易日期: {target_date_str} | 净值日期: {nav_date_str}")
        print(f"找到 {len(plans)} 个定投计划\n")
        
        # 初始化交易写入器
        writer = TransactionImporter(db_path='fund.db')
        
        success_count = 0
        skip_count = 0
        error_count = 0
        
        for plan in plans:
            if not plan.get('enabled', True):
                print(f"跳过已禁用计划: {plan['plan_name']}\n")
                skip_count += 1
                continue
            
            # 检查日期是否在计划范围内
            plan_start = datetime.strptime(plan['start_date'], '%Y-%m-%d')
            plan_end = datetime.strptime(plan.get('end_date', '2099-12-31'), '%Y-%m-%d')
            
            if trans_date < plan_start or trans_date > plan_end:
                print(f"{plan['plan_name']}: 不在计划日期范围内 ({plan['start_date']} ~ {plan.get('end_date', '持续')})\n")
                skip_count += 1
                continue
            
            print(f"处理计划: {plan['plan_name']}")
            print(f"基金: {plan['fund_name']} ({plan['fund_code']})")
            print(f"金额: ¥{plan['amount']:.2f}")
            print(f"频率: {plan['frequency']}")
            
            # 检查是否已存在该交易记录
            if self._transaction_exists(plan['fund_code'], target_date_str, plan['plan_name']):
                print(f"该日期已存在定投记录，跳过\n")
                skip_count += 1
                continue
            
            try:
                # 获取净值日净值数据 - 使用 importer 的方法
                nav_info = self.importer._get_nav_for_date(plan['fund_code'], nav_date_str)
                
                if not nav_info:
                    print(f"净值日净值未抓取，创建待确认记录\n")
                    note = f"定投-{plan['plan_name']}[待确认]"
                    writer.add_transaction(
                        fund_code=plan['fund_code'],
                        fund_name=plan['fund_name'],
                        transaction_type='买入',
                        shares=None,
                        unit_nav=None,
                        note=note,
                        transaction_date=target_date_str,
                        nav_date=nav_date_str,
                        target_amount=plan['amount']
                    )
                    success_count += 1
                    continue
                
                # 计算买入份额
                fund_name, unit_nav = nav_info
                shares = plan['amount'] / unit_nav
                
                print(f"\n 计算结果:")
                print(f"投资金额: ¥{plan['amount']:.2f}")
                print(f"单位净值: ¥{unit_nav:.4f}")
                print(f"买入份额: {shares:.2f}")
                
                # 写入数据库
                note = f"定投-{plan['plan_name']}"

                writer.add_transaction(
                    fund_code=plan['fund_code'],
                    fund_name=plan['fund_name'],
                    transaction_type='买入',
                    shares=shares,
                    unit_nav=unit_nav,
                    note=note,
                    transaction_date=target_date_str,
                    nav_date=nav_date_str,
                    target_amount=plan['amount']  # 保存原始金额
                )
                
                success_count += 1
                print(f"已写入数据库\n")
                
            
            except Exception as e:
                print(f"处理失败: {str(e)}\n")
                error_count += 1
                continue
        
        # 汇总
        print(f"导入完成")
        print(f"成功: {success_count} 条，失败: {error_count} 条")

    def Import_date_range(self, start_date_str=None, end_date_str=None):
        """
        批量导入定投计划的交易记录（从计划开始日期到今天）
        
        Args:
            start_date_str: 开始日期 'YYYY-MM-DD'（可选，默认使用各计划的start_date）
            end_date_str: 结束日期 'YYYY-MM-DD'（可选，默认为今天）
        """
        # 默认结束日期为今天
        if end_date_str is None:
            end_date_str = datetime.now().strftime('%Y-%m-%d')
        
        # 如果没有指定开始日期，则从所有计划中找最早的开始日期
        if start_date_str is None:
            if not os.path.exists(self.config_file):
                print(f"配置文件不存在: {self.config_file}")
                return
            
            with open(self.config_file, 'r', encoding='utf-8') as f:
                config = json.load(f)
            
            plans = config.get('plans', [])
            if not plans:
                print("没有定投计划")
                return
            
            # 找到所有启用计划的最早开始日期
            enabled_plans = [p for p in plans if p.get('enabled', True)]
            if not enabled_plans:
                print("没有启用的定投计划")
                return
            
            start_dates = [datetime.strptime(p['start_date'], '%Y-%m-%d') for p in enabled_plans]
            start_date_str = min(start_dates).strftime('%Y-%m-%d')
        
        print(f"批量导入定投交易: {start_date_str} ~ {end_date_str}")
        print(f"说明: 根据各计划的frequency（每日/每周/每月/每季度）规则生成交易记录\n")

        transactions = self.generate_transactions(start_date=start_date_str, end_date=end_date_str)
        
        if not transactions:
            print("没有需要导入的交易记录")
            return
        
        print(f"找到 {len(transactions)} 条需要导入的交易\n")
        
        # 按日期分组
        from collections import defaultdict
        by_date = defaultdict(list)
        for tx in transactions:
            by_date[tx['transaction_date']].append(tx)
        
        # 逐日处理
        for date_str in sorted(by_date.keys()):
            print(f"处理日期: {date_str}")
            
            self.Import_invest_transactions(date_str)

    def generate_transactions(self, plan_id=None, start_date=None, end_date=None):
            """
            生成定投交易记录
            Args:
                plan_id: 计划ID(从1开始), None=所有计划
                start_date: 开始日期
                end_date: 结束日期
            """
            # 加载定投配置
            if not os.path.exists(self.config_file):
                print(f"配置文件不存在: {self.config_file}")
                return []
            
            with open(self.config_file, 'r', encoding='utf-8') as f:
                config = json.load(f)
            
            plans = config.get('plans', [])
            if not plans:
                print("暂无定投计划")
                return []
            
            if start_date is None:
                start_date = datetime.now().strftime('%Y-%m-%d')
            if end_date is None:
                end_date = (datetime.now() + relativedelta(months=3)).strftime('%Y-%m-%d')
            
            start_dt = datetime.strptime(start_date, '%Y-%m-%d')
            end_dt = datetime.strptime(end_date, '%Y-%m-%d')
            
            all_transactions = []
            
            plans_to_process = plans if plan_id is None else [plans[plan_id-1]]
            
            for plan in plans_to_process:
                if not plan.get('enabled', True):
                    continue
                
                plan_start = datetime.strptime(plan['start_date'], '%Y-%m-%d')
                plan_end = datetime.strptime(plan.get('end_date', '2099-12-31'), '%Y-%m-%d')
                
                actual_start = max(start_dt, plan_start)
                actual_end = min(end_dt, plan_end)
                
                if actual_start > actual_end:
                    continue
                
                dates=TradeDateChecker(self.config_file, db_path=self.db_path)
                transactions = dates._generate_dates(plan, actual_start, actual_end)
                all_transactions.extend(transactions)
            

            all_transactions.sort(key=lambda x: x['transaction_date'])
            
            return all_transactions


# 向后兼容的函数接口
def import_auto_invest_date_range(start_date_str=None, end_date_str=None, 
                                 config_file='auto_invest_setting.json', db_path='fund.db'):
    """批量导入定投计划的交易记录
    
    Args:
        start_date_str: 开始日期 'YYYY-MM-DD'（可选）
        end_date_str: 结束日期 'YYYY-MM-DD'（可选，默认为今天）
        config_file: 配置文件路径
        db_path: 数据库路径
    """
    importer = ImportAutoInvest(config_file=config_file, db_path=db_path)
    importer.Import_date_range(start_date_str, end_date_str)


def import_auto_invest_single_date(target_date_str, config_file='auto_invest_setting.json', db_path='fund.db'):
    """导入指定日期的定投交易记录
    
    Args:
        target_date_str: 目标日期 'YYYY-MM-DD'
        config_file: 配置文件路径
        db_path: 数据库路径
    """
    importer = ImportAutoInvest(config_file=config_file, db_path=db_path)
    importer.Import_invest_transactions(target_date_str)


















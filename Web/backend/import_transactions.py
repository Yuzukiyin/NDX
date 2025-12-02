"""
从CSV文件批量导入历史交易记录的模块（PostgreSQL）
"""

import csv
from datetime import datetime
import os
from typing import Optional, Tuple
from sqlalchemy import create_engine, text
from tradeDate import TradeDateChecker

class TransactionImporter:
    def __init__(self, db_url: str | None = None, csv_file='transactions.csv', user_id=1):
        '''初始化交易导入器（仅支持PostgreSQL）'''
        self.csv_file = csv_file
        self.user_id = user_id
        
        # 获取数据库URL
        if db_url:
            self.db_url = self._resolve_db_url(db_url)
        else:
            self.db_url = os.getenv('DATABASE_URL', 'postgresql://localhost:5432/ndx')
            self.db_url = self._resolve_db_url(self.db_url)
        
        self.engine = create_engine(self.db_url, future=True)

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

    def add_transaction(self, 
                       fund_code: str,
                       fund_name: str,
                       transaction_type: str, 
                       shares: float,
                       unit_nav: float,
                       note: str = '',
                       transaction_date: Optional[str] = None,
                       nav_date: Optional[str] = None,
                       target_amount: Optional[float] = None):
       
        if transaction_date is None:
            transaction_date = datetime.now().strftime('%Y-%m-%d')
        
        # 按精度约束进行四舍五入：shares(6), unit_nav(6), amount(2)
        if shares is not None and unit_nav is not None:
            shares = round(shares, 6)
            unit_nav = round(unit_nav, 6)
            amount = round(shares * unit_nav, 2)
        else:
            amount = 0  # 待确认记录
        
        if target_amount is not None:
            target_amount = round(target_amount, 2)
        
        with self.engine.connect() as conn:
            conn.execute(
                text('''
                    INSERT INTO transactions (
                        user_id, fund_code, fund_name, transaction_date, nav_date, transaction_type,
                        target_amount, shares, unit_nav, amount, note
                    )
                    VALUES (:user_id, :fund_code, :fund_name, :transaction_date, :nav_date, :transaction_type,
                            :target_amount, :shares, :unit_nav, :amount, :note)
                '''),
                {
                    'user_id': self.user_id,
                    'fund_code': fund_code,
                    'fund_name': fund_name,
                    'transaction_date': transaction_date,
                    'nav_date': nav_date,
                    'transaction_type': transaction_type,
                    'target_amount': target_amount,
                    'shares': shares,
                    'unit_nav': unit_nav,
                    'amount': amount,
                    'note': note
                }
            )
            conn.commit()
        
        if shares is not None and unit_nav is not None:
            print(f"{transaction_type}：{fund_name}({fund_code}) {shares:.2f}份 @ ¥{unit_nav:.4f} = ¥{amount:.2f}")
        else:
            print(f"{transaction_type}[待确认]：{fund_name}({fund_code}) 交易日={transaction_date} 净值日={nav_date} 金额=¥{target_amount:.2f} 等待净值")

    def import_from_csv(self, skip_header=True):
        """
        从CSV文件导入交易记录（PostgreSQL）
        
        Args:
            skip_header: 跳过第一行标题
        """
        if not os.path.exists(self.csv_file):
            print(f"文件不存在: {self.csv_file}")
            return
        
        print(f"导入交易记录: {self.csv_file}")
        
        success_count = 0
        error_count = 0
        errors = []
        
        try:
            checker = TradeDateChecker(db_url=self.db_url)
            with open(self.csv_file, 'r', encoding='utf-8-sig') as f:
                reader = csv.reader(f)
                if skip_header:
                    _ = next(reader, None)
                line_start = 2 if skip_header else 1
                
                for row_num, row in enumerate(reader, start=line_start):
                    try:
                        # 支持两种格式:
                        # 旧格式: fund_code,fund_name,transaction_date,transaction_type,shares,unit_nav,note
                        # 新简化格式: fund_code,transaction_date,transaction_type,amount,note
                        if len(row) >= 7:  # 旧格式
                            fund_code = row[0].strip()
                            fund_name = row[1].strip()
                            transaction_date = row[2].strip()
                            transaction_type = row[3].strip()
                            shares = float(row[4].strip())
                            unit_nav = float(row[5].strip())
                            note = row[6].strip() if len(row) > 6 else ''
                            simplified = False
                        elif len(row) >= 5:  # 新格式
                            fund_code = row[0].strip()
                            transaction_date = row[1].strip()
                            transaction_type = row[2].strip()
                            amount = float(row[3].strip())
                            note = row[4].strip() if len(row) > 4 else ''
                            simplified = True
                        else:
                            raise ValueError("列数不足，必须是旧格式>=7列或新格式>=5列")

                        # 验证类型
                        if transaction_type not in ['买入', '卖出']:
                            raise ValueError(f"交易类型必须是'买入'或'卖出'，当前值: {transaction_type}")
                        
                        # 验证日期
                        try:
                            datetime.strptime(transaction_date, '%Y-%m-%d')
                        except ValueError:
                            raise ValueError(f"日期格式错误，应为 YYYY-MM-DD，当前值: {transaction_date}")

                        if simplified:
                            if amount <= 0:
                                raise ValueError(f"金额必须大于0，当前值: {amount}")
                            
                            trans_dt = datetime.strptime(transaction_date, '%Y-%m-%d')
                            # 净值日期：非交易日使用下一交易日
                            if checker.is_trading_day(trans_dt):
                                nav_date_str = transaction_date
                            else:
                                nav_dt = checker.get_next_trading_day(trans_dt, 1)
                                nav_date_str = nav_dt.strftime('%Y-%m-%d')
                            
                            target_amount_val = amount
                            # 查询净值日 NAV
                            nav_info = self._get_nav_for_date(fund_code, nav_date_str)
                            if not nav_info:
                                print(f"净值日({nav_date_str})净值未抓取，创建待确认记录")
                                self.add_transaction(
                                    fund_code=fund_code,
                                    fund_name='',
                                    transaction_type=transaction_type,
                                    shares=None,
                                    unit_nav=None,
                                    note=note + '[待确认]',
                                    transaction_date=transaction_date,
                                    nav_date=nav_date_str,
                                    target_amount=target_amount_val
                                )
                                success_count += 1
                                continue
                            
                            fund_name, unit_nav = nav_info
                            if unit_nav <= 0:
                                raise ValueError("净值无效")
                            shares = round(amount / unit_nav, 6)
                            amount = round(shares * unit_nav, 2)
                        else:
                            target_amount_val = None
                            trans_dt = datetime.strptime(transaction_date, '%Y-%m-%d')
                            
                            if checker.is_trading_day(trans_dt):
                                nav_date_str = transaction_date
                            else:
                                nav_dt = checker.get_next_trading_day(trans_dt, 1)
                                nav_date_str = nav_dt.strftime('%Y-%m-%d')
                            
                            if shares <= 0:
                                raise ValueError(f"份额必须大于0，当前值: {shares}")
                            if unit_nav <= 0:
                                raise ValueError(f"单位净值必须大于0，当前值: {unit_nav}")
                            
                            # 校验提供的净值是否与净值日净值一致（仅作提示）
                            nav_check = self._get_nav_for_date(fund_code, nav_date_str)
                            if nav_check:
                                if abs(nav_check[1] - unit_nav) > 1e-4:
                                    print(f"行{row_num} 提供净值与净值日({nav_date_str})净值不一致，数据库={nav_check[1]:.4f} vs 提供={unit_nav:.4f}")
                            
                            amount = round(shares * unit_nav, 2)

                        # 导入
                        self.add_transaction(
                            fund_code=fund_code,
                            fund_name=fund_name,
                            transaction_type=transaction_type,
                            shares=shares,
                            unit_nav=unit_nav,
                            note=note,
                            transaction_date=transaction_date,
                            nav_date=nav_date_str,
                            target_amount=target_amount_val
                        )
                        mode = '简化' if simplified else '旧'
                        print(f"成功({mode}格式) shares={shares:.2f} nav={unit_nav:.4f} amount=¥{amount:.2f}\n")
                        success_count += 1
                        
                    except Exception as e:
                        error_msg = f"第{row_num}行错误: {str(e)}"
                        errors.append(error_msg)
                        print(f"{str(e)}\n")
                        error_count += 1
        
        except Exception as e:
            print(f"读取CSV文件失败: {e}")
            return
        
        print(f"导入完成")
        print(f"成功: {success_count} 条")
        if error_count > 0:
            print(f"失败: {error_count} 条")
            print(f"\n错误详情:")
            for error in errors:
                print(f"{error}")

    def _get_nav_for_date(self, fund_code: str, transaction_date: str) -> Optional[Tuple[str, float]]:
        """获取某基金在指定日期的 unit_nav 和 fund_name（从共享净值表）
        Returns: (fund_name, unit_nav) 或 None
        """
        with self.engine.connect() as conn:
            result = conn.execute(
                text("""
                    SELECT fund_name, unit_nav FROM fund_nav_history 
                    WHERE fund_code=:fund_code AND price_date=:price_date 
                    ORDER BY fetched_at DESC LIMIT 1
                """),
                {'fund_code': fund_code, 'price_date': transaction_date}
            )
            row = result.fetchone()
        
        if not row:
            return None
        return row[0], float(row[1])


# 向后兼容的函数接口
def import_from_csv(csv_file='transactions.csv', db_url=None, skip_header=True, user_id=1):
    """从CSV文件导入交易记录（PostgreSQL）
    
    Args:
        csv_file: CSV文件路径
        db_url: PostgreSQL数据库URL
        skip_header: 是否跳过第一行标题
        user_id: 用户ID
    """
    importer = TransactionImporter(db_url=db_url, csv_file=csv_file, user_id=user_id)
    importer.import_from_csv(skip_header=skip_header)


def add_transaction(fund_code, fund_name, transaction_type, shares, unit_nav, 
                   note='', transaction_date=None, nav_date=None, target_amount=None, 
                   db_url=None, user_id=1):
    """添加单笔交易记录（PostgreSQL）
    
    Args:
        fund_code: 基金代码
        fund_name: 基金名称
        transaction_type: 交易类型（'买入'或'卖出'）
        shares: 份额
        unit_nav: 单位净值
        note: 备注
        transaction_date: 交易日期
        nav_date: 净值日期
        target_amount: 目标金额
        db_url: PostgreSQL数据库URL
        user_id: 用户ID
    """
    importer = TransactionImporter(db_url=db_url, user_id=user_id)
    importer.add_transaction(fund_code, fund_name, transaction_type, shares, unit_nav, 
                            note, transaction_date, nav_date, target_amount)

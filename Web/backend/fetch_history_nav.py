'''获取定投计划中基金历史净值的模块（PostgreSQL）'''

import sys
import os
import json
from datetime import datetime, timedelta
from sqlalchemy import create_engine, text
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'fundSpider'))
from fundSpider.fund_info import FuncInfo

class HistoryNavFetcher:
    def __init__(self, data_source='fundSpider', db_url: str | None = None, user_id: int = 1):
        '''初始化净值抓取器（仅支持PostgreSQL）'''
        self.data_source = data_source
        self.user_id = user_id
        
        # 获取数据库URL（仅支持PostgreSQL）
        if db_url:
            self.db_url = self._resolve_db_url(db_url)
        else:
            # 从环境变量获取
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

    def load_enabled_plans(self):
        """从数据库读取启用的定投计划并返回列表字典
        
        从 auto_invest_plans 表读取当前用户的定投计划（仅PostgreSQL）
        
        字段: plan_name, fund_code, fund_name, amount, frequency, start_date, end_date, enabled
        仅保留 enabled=true 的计划
        """
        # 从数据库读取定投计划
        try:
            with self.engine.connect() as conn:
                result = conn.execute(
                    text("""
                        SELECT plan_name, fund_code, fund_name, amount, frequency, 
                               start_date::text, end_date::text, enabled
                        FROM auto_invest_plans
                        WHERE user_id = :user_id AND enabled = true
                    """),
                    {"user_id": self.user_id}
                )
                rows = result.fetchall()
                if rows:
                    results = []
                    for row in rows:
                        results.append({
                            'plan_name': row[0],
                            'fund_code': row[1],
                            'fund_name': row[2],
                            'amount': float(row[3]),
                            'frequency': row[4],
                            'start_date': row[5],  # 已经是字符串
                            'end_date': row[6],    # 已经是字符串
                            'enabled': bool(row[7])
                        })
                    print(f"从数据库加载了 {len(results)} 个启用的定投计划")
                    return results
        except Exception as e:
            print(f"从数据库读取计划失败: {e}")
            return []

    def fetch_fund_history(self, fund_code, fund_name, start_date, end_date):
        """
        获取单个基金的历史净值数据
        
        Args:
            fund_code: 基金代码
            fund_name: 基金名称
            start_date: 开始日期 (datetime对象、字符串 'YYYY-MM-DD' 或 None 表示从基金成立日起)
            end_date: 结束日期 (datetime对象或字符串 'YYYY-MM-DD')
    
        Returns:
            DataFrame: 包含历史净值数据的DataFrame（本函数只抓取数据不写入数据库）
        """
        print(f"正在获取: {fund_name} ({fund_code})")
        
        # 如果 start_date 为 None，设为一个足够早的日期，让API返回从基金成立日开始的数据
        if start_date is None:
            start_date = datetime(2000, 1, 1)
        
        # 如果 end_date 为 None，设为今天
        if end_date is None:
            end_date = datetime.now()
        
        if isinstance(start_date, str):
            start_date = datetime.strptime(start_date, '%Y-%m-%d')
        if isinstance(end_date, str):
            end_date = datetime.strptime(end_date, '%Y-%m-%d')
        
        start_display = '基金成立日'  # 显示为"基金成立日"更友好
        end_display = end_date.strftime('%Y-%m-%d')
        print(f"时间范围: {start_display} ~ {end_display}")
        
        fund = FuncInfo(code=fund_code, name=fund_name)
        
        fund.load_net_value_info(start_date, end_date)
        
        df = fund.get_data_frame()
        
        if df.empty:
            print("未获取到数据")
            return None
        
        print(f"成功获取 {len(df)} 条记录")
        return df
    
    def check_nav_exists(self, fund_code, price_date):
        """检查数据库中是否已存在指定基金某日的历史净值
        
        Args:
            fund_code: 基金代码
            price_date: 净值日期 (字符串 'YYYY-MM-DD')
        
        Returns:
            bool: True=已存在, False=不存在
        """
        with self.engine.connect() as conn:
            result = conn.execute(
                text(
                    """SELECT 1 FROM fund_nav_history
                        WHERE fund_code = :fund_code AND price_date = :price_date AND data_source = :source
                        LIMIT 1"""
                ),
                {"fund_code": fund_code, "price_date": price_date, "source": self.data_source},
            )
            return result.first() is not None

    def get_latest_nav_date(self, fund_code):
        """获取指定基金在当前 data_source 下已存在的最新净值日期

        Args:
            fund_code: 基金代码
        Returns:
            str | None: 最新 price_date (YYYY-MM-DD) 如果不存在返回 None
        """
        with self.engine.connect() as conn:
            latest = conn.execute(
                text(
                    """SELECT MAX(price_date)::text FROM fund_nav_history
                        WHERE fund_code = :fund_code AND data_source = :source"""
                ),
                {"fund_code": fund_code, "source": self.data_source},
            ).scalar()
        return latest

    def save_nav_history(self, df, fund_code, fund_name):
        """将 DataFrame 写入 fund_nav_history，跳过已存在的日期"""
        if df is None or df.empty:
            print(f"{fund_code} 没有可写入的净值数据")
            return 0
        
        # 一次性查询所有已存在的日期，避免每行都查询数据库
        with self.engine.connect() as conn:
            result = conn.execute(
                text("""
                    SELECT price_date FROM fund_nav_history
                    WHERE fund_code = :fund_code AND data_source = :source
                """),
                {"fund_code": fund_code, "source": self.data_source}
            )
            existing_dates = {row[0] for row in result.fetchall()}
        
        records = []
        skipped_count = 0
        for _, row in df.iterrows():
            price_date = row.get('净值日期')
            
            # 检查该日期数据是否已存在
            if price_date in existing_dates:
                skipped_count += 1
                continue
            
            unit_nav = row.get('单位净值')
            cumulative_nav = row.get('累计净值')
            daily_growth = row.get('日增长率')
        
            if isinstance(daily_growth, str):
                if daily_growth.strip() == '--' or daily_growth.strip() == '':
                    daily_growth_rate = None
                else:
                    daily_growth_rate = daily_growth.replace('%', '')
                    try:
                        daily_growth_rate = float(daily_growth_rate)
                    except ValueError:
                        daily_growth_rate = None
            else:
                try:
                    daily_growth_rate = float(daily_growth) if daily_growth is not None else None
                except Exception:
                    daily_growth_rate = None
            try:
                unit_nav_f = float(unit_nav)
            except Exception:
                continue
            cumulative_nav_f = None
            try:
                if cumulative_nav not in (None, '', '--'):
                    cumulative_nav_f = float(cumulative_nav)
            except Exception:
                cumulative_nav_f = None
            records.append((fund_code, fund_name, price_date, unit_nav_f, cumulative_nav_f, daily_growth_rate,
                             self.data_source))
        if skipped_count > 0:
            print(f"跳过已存在的 {skipped_count} 条记录")
        
        if not records:
            print(f"{fund_code} 没有可写入的有效净值行（全部已存在或无效）")
            return 0
        
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
        payloads = [
            {
                'fund_code': rec[0],
                'fund_name': rec[1],
                'price_date': rec[2],
                'unit_nav': rec[3],
                'cumulative_nav': rec[4],
                'daily_growth_rate': rec[5],
                'data_source': rec[6],
            }
            for rec in records
        ]

        with self.engine.begin() as conn:
            result = conn.execute(sql, payloads)
            affected = result.rowcount or 0
        
        total_processed = len(records) + skipped_count
        print(f"写入 fund_nav_history 完成: {fund_code} 新增 {len(records)} 行，跳过 {skipped_count} 行，共处理 {total_processed} 行")
        return affected

    def import_enabled_plans(self, start_date_override: str | None = None, end_date_override: str | None = None):
            """批量导入启用计划历史净值并返回写入明细
            Args:
                start_date_override: 可选覆盖的开始日期 (字符串 'YYYY-MM-DD'，留空则从基金成立日起)
                end_date_override: 可选覆盖的结束日期 (字符串 'YYYY-MM-DD'，留空则到今天)
            
            Returns:
                List[Dict]: 每个计划的导入结果明细
            """

            plans = self.load_enabled_plans()
            if not plans:
                return []
            end_used_global = end_date_override or datetime.now().strftime('%Y-%m-%d')
            details = []
            print(f"\n将导入 {len(plans)} 个启用计划到数据库: {self.db_url}")
            for plan in plans:
                fund_code = plan['fund_code']
                fund_name = plan['fund_name']
                plan_name = plan['plan_name']
                # 计算起始日期：如果存在最新净值日期，则从其下一日开始；否则视为基金成立日 (None)
                latest_date = self.get_latest_nav_date(fund_code)
                start_used = None
                if latest_date:
                    try:
                        dt_latest = datetime.strptime(latest_date, '%Y-%m-%d')
                        next_day = dt_latest + timedelta(days=1)
                        start_used = next_day.strftime('%Y-%m-%d')
                    except Exception:
                        start_used = None
                # 如果用户提供了覆盖开始日期，取二者中较晚的那个
                if start_date_override:
                    try:
                        dt_override = datetime.strptime(start_date_override, '%Y-%m-%d')
                        if start_used:
                            dt_start_used = datetime.strptime(start_used, '%Y-%m-%d')
                            if dt_override > dt_start_used:
                                start_used = start_date_override
                        else:
                            start_used = start_date_override
                    except Exception:
                        pass
                end_used = end_used_global
                start_display = start_used or '基金成立日'
                print(f"\n[{fund_code}] {fund_name}\n计划: {plan_name}\n起始: {start_display} 结束: {end_used}")
                record = {
                    'fund_code': fund_code,
                    'fund_name': fund_name,
                    'plan_name': plan_name,
                    'start_used': start_display,
                    'end_used': end_used,
                    'rows_written': 0,
                    'success': False,
                    'error': ''
                }
                try:
                    # 若最新日期已覆盖到结束日期之前（即没有新数据需要抓取），直接跳过抓取
                    if start_used and start_used > end_used:
                        print(f"无需要更新的净值：最新已存在日期 {latest_date} 已不早于结束日期 {end_used}")
                        record['success'] = True
                        details.append(record)
                        continue
                    df = self.fetch_fund_history(fund_code, fund_name, start_used, end_used)
                    if df is not None and not df.empty:
                        rows = self.save_nav_history(df, fund_code, fund_name)
                        record['rows_written'] = rows
                    record['success'] = True
                except Exception as e:
                    record['error'] = str(e)
                    print(f"导入失败 {fund_name}({fund_code}): {e}")
                details.append(record)
            # 汇总
            success_cnt = sum(1 for d in details if d['success'])
            print(f"\n完成：成功 {success_cnt}/{len(details)}")
            return details



def fetch_nav_history(start_date_override=None, end_date_override=None, 
                     db_url=None, data_source='fundSpider', user_id=1):
    """批量导入启用计划的历史净值（PostgreSQL）
    
    Args:
        start_date_override: 可选覆盖的开始日期 (字符串 'YYYY-MM-DD'，留空则从基金成立日起)
        end_date_override: 可选覆盖的结束日期 (字符串 'YYYY-MM-DD'，留空则到今天)
        db_url: PostgreSQL数据库URL
        data_source: 数据源标识
        user_id: 用户ID
    
    Returns:
        List[Dict]: 每个计划的导入结果明细
    """
    fetcher = HistoryNavFetcher(db_url=db_url, data_source=data_source, user_id=user_id)
    return fetcher.import_enabled_plans(start_date_override, end_date_override)


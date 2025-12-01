'''获取定投计划中基金历史净值的模块'''
#auto_invest_setting.json
#fund.db

import sys
import os
import json
import sqlite3
from datetime import datetime, timedelta
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'fundSpider'))
from fundSpider.fund_info import FuncInfo

class HistoryNavFetcher:
    def __init__(self, config_path='auto_invest_setting.json', db_path='fund.db', data_source='fundSpider', user_id=1):
        '''设置默认输出目录和配置文件路径'''
        self.config_path = config_path
        self.db_path = db_path
        self.data_source = data_source
        self.user_id = user_id  # 添加user_id支持多租户

    def load_enabled_plans(self):
        """读取启用定投计划并返回列表字典

        字段: plan_name, fund_code, fund_name, amount, frequency, start_date, end_date, enabled
        仅保留 enabled=true 且关键字段存在的计划
        """
        full_path = self.config_path
        if not os.path.isabs(full_path):
            full_path = os.path.join(os.path.dirname(__file__), self.config_path)
        if not os.path.exists(full_path):
            print(f"未找到配置文件: {full_path}")
            return []
        try:
            with open(full_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
        except Exception as e:
            print(f"读取配置文件失败: {e}")
            return []
        raw_plans = data.get('plans', [])
        results = []
        for p in raw_plans:
            if not p.get('enabled'):
                continue
            if not p.get('fund_code') or not p.get('fund_name'):
                continue
            results.append({
                'plan_name': p.get('plan_name',''),
                'fund_code': p['fund_code'],
                'fund_name': p['fund_name'],
                'amount': p.get('amount', 0.0),
                'frequency': p.get('frequency',''),
                'start_date': p.get('start_date') or (datetime.now() - timedelta(days=365)).strftime('%Y-%m-%d'),
                'end_date': p.get('end_date') or '2099-12-31',
                'enabled': True
            })
        if not results:
            print("配置文件中没有启用的计划")
        return results

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
        conn = sqlite3.connect(self.db_path)
        cur = conn.cursor()
        cur.execute("""
            SELECT COUNT(*) FROM fund_nav_history
            WHERE user_id = ? AND fund_code = ? AND price_date = ? AND data_source = ?
        """, (self.user_id, fund_code, price_date, self.data_source))
        count = cur.fetchone()[0]
        conn.close()
        return count > 0

    def get_latest_nav_date(self, fund_code):
        """获取指定基金在当前 data_source 下已存在的最新净值日期

        Args:
            fund_code: 基金代码
        Returns:
            str | None: 最新 price_date (YYYY-MM-DD) 如果不存在返回 None
        """
        conn = sqlite3.connect(self.db_path)
        cur = conn.cursor()
        cur.execute("""
            SELECT MAX(price_date) FROM fund_nav_history
            WHERE user_id = ? AND fund_code = ? AND data_source = ?
        """, (self.user_id, fund_code, self.data_source))
        row = cur.fetchone()
        conn.close()
        latest = row[0] if row and row[0] else None
        return latest

    def save_nav_history(self, df, fund_code, fund_name):
        """将 DataFrame 写入 fund_nav_history (fund.db)，跳过已存在的日期"""
        if df is None or df.empty:
            print(f"{fund_code} 没有可写入的净值数据")
            return 0
        records = []
        skipped_count = 0
        for _, row in df.iterrows():
            price_date = row.get('净值日期')
            
            # 检查该日期数据是否已存在
            if self.check_nav_exists(fund_code, price_date):
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
            records.append((self.user_id, fund_code, fund_name, price_date, unit_nav_f, cumulative_nav_f, daily_growth_rate,
                             self.data_source))
        if skipped_count > 0:
            print(f"跳过已存在的 {skipped_count} 条记录")
        
        if not records:
            print(f"{fund_code} 没有可写入的有效净值行（全部已存在或无效）")
            return 0
        
        conn = sqlite3.connect(self.db_path)
        cur = conn.cursor()
        cur.execute("""
        CREATE TABLE IF NOT EXISTS fund_nav_history (
            nav_id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            fund_code TEXT NOT NULL,
            fund_name TEXT NOT NULL,
            price_date TEXT NOT NULL,
            unit_nav REAL NOT NULL,
            cumulative_nav REAL,
            daily_growth_rate REAL,
            data_source TEXT DEFAULT 'fundSpider',
            fetched_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(user_id, fund_code, price_date, data_source)
        );
        """)
        sql = """
        INSERT INTO fund_nav_history (
            user_id,fund_code,fund_name,price_date,unit_nav,cumulative_nav,daily_growth_rate,
            data_source
        ) VALUES (?,?,?,?,?,?,?,?)
        ON CONFLICT(fund_code, price_date, data_source) DO UPDATE SET
            unit_nav=excluded.unit_nav,
            cumulative_nav=excluded.cumulative_nav,
            daily_growth_rate=excluded.daily_growth_rate,
            fetched_at=CURRENT_TIMESTAMP;
        """
        cur.executemany(sql, records)
        conn.commit()
        affected = cur.rowcount
        conn.close()
        
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
            print(f"\n将导入 {len(plans)} 个启用计划到数据库: {self.db_path}")
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
                     config_path='auto_invest_setting.json', db_path='fund.db', data_source='fundSpider'):
    """批量导入启用计划的历史净值
    
    Args:
        start_date_override: 可选覆盖的开始日期 (字符串 'YYYY-MM-DD'，留空则从基金成立日起)
        end_date_override: 可选覆盖的结束日期 (字符串 'YYYY-MM-DD'，留空则到今天)
        config_path: 配置文件路径
        db_path: 数据库路径
        data_source: 数据源标识
    
    Returns:
        List[Dict]: 每个计划的导入结果明细
    """
    fetcher = HistoryNavFetcher(config_path=config_path, db_path=db_path, data_source=data_source)
    return fetcher.import_enabled_plans(start_date_override, end_date_override)


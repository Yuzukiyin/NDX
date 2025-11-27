"""
历史净值走势图生成工具
"""

from __future__ import annotations
import sqlite3
from dataclasses import dataclass
from datetime import datetime
from typing import List, Optional
import os
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates


@dataclass
class NavRecord:
    """净值记录数据结构"""
    date: str
    unit_nav: float
    cumulative_nav: Optional[float]
    daily_growth_rate: Optional[float]


class NavPlotter:
    """基金历史净值数据导出与绘图类"""
    
    def __init__(self, db_path: str = 'fund.db'):
        """初始化
        
        :param db_path: 数据库路径
        """
        self.db_path = db_path
    
    @staticmethod
    def _parse_date(s: Optional[str]) -> Optional[datetime]:
        """解析日期字符串"""
        if not s:
            return None
        return datetime.strptime(s, '%Y-%m-%d')
    
    @staticmethod
    def _ensure_dir(path: str) -> None:
        """确保目录存在"""
        dir_path = os.path.dirname(os.path.abspath(path))
        if dir_path and not os.path.exists(dir_path):
            os.makedirs(dir_path, exist_ok=True)
    
    def get_nav_history(self, 
                       fund_code: str,
                       start_date: Optional[str] = None,
                       end_date: Optional[str] = None) -> List[NavRecord]:
        """从数据库查询指定基金历史净值记录 (按 price_date 升序)
        
        :param fund_code: 基金代码
        :param start_date: 起始日期 (YYYY-MM-DD) 可空
        :param end_date: 结束日期 (YYYY-MM-DD) 可空
        :return: NavRecord 列表
        """
        start_dt = self._parse_date(start_date)
        end_dt = self._parse_date(end_date)
        conn = sqlite3.connect(self.db_path)
        cur = conn.cursor()
        params = [fund_code]
        sql = "SELECT price_date, unit_nav, cumulative_nav, daily_growth_rate FROM fund_nav_history WHERE fund_code = ?"
        if start_dt:
            sql += " AND price_date >= ?"
            params.append(start_dt.strftime('%Y-%m-%d'))
        if end_dt:
            sql += " AND price_date <= ?"
            params.append(end_dt.strftime('%Y-%m-%d'))
        sql += " ORDER BY price_date ASC"
        cur.execute(sql, params)
        rows = cur.fetchall()
        conn.close()
        
        records: List[NavRecord] = []
        for r in rows:
            price_date, unit_nav, cumulative_nav, daily_rate = r
            try:
                unit_nav_f = float(unit_nav)
            except Exception:
                continue
            cum_f = None
            if cumulative_nav is not None:
                try:
                    cum_f = float(cumulative_nav)
                except Exception:
                    cum_f = None
            rate_f = None
            if daily_rate is not None:
                try:
                    rate_f = float(daily_rate)
                except Exception:
                    rate_f = None
            records.append(NavRecord(price_date, unit_nav_f, cum_f, rate_f))
        return records

    def export_csv(self, records: List[NavRecord], path: str) -> None:
        """导出 CSV 文件供 Origin 导入
        
        :param records: 净值记录列表
        :param path: 输出文件路径
        """
        self._ensure_dir(path)
        
        df = pd.DataFrame([{
            'Date': r.date,
            'Unit_NAV': r.unit_nav,
            'Cumulative_NAV': r.cumulative_nav if r.cumulative_nav is not None else '',
            'Daily_Growth_Rate': r.daily_growth_rate if r.daily_growth_rate is not None else ''
        } for r in records])
        df.to_csv(path, index=False, encoding='utf-8')
        print(f"CSV 导出完成: {path} ({len(records)} 条记录)")

    def plot_png(self, records: List[NavRecord], path: str, fund_code: str) -> None:
        """使用 matplotlib 生成 PNG 折线图
        
        :param records: 净值记录列表
        :param path: 输出图片路径
        :param fund_code: 基金代码（用于标题）
        """
        if not records:
            print('没有记录可绘制')
            return
        
        self._ensure_dir(path)
        
        dates = [datetime.strptime(r.date, '%Y-%m-%d') for r in records]
        values = [r.unit_nav for r in records]
        
        plt.rcParams['font.sans-serif'] = ['SimHei', 'Microsoft YaHei']
        plt.rcParams['axes.unicode_minus'] = False
        
        fig, ax = plt.subplots(figsize=(12, 6))
        ax.plot(dates, values, label='单位净值', color='#1f77b4', linewidth=1.5)
        ax.set_xlabel('日期', fontsize=11)
        ax.set_ylabel('单位净值', fontsize=11)
        ax.set_title(f'基金 {fund_code} 历史净值走势', fontsize=13, fontweight='bold')
        ax.grid(alpha=0.3, linestyle='--')
        ax.legend(loc='best')
        
        ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d'))
        fig.autofmt_xdate()
        
        plt.tight_layout()
        plt.savefig(path, dpi=150, bbox_inches='tight')
        print(f"PNG 图像保存: {path}")
        plt.close()
    
    def export_nav_data(self,
                       fund_code: str, 
                       output_path: Optional[str] = None,
                       start_date: Optional[str] = None,
                       end_date: Optional[str] = None,
                       mode: str = 'both') -> bool:
        """导出历史净值数据
        
        :param fund_code: 基金代码
        :param output_path: 输出文件路径（不含扩展名，留空则自动生成为 nav_<基金代码>_<基金名>）
        :param start_date: 起始日期 (可选)
        :param end_date: 结束日期 (可选)
        :param mode: 'csv'=仅CSV供Origin, 'png'=仅matplotlib图片, 'both'=两者都生成
        :return: 是否成功
        """
        print(f"正在查询基金 {fund_code} 的历史净值...")
        records = self.get_nav_history(fund_code, start_date, end_date)
        
        if not records:
            print(f"未找到基金 {fund_code} 的历史净值记录")
            return False
        
        print(f"查询到 {len(records)} 条记录 (日期范围: {records[0].date} ~ {records[-1].date})")
        
        # 生成文件路径：若未指定则自动生成
        if output_path:
            base_path = output_path.rsplit('.', 1)[0] if '.' in output_path else output_path
        else:
            # 从数据库获取基金名称
            conn = sqlite3.connect(self.db_path)
            cur = conn.cursor()
            cur.execute("SELECT DISTINCT fund_name FROM fund_nav_history WHERE fund_code = ? LIMIT 1", (fund_code,))
            row = cur.fetchone()
            conn.close()
            fund_name = row[0] if row else fund_code
            # 自动生成：nav_<基金代码>_<基金名>
            base_path = f"nav_{fund_code}_{fund_name}"
        
        if mode in ['csv', 'both']:
            csv_path = f"{base_path}.csv"
            self.export_csv(records, csv_path)
        
        if mode in ['png', 'both']:
            png_path = f"{base_path}.png"
            self.plot_png(records, png_path, fund_code)
        
        return True


# 向后兼容的函数接口
def export_nav_data(fund_code: str, 
                   output_path: Optional[str] = None,
                   start_date: Optional[str] = None,
                   end_date: Optional[str] = None,
                   mode: str = 'both',
                   db_path: str = 'fund.db') -> bool:
    """导出历史净值数据
    
    :param fund_code: 基金代码
    :param output_path: 输出文件路径（留空自动生成）
    :param start_date: 起始日期 (可选)
    :param end_date: 结束日期 (可选)
    :param mode: 'csv'/'png'/'both'
    :param db_path: 数据库路径
    :return: 是否成功
    """
    plotter = NavPlotter(db_path)
    return plotter.export_nav_data(fund_code, output_path, start_date, end_date, mode)

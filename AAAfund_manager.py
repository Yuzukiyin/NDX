'''基金管理系统'''
#fund.db
#auto_invest_setting.json

from init_database import InitDatabase
from fetch_history_nav import HistoryNavFetcher
from import_transactions import TransactionImporter
from import_auto_invest import ImportAutoInvest
from update_pending_transactions import PendingTransactionUpdater
from nav_plot import NavPlotter

def main():
    # if input("初始化数据库？(y/[n]): ").strip().lower() == 'y':
    #     _ = InitDatabase(db_path='fund.db')
    #     print("数据库初始化完成：已生成 fund.db")

    if input("抓取历史净值？([y]/n): ").strip().lower() != 'n':
        fetcher = HistoryNavFetcher()
        fetcher.import_enabled_plans()
        print("历史净值抓取完成，已写入 fund_nav_history 表")

    # if input("导入历史交易？([y]/n): ").strip().lower() != 'n':
    #     importer = TransactionImporter(db_path='fund.db')
    #     importer.import_from_csv()
    #     print("历史交易导入完成，已写入 transactions 表")

    if input("根据定投计划导入定投交易？([y]/n): ").strip().lower() != 'n':
        importer = ImportAutoInvest(config_file='auto_invest_setting.json', db_path='fund.db')
        importer.Import_date_range()
        print("定投交易导入完成，已写入 transactions 表")
    
    if input("更新待确认交易记录？([y]/n): ").strip().lower() != 'n':
        updater = PendingTransactionUpdater()
        updater.process_pending_records()
        print("待确认交易记录更新完成。")
    
    # if input("导出历史净值数据/图表？(y/[n]): ").strip().lower() == 'y':
    #     fund_code = input("请输入基金代码: ").strip()
    #     if fund_code:
    #         print("选择输出模式:")
    #         print("1.CSV")
    #         print("2.PNG")
    #         print("3.同时输出CSV和PNG")
    #         mode_choice = input("请选择 (1/2/[3]): ").strip() or '3'
    #         mode_map = {'1': 'csv', '2': 'png', '3': 'both'}
    #         mode = mode_map.get(mode_choice, 'both')
            
    #         plotter = NavPlotter()
    #         plotter.export_nav_data(fund_code, None, None, None, mode)
    

if __name__ == '__main__':
    main()




-- ============================================
-- 交易记录表：记录每一笔买入或卖出交易的详细信息
-- ============================================
CREATE TABLE IF NOT EXISTS transactions (
    transaction_id INTEGER PRIMARY KEY AUTOINCREMENT,
    fund_code TEXT NOT NULL,                      -- 基金代码（如 021000）
    fund_name TEXT NOT NULL,                      -- 基金名称
    transaction_date TEXT NOT NULL,               -- 交易日期 (YYYY-MM-DD，实际买入/卖出日期)
    nav_date TEXT,                                -- 净值日期 (YYYY-MM-DD，unit_nav对应的日期，非交易日则为下一交易日)
    transaction_type TEXT NOT NULL CHECK(transaction_type IN ('买入', '卖出')),
    target_amount REAL,                           -- 原始投资金额（简化格式使用，用于计算shares）
    shares REAL,                                  -- 交易份额（保留2位小数，待确认时可为NULL）
    unit_nav REAL,                                -- 单位净值（nav_date当天的净值，保留4位小数，待确认时可为NULL）
    amount REAL NOT NULL DEFAULT 0,               -- 交易金额 = shares * unit_nav（保留2位小数）
    note TEXT,                                    -- 备注
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ============================================
-- 基金概览表：记录每个基金的汇总信息和持仓情况
-- ============================================
CREATE TABLE IF NOT EXISTS fund_overview (
    fund_id INTEGER PRIMARY KEY AUTOINCREMENT,
    fund_code TEXT NOT NULL UNIQUE,               -- 基金代码（唯一）
    fund_name TEXT NOT NULL,                      -- 基金名称
    total_shares REAL DEFAULT 0,                  -- 当前持有份额（保留2位小数）
    total_cost REAL DEFAULT 0,                    -- 总买入成本（保留2位小数）
    average_buy_nav REAL DEFAULT 0,               -- 平均买入净值（保留4位小数）
    first_buy_date TEXT,                          -- 首次买入日期
    last_transaction_date TEXT,                   -- 最近交易日期
    last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ============================================
-- 历史净值明细表：完整存储抓取的每日净值原始信息
-- 原始数据仓库
-- ============================================
CREATE TABLE IF NOT EXISTS fund_nav_history (
    nav_id INTEGER PRIMARY KEY AUTOINCREMENT,
    fund_code TEXT NOT NULL,                          -- 基金代码
    fund_name TEXT NOT NULL,                          -- 基金名称
    price_date TEXT NOT NULL,                         -- 净值日期 (YYYY-MM-DD)
    unit_nav REAL NOT NULL,                           -- 单位净值（4位小数）
    cumulative_nav REAL,                              -- 累计净值（可为空，仅存档）
    daily_growth_rate REAL,                           -- 日增长率%（可为空，2位小数）
    data_source TEXT DEFAULT 'fundSpider',            -- 数据来源标记
    fetched_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(fund_code, price_date, data_source)
);

-- 提高查询效率的索引（按基金+日期区间查询较多）
CREATE INDEX IF NOT EXISTS idx_fund_nav_history_code_date
ON fund_nav_history(fund_code, price_date);

-- ============================================
-- 触发器1：更新交易记录后，自动更新基金概览
-- ============================================
DROP TRIGGER IF EXISTS update_fund_overview_after_insert;
CREATE TRIGGER update_fund_overview_after_insert
AFTER INSERT ON transactions
FOR EACH ROW
WHEN NEW.shares IS NOT NULL AND NEW.unit_nav IS NOT NULL AND NEW.amount IS NOT NULL
BEGIN
    -- 如果基金不存在，先插入
    INSERT OR IGNORE INTO fund_overview (
        fund_code, fund_name, total_shares, total_cost, average_buy_nav, first_buy_date
    )
    VALUES (NEW.fund_code, NEW.fund_name, 0, 0, 0, NEW.transaction_date);
    
    -- 更新基金概览
    UPDATE fund_overview
    SET 
        -- 更新总份额（保留2位小数）
        total_shares = ROUND(total_shares + CASE 
            WHEN NEW.transaction_type = '买入' THEN NEW.shares
            WHEN NEW.transaction_type = '卖出' THEN -NEW.shares
            ELSE 0
        END, 2),
        -- 更新总成本（买入增加，卖出不影响，保留2位小数）
        total_cost = ROUND(total_cost + CASE 
            WHEN NEW.transaction_type = '买入' THEN NEW.amount
            ELSE 0
        END, 2),
        -- 重新计算平均买入净值（保留4位小数）
        average_buy_nav = CASE
            WHEN ROUND(total_shares + CASE 
                    WHEN NEW.transaction_type = '买入' THEN NEW.shares
                    WHEN NEW.transaction_type = '卖出' THEN -NEW.shares
                    ELSE 0
                END, 2) = 0 THEN 0
            ELSE ROUND((total_cost + CASE 
                    WHEN NEW.transaction_type = '买入' THEN NEW.amount
                    ELSE 0
                END) /
                ROUND(total_shares + CASE 
                    WHEN NEW.transaction_type = '买入' THEN NEW.shares
                    WHEN NEW.transaction_type = '卖出' THEN -NEW.shares
                    ELSE 0
                END, 2), 4)
        END,
        -- 更新最近交易日期
        last_transaction_date = NEW.transaction_date,
        last_updated = CURRENT_TIMESTAMP
    WHERE fund_code = NEW.fund_code;
END;

-- ============================================
-- 触发器2：删除交易后，重新计算基金概览
-- ============================================
DROP TRIGGER IF EXISTS update_fund_overview_after_delete;
CREATE TRIGGER update_fund_overview_after_delete
AFTER DELETE ON transactions
FOR EACH ROW
WHEN OLD.shares IS NOT NULL AND OLD.unit_nav IS NOT NULL AND OLD.amount IS NOT NULL
BEGIN
    UPDATE fund_overview
    SET 
        total_shares = ROUND((
            SELECT COALESCE(SUM(CASE 
                WHEN transaction_type = '买入' THEN shares
                WHEN transaction_type = '卖出' THEN -shares
                ELSE 0
            END), 0)
            FROM transactions
            WHERE fund_code = OLD.fund_code
        ), 2),
        total_cost = ROUND((
            SELECT COALESCE(SUM(CASE 
                WHEN transaction_type = '买入' THEN amount
                ELSE 0
            END), 0)
            FROM transactions
            WHERE fund_code = OLD.fund_code
        ), 2),
        average_buy_nav = CASE
            WHEN ROUND((SELECT COALESCE(SUM(CASE 
                WHEN transaction_type = '买入' THEN shares
                WHEN transaction_type = '卖出' THEN -shares
                ELSE 0
            END), 0) FROM transactions WHERE fund_code = OLD.fund_code), 2) = 0 THEN 0
            ELSE ROUND((SELECT COALESCE(SUM(CASE 
                WHEN transaction_type = '买入' THEN amount
                ELSE 0
            END), 0) FROM transactions WHERE fund_code = OLD.fund_code) /
            ROUND((SELECT COALESCE(SUM(CASE 
                WHEN transaction_type = '买入' THEN shares
                WHEN transaction_type = '卖出' THEN -shares
                ELSE 0
            END), 0) FROM transactions WHERE fund_code = OLD.fund_code), 2), 4)
        END,
        last_updated = CURRENT_TIMESTAMP
    WHERE fund_code = OLD.fund_code;
END;

-- ============================================
-- 触发器3：待确认记录填充净值后，更新基金概览
-- ============================================
DROP TRIGGER IF EXISTS update_fund_overview_after_fill;
CREATE TRIGGER update_fund_overview_after_fill
AFTER UPDATE ON transactions
FOR EACH ROW
WHEN OLD.shares IS NULL AND NEW.shares IS NOT NULL
BEGIN
    UPDATE fund_overview
    SET 
        total_shares = ROUND(total_shares + CASE 
            WHEN NEW.transaction_type = '买入' THEN NEW.shares
            WHEN NEW.transaction_type = '卖出' THEN -NEW.shares
            ELSE 0
        END, 2),
        total_cost = ROUND(total_cost + CASE 
            WHEN NEW.transaction_type = '买入' THEN NEW.amount
            ELSE 0
        END, 2),
        average_buy_nav = CASE
            WHEN ROUND(total_shares + CASE 
                    WHEN NEW.transaction_type = '买入' THEN NEW.shares
                    WHEN NEW.transaction_type = '卖出' THEN -NEW.shares
                    ELSE 0
                END, 2) = 0 THEN 0
            ELSE ROUND((total_cost + CASE 
                    WHEN NEW.transaction_type = '买入' THEN NEW.amount
                    ELSE 0
                END) /
                ROUND(total_shares + CASE 
                    WHEN NEW.transaction_type = '买入' THEN NEW.shares
                    WHEN NEW.transaction_type = '卖出' THEN -NEW.shares
                    ELSE 0
                END, 2), 4)
        END,
        last_updated = CURRENT_TIMESTAMP
    WHERE fund_code = NEW.fund_code;
END;

-- ============================================
-- 视图：基金实时概览（包含详细交易信息）
-- ============================================
DROP VIEW IF EXISTS fund_realtime_overview;
CREATE VIEW fund_realtime_overview AS
SELECT 
    fo.fund_id,
    fo.fund_code,
    fo.fund_name,
    fo.total_shares,              -- Python层格式化
    fo.total_cost,                -- Python层格式化
    fo.average_buy_nav,           -- Python层格式化
    COALESCE(mp.unit_nav, 0) as current_nav,  -- 完全基于历史净值；无记录则为0
    fo.total_shares * COALESCE(mp.unit_nav, 0) as current_value, -- 用最新净值计算当前市值
    ROUND(fo.total_shares * COALESCE(mp.unit_nav, 0) - fo.total_cost, 2) as profit,
    CASE 
        WHEN fo.total_cost > 0 THEN ROUND((fo.total_shares * COALESCE(mp.unit_nav, 0) - fo.total_cost) / fo.total_cost * 100, 2)
        ELSE 0
    END as profit_rate,
    fo.first_buy_date,
    fo.last_transaction_date,
    COALESCE(mp.price_date, '') as last_nav_date,
    COALESCE(mp.daily_growth_rate, 0) as daily_growth_rate,
    COALESCE(mp.data_source, '') as data_source,
    fo.last_updated
FROM fund_overview fo
LEFT JOIN (
    -- 从历史净值表获取每个基金的最新净值记录（最新日期 + 最新抓取）
    SELECT fA.fund_code, fA.price_date, fA.unit_nav, fA.daily_growth_rate, fA.data_source
    FROM fund_nav_history fA
    JOIN (
        SELECT fund_code, MAX(price_date) AS max_date
        FROM fund_nav_history
        GROUP BY fund_code
    ) mx ON mx.fund_code = fA.fund_code AND mx.max_date = fA.price_date
    JOIN (
        SELECT fund_code, price_date, MAX(fetched_at) AS max_fetch
        FROM fund_nav_history
        GROUP BY fund_code, price_date
    ) mf ON mf.fund_code = fA.fund_code AND mf.price_date = fA.price_date AND mf.max_fetch = fA.fetched_at
) mp ON fo.fund_code = mp.fund_code;

-- ============================================
-- 视图：总利润汇总
-- ============================================
CREATE VIEW IF NOT EXISTS profit_summary AS
SELECT 
    COUNT(*) as total_funds,                              -- 基金数量
    SUM(fo.total_shares) as total_shares,                 -- 总份额
    SUM(fo.total_cost) as total_cost,                     -- 总成本
    SUM(fo.total_shares * COALESCE(mp.unit_nav, 0)) as total_value,  -- 总市值
    SUM(fo.total_shares * COALESCE(mp.unit_nav, 0) - fo.total_cost) as total_profit, -- 总利润
    CASE 
        WHEN SUM(fo.total_cost) > 0 
        THEN (SUM(fo.total_shares * COALESCE(mp.unit_nav, 0) - fo.total_cost) / SUM(fo.total_cost) * 100)
        ELSE 0 
    END as total_return_rate                              -- 总收益率%
FROM fund_overview fo
LEFT JOIN (
    -- 每只基金的最新净值（最新日期 + 最新抓取）
    SELECT fA.fund_code, fA.unit_nav
    FROM fund_nav_history fA
    JOIN (
        SELECT fund_code, MAX(price_date) AS max_date
        FROM fund_nav_history
        GROUP BY fund_code
    ) mx ON mx.fund_code = fA.fund_code AND mx.max_date = fA.price_date
    JOIN (
        SELECT fund_code, price_date, MAX(fetched_at) AS max_fetch
        FROM fund_nav_history
        GROUP BY fund_code, price_date
    ) mf ON mf.fund_code = fA.fund_code AND mf.price_date = fA.price_date AND mf.max_fetch = fA.fetched_at
) mp ON fo.fund_code = mp.fund_code;


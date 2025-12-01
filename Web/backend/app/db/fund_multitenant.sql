-- Fund tables with multi-tenant support (user_id)
-- This script augments ndx_users.db with fund-related tables/views

PRAGMA foreign_keys = ON;

-- =========================
-- Core tables
-- =========================
CREATE TABLE IF NOT EXISTS transactions (
    transaction_id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    fund_code TEXT NOT NULL,
    fund_name TEXT NOT NULL,
    transaction_date TEXT NOT NULL,
    nav_date TEXT,
    transaction_type TEXT NOT NULL CHECK(transaction_type IN ('买入','卖出')),
    target_amount REAL,
    shares REAL,
    unit_nav REAL,
    amount REAL NOT NULL DEFAULT 0,
    note TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_transactions_user_date
ON transactions(user_id, transaction_date DESC, transaction_id DESC);

CREATE TABLE IF NOT EXISTS fund_overview (
    fund_id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    fund_code TEXT NOT NULL,
    fund_name TEXT NOT NULL,
    total_shares REAL DEFAULT 0,
    total_cost REAL DEFAULT 0,
    average_buy_nav REAL DEFAULT 0,
    first_buy_date TEXT,
    last_transaction_date TEXT,
    last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(user_id, fund_code)
);

CREATE INDEX IF NOT EXISTS idx_fund_overview_user
ON fund_overview(user_id, fund_code);

-- NAV history is global (shared across ALL users - same fund has same nav for everyone)
CREATE TABLE IF NOT EXISTS fund_nav_history (
    nav_id INTEGER PRIMARY KEY AUTOINCREMENT,
    fund_code TEXT NOT NULL,
    fund_name TEXT NOT NULL,
    price_date TEXT NOT NULL,
    unit_nav REAL NOT NULL,
    cumulative_nav REAL,
    daily_growth_rate REAL,
    data_source TEXT DEFAULT 'fundSpider',
    fetched_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(fund_code, price_date, data_source)
);

CREATE INDEX IF NOT EXISTS idx_fund_nav_history_code_date
ON fund_nav_history(fund_code, price_date);

-- =========================
-- Triggers keeping overview in sync
-- =========================
DROP TRIGGER IF EXISTS update_fund_overview_after_insert;
CREATE TRIGGER update_fund_overview_after_insert
AFTER INSERT ON transactions
FOR EACH ROW
WHEN NEW.shares IS NOT NULL AND NEW.unit_nav IS NOT NULL AND NEW.amount IS NOT NULL
BEGIN
    INSERT OR IGNORE INTO fund_overview (
        user_id, fund_code, fund_name, total_shares, total_cost, average_buy_nav, first_buy_date
    ) VALUES (NEW.user_id, NEW.fund_code, NEW.fund_name, 0, 0, 0, NEW.transaction_date);

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
        last_transaction_date = NEW.transaction_date,
        last_updated = CURRENT_TIMESTAMP
    WHERE user_id = NEW.user_id AND fund_code = NEW.fund_code;
END;

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
            WHERE user_id = OLD.user_id AND fund_code = OLD.fund_code
        ), 2),
        total_cost = ROUND((
            SELECT COALESCE(SUM(CASE 
                WHEN transaction_type = '买入' THEN amount
                ELSE 0
            END), 0)
            FROM transactions
            WHERE user_id = OLD.user_id AND fund_code = OLD.fund_code
        ), 2),
        average_buy_nav = CASE
            WHEN ROUND((SELECT COALESCE(SUM(CASE 
                WHEN transaction_type = '买入' THEN shares
                WHEN transaction_type = '卖出' THEN -shares
                ELSE 0
            END), 0) FROM transactions WHERE user_id = OLD.user_id AND fund_code = OLD.fund_code), 2) = 0 THEN 0
            ELSE ROUND((SELECT COALESCE(SUM(CASE 
                WHEN transaction_type = '买入' THEN amount
                ELSE 0
            END), 0) FROM transactions WHERE user_id = OLD.user_id AND fund_code = OLD.fund_code) /
            ROUND((SELECT COALESCE(SUM(CASE 
                WHEN transaction_type = '买入' THEN shares
                WHEN transaction_type = '卖出' THEN -shares
                ELSE 0
            END), 0) FROM transactions WHERE user_id = OLD.user_id AND fund_code = OLD.fund_code), 2), 4)
        END,
        last_updated = CURRENT_TIMESTAMP
    WHERE user_id = OLD.user_id AND fund_code = OLD.fund_code;
END;

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
    WHERE user_id = NEW.user_id AND fund_code = NEW.fund_code;
END;

-- =========================
-- Views filtered by user_id
-- =========================
DROP VIEW IF EXISTS fund_realtime_overview;
CREATE VIEW fund_realtime_overview AS
SELECT 
    fo.user_id,
    fo.fund_id,
    fo.fund_code,
    fo.fund_name,
    fo.total_shares,
    fo.total_cost,
    fo.average_buy_nav,
    COALESCE(mp.unit_nav, 0) as current_nav,
    fo.total_shares * COALESCE(mp.unit_nav, 0) as current_value,
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

DROP VIEW IF EXISTS profit_summary;
CREATE VIEW profit_summary AS
SELECT 
    fo.user_id,
    COUNT(*) as total_funds,
    SUM(fo.total_shares) as total_shares,
    SUM(fo.total_cost) as total_cost,
    SUM(fo.total_shares * COALESCE(mp.unit_nav, 0)) as total_value,
    SUM(fo.total_shares * COALESCE(mp.unit_nav, 0) - fo.total_cost) as total_profit,
    CASE 
        WHEN SUM(fo.total_cost) > 0 
        THEN (SUM(fo.total_shares * COALESCE(mp.unit_nav, 0) - fo.total_cost) / SUM(fo.total_cost) * 100)
        ELSE 0 
    END as total_return_rate
FROM fund_overview fo
LEFT JOIN (
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
) mp ON fo.fund_code = mp.fund_code
GROUP BY fo.user_id;

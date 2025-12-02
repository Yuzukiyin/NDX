-- PostgreSQL fund tables with multi-tenant support
-- This script creates fund-related tables, triggers, and views for PostgreSQL.

CREATE TABLE IF NOT EXISTS transactions (
    transaction_id BIGSERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    fund_code TEXT NOT NULL,
    fund_name TEXT NOT NULL,
    transaction_date DATE NOT NULL,
    nav_date DATE,
    transaction_type TEXT NOT NULL CHECK (transaction_type IN ('买入','卖出')),
    target_amount NUMERIC(20,2),
    shares NUMERIC(28,6),
    unit_nav NUMERIC(20,6),
    amount NUMERIC(20,2) NOT NULL DEFAULT 0,
    note TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_transactions_user_date
ON transactions(user_id, transaction_date DESC, transaction_id DESC);

CREATE TABLE IF NOT EXISTS fund_overview (
    fund_id BIGSERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    fund_code TEXT NOT NULL,
    fund_name TEXT NOT NULL,
    total_shares NUMERIC(28,6) DEFAULT 0,
    total_cost NUMERIC(20,2) DEFAULT 0,
    average_buy_nav NUMERIC(20,6) DEFAULT 0,
    first_buy_date DATE,
    last_transaction_date DATE,
    last_updated TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(user_id, fund_code)
);

CREATE INDEX IF NOT EXISTS idx_fund_overview_user
ON fund_overview(user_id, fund_code);

CREATE TABLE IF NOT EXISTS fund_nav_history (
    nav_id BIGSERIAL PRIMARY KEY,
    fund_code TEXT NOT NULL,
    fund_name TEXT NOT NULL,
    price_date DATE NOT NULL,
    unit_nav NUMERIC(20,6) NOT NULL,
    cumulative_nav NUMERIC(20,6),
    daily_growth_rate NUMERIC(6,3),
    data_source TEXT DEFAULT 'fundSpider',
    fetched_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(fund_code, price_date, data_source)
);

CREATE INDEX IF NOT EXISTS idx_fund_nav_history_code_date
ON fund_nav_history(fund_code, price_date);

-- Trigger functions
CREATE OR REPLACE FUNCTION trg_fund_overview_after_insert()
RETURNS TRIGGER AS $$
BEGIN
    INSERT INTO fund_overview (user_id, fund_code, fund_name, total_shares, total_cost, average_buy_nav, first_buy_date)
    VALUES (NEW.user_id, NEW.fund_code, NEW.fund_name, 0, 0, 0, NEW.transaction_date)
    ON CONFLICT (user_id, fund_code) DO NOTHING;

    UPDATE fund_overview
    SET total_shares = ROUND(total_shares + CASE
            WHEN NEW.transaction_type = '买入' THEN COALESCE(NEW.shares, 0)
            WHEN NEW.transaction_type = '卖出' THEN -COALESCE(NEW.shares, 0)
            ELSE 0
        END, 6),
        total_cost = ROUND(total_cost + CASE
            WHEN NEW.transaction_type = '买入' THEN COALESCE(NEW.amount, 0)
            ELSE 0
        END, 2),
        average_buy_nav = CASE
            WHEN ROUND(total_shares + CASE
                    WHEN NEW.transaction_type = '买入' THEN COALESCE(NEW.shares, 0)
                    WHEN NEW.transaction_type = '卖出' THEN -COALESCE(NEW.shares, 0)
                    ELSE 0
                END, 6) = 0 THEN 0
            ELSE ROUND((total_cost + CASE
                    WHEN NEW.transaction_type = '买入' THEN COALESCE(NEW.amount, 0)
                    ELSE 0
                END) /
                NULLIF(ROUND(total_shares + CASE
                    WHEN NEW.transaction_type = '买入' THEN COALESCE(NEW.shares, 0)
                    WHEN NEW.transaction_type = '卖出' THEN -COALESCE(NEW.shares, 0)
                    ELSE 0
                END, 6), 0), 6)
        END,
        last_transaction_date = NEW.transaction_date,
        last_updated = CURRENT_TIMESTAMP
    WHERE user_id = NEW.user_id AND fund_code = NEW.fund_code;

    RETURN NULL;
END;
$$ LANGUAGE plpgsql;

CREATE OR REPLACE FUNCTION trg_fund_overview_after_delete()
RETURNS TRIGGER AS $$
DECLARE
    new_total_shares NUMERIC(28,6);
    new_total_cost NUMERIC(20,2);
BEGIN
    SELECT COALESCE(SUM(CASE
            WHEN transaction_type = '买入' THEN shares
            WHEN transaction_type = '卖出' THEN -shares
            ELSE 0
        END), 0),
        COALESCE(SUM(CASE
            WHEN transaction_type = '买入' THEN amount
            ELSE 0
        END), 0)
    INTO new_total_shares, new_total_cost
    FROM transactions
    WHERE user_id = OLD.user_id AND fund_code = OLD.fund_code;

    UPDATE fund_overview
    SET total_shares = ROUND(new_total_shares, 6),
        total_cost = ROUND(new_total_cost, 2),
        average_buy_nav = CASE
            WHEN ROUND(new_total_shares, 6) = 0 THEN 0
            ELSE ROUND(new_total_cost / NULLIF(ROUND(new_total_shares, 6), 0), 6)
        END,
        last_updated = CURRENT_TIMESTAMP
    WHERE user_id = OLD.user_id AND fund_code = OLD.fund_code;

    RETURN NULL;
END;
$$ LANGUAGE plpgsql;

CREATE OR REPLACE FUNCTION trg_fund_overview_after_fill()
RETURNS TRIGGER AS $$
BEGIN
    UPDATE fund_overview
    SET total_shares = ROUND(total_shares + CASE
            WHEN NEW.transaction_type = '买入' THEN COALESCE(NEW.shares, 0)
            WHEN NEW.transaction_type = '卖出' THEN -COALESCE(NEW.shares, 0)
            ELSE 0
        END, 6),
        total_cost = ROUND(total_cost + CASE
            WHEN NEW.transaction_type = '买入' THEN COALESCE(NEW.amount, 0)
            ELSE 0
        END, 2),
        average_buy_nav = CASE
            WHEN ROUND(total_shares + CASE
                    WHEN NEW.transaction_type = '买入' THEN COALESCE(NEW.shares, 0)
                    WHEN NEW.transaction_type = '卖出' THEN -COALESCE(NEW.shares, 0)
                    ELSE 0
                END, 6) = 0 THEN 0
            ELSE ROUND((total_cost + CASE
                    WHEN NEW.transaction_type = '买入' THEN COALESCE(NEW.amount, 0)
                    ELSE 0
                END) /
                NULLIF(ROUND(total_shares + CASE
                    WHEN NEW.transaction_type = '买入' THEN COALESCE(NEW.shares, 0)
                    WHEN NEW.transaction_type = '卖出' THEN -COALESCE(NEW.shares, 0)
                    ELSE 0
                END, 6), 0), 6)
        END,
        last_updated = CURRENT_TIMESTAMP
    WHERE user_id = NEW.user_id AND fund_code = NEW.fund_code;

    RETURN NULL;
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS trg_update_fund_overview_after_insert ON transactions;
CREATE TRIGGER trg_update_fund_overview_after_insert
AFTER INSERT ON transactions
FOR EACH ROW
WHEN (NEW.shares IS NOT NULL AND NEW.unit_nav IS NOT NULL AND NEW.amount IS NOT NULL)
EXECUTE FUNCTION trg_fund_overview_after_insert();

DROP TRIGGER IF EXISTS trg_update_fund_overview_after_delete ON transactions;
CREATE TRIGGER trg_update_fund_overview_after_delete
AFTER DELETE ON transactions
FOR EACH ROW
WHEN (OLD.shares IS NOT NULL AND OLD.unit_nav IS NOT NULL AND OLD.amount IS NOT NULL)
EXECUTE FUNCTION trg_fund_overview_after_delete();

DROP TRIGGER IF EXISTS trg_update_fund_overview_after_fill ON transactions;
CREATE TRIGGER trg_update_fund_overview_after_fill
AFTER UPDATE ON transactions
FOR EACH ROW
WHEN (OLD.shares IS NULL AND NEW.shares IS NOT NULL)
EXECUTE FUNCTION trg_fund_overview_after_fill();

-- Views
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
    COALESCE(mp.unit_nav, 0) AS current_nav,
    fo.total_shares * COALESCE(mp.unit_nav, 0) AS current_value,
    ROUND((fo.total_shares * COALESCE(mp.unit_nav, 0) - fo.total_cost)::numeric, 2) AS profit,
    CASE 
        WHEN fo.total_cost > 0 THEN ROUND(((fo.total_shares * COALESCE(mp.unit_nav, 0) - fo.total_cost) / fo.total_cost * 100)::numeric, 2)
        ELSE 0
    END AS profit_rate,
    fo.first_buy_date,
    fo.last_transaction_date,
    COALESCE(mp.price_date::text, '') AS last_nav_date,
    COALESCE(mp.daily_growth_rate, 0) AS daily_growth_rate,
    COALESCE(mp.data_source, '') AS data_source,
    fo.last_updated
FROM fund_overview fo
LEFT JOIN (
    SELECT DISTINCT ON (fund_code) 
        fund_code,
        price_date,
        unit_nav,
        daily_growth_rate,
        data_source
    FROM fund_nav_history
    ORDER BY fund_code, price_date DESC, fetched_at DESC
) mp ON fo.fund_code = mp.fund_code;

DROP VIEW IF EXISTS profit_summary;
CREATE VIEW profit_summary AS
SELECT 
    fo.user_id,
    COUNT(*) AS total_funds,
    COALESCE(SUM(fo.total_shares), 0) AS total_shares,
    COALESCE(SUM(fo.total_cost), 0) AS total_cost,
    COALESCE(SUM(fo.total_shares * COALESCE(mp.unit_nav, 0)), 0) AS total_value,
    COALESCE(SUM(fo.total_shares * COALESCE(mp.unit_nav, 0) - fo.total_cost), 0) AS total_profit,
    CASE 
        WHEN COALESCE(SUM(fo.total_cost), 0) > 0 
        THEN (COALESCE(SUM(fo.total_shares * COALESCE(mp.unit_nav, 0) - fo.total_cost), 0) / SUM(fo.total_cost) * 100)
        ELSE 0 
    END AS total_return_rate
FROM fund_overview fo
LEFT JOIN (
    SELECT DISTINCT ON (fund_code) 
        fund_code,
        unit_nav
    FROM fund_nav_history
    ORDER BY fund_code, price_date DESC, fetched_at DESC
) mp ON fo.fund_code = mp.fund_code
GROUP BY fo.user_id;

-- Add auto_invest_plans table to fund_multitenant.sql

CREATE TABLE IF NOT EXISTS auto_invest_plans (
    plan_id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    plan_name TEXT NOT NULL,
    fund_code TEXT NOT NULL,
    fund_name TEXT NOT NULL,
    amount REAL NOT NULL CHECK(amount > 0),
    frequency TEXT NOT NULL CHECK(frequency IN ('daily','weekly','monthly')),
    start_date TEXT NOT NULL,
    end_date TEXT NOT NULL,
    enabled INTEGER NOT NULL DEFAULT 1,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(user_id, plan_name)
);

CREATE INDEX IF NOT EXISTS idx_auto_invest_user
ON auto_invest_plans(user_id, enabled);

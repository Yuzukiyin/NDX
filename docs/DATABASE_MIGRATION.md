# 数据库迁移指南

## 从SQLite迁移到PostgreSQL

### 场景说明
如果你之前使用本地SQLite数据库（`fund.db`），现在要迁移到PostgreSQL（Railway），按以下步骤操作。

### 准备工作

1. **备份当前数据**
```bash
# 备份SQLite数据库
cp fund.db fund.db.backup
cp ndx_users.db ndx_users.db.backup
```

2. **导出数据为SQL**
```bash
sqlite3 fund.db .dump > fund_backup.sql
sqlite3 ndx_users.db .dump > users_backup.sql
```

### 方法1: 使用迁移脚本（推荐）

脚本位于 `Web/backend/scripts/migrate_sqlite_to_postgres.py`

```bash
cd Web/backend

# 设置环境变量
export SOURCE_DB="sqlite:///../../fund.db"
export TARGET_DB="postgresql://user:pass@host:port/dbname"

# 执行迁移
python scripts/migrate_sqlite_to_postgres.py
```

脚本功能：
- ✅ 自动迁移所有表数据
- ✅ 处理数据类型差异
- ✅ 保留时间戳
- ✅ 验证数据完整性

### 方法2: 手动迁移

#### Step 1: 导出CSV数据

```bash
# 导出基金净值历史
sqlite3 fund.db -header -csv "SELECT * FROM fund_nav_history;" > nav_history.csv

# 导出交易记录
sqlite3 fund.db -header -csv "SELECT * FROM transactions;" > transactions.csv

# 导出定投计划
sqlite3 ndx_users.db -header -csv "SELECT * FROM auto_invest_plans;" > plans.csv

# 导出用户数据
sqlite3 ndx_users.db -header -csv "SELECT * FROM users;" > users.csv
```

#### Step 2: 导入到PostgreSQL

```bash
# 连接到PostgreSQL
psql $DATABASE_URL

# 导入数据
\copy fund_nav_history FROM 'nav_history.csv' CSV HEADER;
\copy transactions FROM 'transactions.csv' CSV HEADER;
\copy auto_invest_plans FROM 'plans.csv' CSV HEADER;
\copy users FROM 'users.csv' CSV HEADER;
```

### 方法3: 使用pgloader（大数据量）

安装pgloader：
```bash
# macOS
brew install pgloader

# Ubuntu
sudo apt-get install pgloader

# Windows (WSL)
wsl sudo apt-get install pgloader
```

创建配置文件 `migration.load`：
```lisp
LOAD DATABASE
  FROM sqlite://fund.db
  INTO postgresql://user:pass@host:port/dbname

WITH include drop, create tables, create indexes, reset sequences

SET work_mem to '256MB', maintenance_work_mem to '512 MB';
```

执行迁移：
```bash
pgloader migration.load
```

## 验证迁移

### 1. 检查表结构
```sql
-- PostgreSQL
\dt
\d+ fund_nav_history
\d+ transactions
\d+ auto_invest_plans
\d+ users
```

### 2. 验证数据量
```sql
-- SQLite
SELECT COUNT(*) FROM fund_nav_history;
SELECT COUNT(*) FROM transactions;

-- PostgreSQL (应该相同)
SELECT COUNT(*) FROM fund_nav_history;
SELECT COUNT(*) FROM transactions;
```

### 3. 验证数据样本
```sql
-- 检查最新记录
SELECT * FROM fund_nav_history ORDER BY fetched_at DESC LIMIT 5;
SELECT * FROM transactions ORDER BY transaction_date DESC LIMIT 5;
```

### 4. 运行迁移验证脚本
```bash
cd Web/backend
python scripts/verify_migration.py
```

## 常见问题

### 1. 字符编码问题
```bash
# 导出时指定UTF-8
sqlite3 fund.db
.mode csv
.headers on
.output data.csv
SELECT * FROM table_name;
.quit

# 导入时指定编码
COPY table_name FROM '/path/to/data.csv' CSV HEADER ENCODING 'UTF8';
```

### 2. 时间戳格式差异
```sql
-- SQLite: YYYY-MM-DD HH:MM:SS
-- PostgreSQL: timestamp with time zone

-- 转换
UPDATE transactions SET 
  transaction_date = transaction_date::timestamp AT TIME ZONE 'Asia/Shanghai';
```

### 3. 自增ID重置
```sql
-- PostgreSQL重置序列
SELECT setval('users_id_seq', (SELECT MAX(id) FROM users));
SELECT setval('auto_invest_plans_id_seq', (SELECT MAX(id) FROM auto_invest_plans));
```

### 4. 唯一约束冲突
```sql
-- 检查重复数据
SELECT fund_code, price_date, COUNT(*) 
FROM fund_nav_history 
GROUP BY fund_code, price_date 
HAVING COUNT(*) > 1;

-- 删除重复（保留最新）
DELETE FROM fund_nav_history a USING fund_nav_history b
WHERE a.nav_id < b.nav_id 
AND a.fund_code = b.fund_code 
AND a.price_date = b.price_date;
```

## 迁移后优化

### 1. 创建索引
```sql
-- 加速查询
CREATE INDEX idx_nav_fund_date ON fund_nav_history(fund_code, price_date);
CREATE INDEX idx_trans_fund_date ON transactions(fund_code, transaction_date);
CREATE INDEX idx_trans_user ON transactions(user_id);
CREATE INDEX idx_plans_user ON auto_invest_plans(user_id);
```

### 2. 更新统计信息
```sql
ANALYZE fund_nav_history;
ANALYZE transactions;
ANALYZE auto_invest_plans;
ANALYZE users;
```

### 3. 清理数据
```sql
-- 删除测试数据
DELETE FROM transactions WHERE note LIKE '%test%';

-- 删除旧的无效记录
DELETE FROM fund_nav_history WHERE price_date < '2020-01-01';
```

## 回滚计划

如果迁移出现问题：

### 1. 保留SQLite备份
```bash
# 不要删除原始的 .db 文件
ls -lh *.db.backup
```

### 2. 清空PostgreSQL表
```sql
TRUNCATE TABLE fund_nav_history CASCADE;
TRUNCATE TABLE transactions CASCADE;
TRUNCATE TABLE auto_invest_plans CASCADE;
TRUNCATE TABLE users CASCADE;
```

### 3. 恢复SQLite数据
```bash
# 从备份恢复
cp fund.db.backup fund.db
cp ndx_users.db.backup ndx_users.db

# 重新启动本地服务
python start.py
```

## 生产环境最佳实践

### 1. 分阶段迁移
- Day 1: 迁移用户数据
- Day 2: 迁移基金数据
- Day 3: 迁移交易数据
- Day 4: 验证并切换

### 2. 双写策略
```python
# 同时写入SQLite和PostgreSQL
async def save_transaction(data):
    # 写入PostgreSQL（主）
    await pg_db.execute(...)
    
    # 写入SQLite（备份）
    sqlite_db.execute(...)
```

### 3. 流量切换
```python
# 使用feature flag控制
if config.USE_POSTGRESQL:
    db = postgresql_db
else:
    db = sqlite_db
```

### 4. 监控迁移进度
```python
import logging

logger.info(f"Migrating table: {table_name}")
logger.info(f"Total rows: {total_rows}")
logger.info(f"Progress: {current_row}/{total_rows}")
```

## 性能对比

| 操作 | SQLite | PostgreSQL |
|------|--------|------------|
| 查询1000条净值 | ~50ms | ~20ms |
| 插入100条交易 | ~100ms | ~30ms |
| 复杂JOIN查询 | ~200ms | ~50ms |
| 并发写入 | 单线程 | 多连接 |
| 数据库大小 | ~100MB | ~80MB |

## 后续维护

### 定期备份
```bash
# 每日自动备份
pg_dump $DATABASE_URL > backup_$(date +%Y%m%d).sql

# 保留30天
find backups/ -name "*.sql" -mtime +30 -delete
```

### 监控查询性能
```sql
-- 查看慢查询
SELECT query, calls, total_time, mean_time
FROM pg_stat_statements
ORDER BY mean_time DESC
LIMIT 10;
```

### 数据库维护
```sql
-- 定期VACUUM
VACUUM ANALYZE;

-- 重建索引
REINDEX DATABASE ndx;
```

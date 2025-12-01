# NDX 历史净值功能修复说明

## 修复的问题

### 1. 数据库表结构问题
**问题描述**：`fund_nav_history` 表缺少 `user_id` 字段，导致多租户支持不完整。

**影响**：
- 历史净值数据无法正确插入（SQL 错误）
- 不同用户之间的净值数据会混淆
- 查询历史净值时可能返回其他用户的数据

**修复内容**：
- 更新 `Web/backend/app/db/fund_multitenant.sql`，为 `fund_nav_history` 表添加 `user_id` 字段
- 更新相关视图 `fund_realtime_overview` 和 `profit_summary`，支持按 `user_id` 过滤
- 更新索引以提升查询性能

### 2. 模块导入路径问题
**问题描述**：`fund_service.py` 中导入 `fetch_history_nav` 和 `update_pending_transactions` 时路径不正确。

**影响**：
- Railway 部署时无法找到模块
- 历史净值抓取功能失败
- 待确认交易更新功能失败

**修复内容**：
- 在 `fetch_history_nav()` 和 `update_pending_transactions()` 方法中添加动态路径
- 确保模块可以从 `Web/backend` 目录正确导入

### 3. 查询过滤缺失
**问题描述**：`get_nav_history()` 方法未按 `user_id` 过滤数据。

**影响**：
- 可能查询到其他用户的历史净值数据
- 数据安全问题

**修复内容**：
- 在 SQL 查询中添加 `user_id` 过滤条件

### 4. 批量添加净值记录问题
**问题描述**：`add_nav_history_batch()` 方法未包含 `user_id` 字段。

**影响**：
- 批量导入净值数据时会失败
- 数据无法正确关联到用户

**修复内容**：
- 在插入和查询时添加 `user_id` 字段处理

## Railway 部署步骤

### 1. 数据库迁移

**重要**：在 Railway 上执行迁移脚本，为现有数据添加 `user_id` 字段。

```bash
# 进入 Railway 项目控制台，或使用 Railway CLI
cd Web/backend
python scripts/migrate_add_user_id_to_nav_history.py
```

这个脚本会：
- 检查 `fund_nav_history` 表是否存在
- 如果没有 `user_id` 字段，则创建新表结构
- 将现有数据迁移到新表，默认分配给 `user_id=1`
- 创建必要的索引

### 2. 更新数据库 Schema

确保 Railway 数据库应用了最新的 schema：

```bash
# 在 Railway 控制台中运行
sqlite3 ndx_users.db < app/db/fund_multitenant.sql
```

### 3. 重新部署后端

```bash
# 提交代码更改
git add .
git commit -m "fix: 修复历史净值功能的多租户支持"
git push

# Railway 会自动重新部署
```

### 4. 验证修复

部署完成后，登录系统测试：

1. 进入「工具」页面
2. 点击「抓取历史净值」
3. 检查是否成功（不再显示 `no such column: user_id` 错误）
4. 进入「基金」页面，查看净值数据是否正确显示

## 文件修改清单

### 修改的文件

1. `Web/backend/app/db/fund_multitenant.sql`
   - 为 `fund_nav_history` 表添加 `user_id` 字段
   - 更新唯一约束和索引
   - 更新视图定义以支持多租户

2. `Web/backend/app/services/fund_service.py`
   - 修复 `fetch_history_nav()` 的导入路径
   - 修复 `update_pending_transactions()` 的导入路径
   - 在 `get_nav_history()` 中添加 `user_id` 过滤
   - 在 `add_nav_history_batch()` 中添加 `user_id` 处理

### 新增的文件

1. `Web/backend/scripts/migrate_add_user_id_to_nav_history.py`
   - 数据库迁移脚本
   - 为现有数据添加 `user_id` 字段

2. `Web/backend/BUGFIX.md`
   - 本说明文档

## 技术细节

### fund_nav_history 表结构（更新后）

```sql
CREATE TABLE fund_nav_history (
    nav_id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL DEFAULT 1,       -- 新增字段
    fund_code TEXT NOT NULL,
    fund_name TEXT NOT NULL,
    price_date TEXT NOT NULL,
    unit_nav REAL NOT NULL,
    cumulative_nav REAL,
    daily_growth_rate REAL,
    data_source TEXT DEFAULT 'fundSpider',
    fetched_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(user_id, fund_code, price_date, data_source)  -- 更新唯一约束
);
```

### 关键代码片段

**修复前**（错误）：
```python
# fund_service.py
query = "SELECT price_date, unit_nav FROM fund_nav_history WHERE fund_code = ?"
params = [fund_code]
```

**修复后**（正确）：
```python
# fund_service.py
query = "SELECT price_date, unit_nav FROM fund_nav_history WHERE user_id = ? AND fund_code = ?"
params = [self.user_id, fund_code]
```

## 注意事项

1. **迁移脚本只需执行一次**：如果表已有 `user_id` 字段，脚本会自动跳过。

2. **现有数据归属**：迁移脚本会将所有现有净值数据分配给 `user_id=1`（默认管理员用户）。

3. **Railway 环境变量**：确保 Railway 上设置了正确的 `DATABASE_URL` 环境变量。

4. **备份建议**：在执行迁移前，建议备份 Railway 数据库。

## 未来改进建议

1. **全局净值共享**：考虑是否需要将净值数据改为全局共享（所有用户共用同一份净值数据），以节省存储空间。

2. **定时任务**：添加定时任务自动抓取最新净值，而不是手动触发。

3. **错误日志**：完善错误日志记录，便于排查问题。

4. **性能优化**：对于大量历史数据，考虑分页或懒加载。

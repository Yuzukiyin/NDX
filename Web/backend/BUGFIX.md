# NDX 历史净值功能修复说明

## 修复的问题

### 1. 数据库表结构问题 ✅ 已修正设计
**原设计缺陷**：`fund_nav_history` 表本应作为全局共享数据，但代码中却使用了 `user_id` 字段。

**正确的设计理念**：
- **历史净值数据是全局通用的**：同一基金在同一日期的净值对所有用户都相同
- **不应该为每个用户单独存储净值数据**：这会造成巨大的数据冗余
- **节省存储空间**：多个用户持有同一基金时，共享同一份净值数据

**修复内容**：
- 确保 `fund_nav_history` 表**不包含** `user_id` 字段（全局共享）
- 更新相关视图 `fund_realtime_overview` 和 `profit_summary`，使用全局净值数据
- 修复所有查询和插入操作，移除不必要的 `user_id` 过滤

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

### 1. 代码已自动推送

GitHub 更新后，Railway 会自动检测并重新部署。

### 2. 数据库 Schema 检查（可选）

如果 Railway 数据库的 `fund_nav_history` 表已存在且包含 `user_id` 字段，需要删除并重建：

```bash
# 在 Railway Shell 中执行
cd Web/backend
sqlite3 ndx_users.db "DROP TABLE IF EXISTS fund_nav_history;"
sqlite3 ndx_users.db < app/db/fund_multitenant.sql
```

**注意**：这会清空历史净值数据，但不影响用户交易记录。用户可以重新抓取净值。

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

### fund_nav_history 表结构（正确设计）

```sql
CREATE TABLE fund_nav_history (
    nav_id INTEGER PRIMARY KEY AUTOINCREMENT,
    fund_code TEXT NOT NULL,              -- 无 user_id，全局共享
    fund_name TEXT NOT NULL,
    price_date TEXT NOT NULL,
    unit_nav REAL NOT NULL,
    cumulative_nav REAL,
    daily_growth_rate REAL,
    data_source TEXT DEFAULT 'fundSpider',
    fetched_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(fund_code, price_date, data_source)  -- 唯一约束不包含 user_id
);
```

### 数据隔离设计

**需要按用户隔离的表**：
- `transactions` - 每个用户的交易记录
- `fund_overview` - 每个用户的持仓统计

**全局共享的表**：
- `fund_nav_history` - 所有用户共享同一份净值数据

### 关键代码片段

**查询历史净值**（全局共享，无需 user_id）：
```python
# fund_service.py - get_nav_history()
query = "SELECT price_date, unit_nav FROM fund_nav_history WHERE fund_code = ?"
params = [fund_code]
```

**插入历史净值**（全局共享，无需 user_id）：
```python
# fetch_history_nav.py - save_nav_history()
INSERT INTO fund_nav_history (
    fund_code, fund_name, price_date, unit_nav, ...
) VALUES (?, ?, ?, ?, ...)
```

## 注意事项

1. **净值数据是全局共享的**：所有用户查询同一基金的净值数据都来自同一个表。

2. **数据隔离边界清晰**：
   - 用户隔离：`transactions`、`fund_overview`
   - 全局共享：`fund_nav_history`

3. **Railway 环境变量**：确保 Railway 上设置了正确的 `DATABASE_URL` 环境变量。

4. **重建表注意**：如果需要删除旧的 `fund_nav_history` 表，用户需要重新抓取净值数据。

## 设计优势

1. **节省存储空间**：多个用户持有同一基金时，不会重复存储净值数据。

2. **数据一致性**：所有用户看到的同一基金的净值数据完全一致。

3. **维护简单**：只需抓取一次净值数据，所有用户即可使用。

4. **性能优化**：减少数据冗余，提升查询效率。

## 未来改进建议

1. **定时任务**：添加定时任务自动抓取最新净值，而不是手动触发。

2. **错误日志**：完善错误日志记录，便于排查问题。

3. **性能优化**：对于大量历史数据，考虑分页或懒加载。

4. **缓存机制**：为常用的净值查询添加缓存层。

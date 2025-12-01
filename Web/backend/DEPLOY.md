# Railway 部署快速指南

## 问题修复完成 ✅

已修复历史净值无法获取的问题，主要包括：
1. 采用正确的**全局共享**设计（移除不必要的 `user_id` 字段）
2. 模块导入路径错误
3. 数据隔离边界不清晰

## 立即部署步骤

### 方式一：自动部署（推荐）

Railway 会自动检测到 GitHub 仓库的更新并重新部署。

1. **等待自动部署完成**（约 2-5 分钟）
2. **执行数据库迁移**（仅需一次）

### 方式二：手动触发部署

如果需要手动触发：

1. 登录 [Railway Dashboard](https://railway.app/)
2. 进入 NDX 项目
3. 点击后端服务
4. 点击 "Deploy" 按钮

## 数据库处理（仅在需要时）

如果 Railway 上的 `fund_nav_history` 表已包含 `user_id` 字段，需要删除并重建：

### 使用 Railway Web Console

1. 进入 Railway Dashboard
2. 选择 NDX 后端服务
3. 点击 "Deploy" 旁的 "..." → "Shell"
4. 在 Shell 中执行：

```bash
cd Web/backend

# 删除旧表（包含 user_id 的错误设计）
sqlite3 ndx_users.db "DROP TABLE IF EXISTS fund_nav_history;"

# 应用正确的 schema
sqlite3 ndx_users.db < app/db/fund_multitenant.sql
```

**注意**：这会清空历史净值数据，但不影响用户交易记录。用户可以重新抓取净值。

### 如果是全新部署

如果是首次部署或表结构已正确，则**无需任何操作**，直接验证即可。

## 验证修复

### 1. 检查部署状态

- Railway Dashboard 显示 "Active"
- 查看 Logs 没有错误

### 2. 测试历史净值功能

1. 登录系统：https://ndx-git-main-yuzukiyins-projects.vercel.app/
2. 进入「工具」页面
3. 点击「抓取历史净值」
4. 应该显示 "✅ 历史净值抓取完成!"

### 3. 检查数据

1. 进入「基金」页面
2. 查看是否显示了最新净值和日增长率
3. 点击基金卡片查看历史数据

## 常见问题

### Q1: 仍然显示 "no such column: user_id" 错误

**原因**：旧代码中使用了 `user_id` 字段，但新设计中已移除。

**解决方案**：
- 确认已部署最新代码
- 检查代码中是否还有残留的 `user_id` 引用
- 重新部署后端服务

### Q2: 显示 "table fund_nav_history has X columns but Y values were supplied"

**原因**：旧表结构包含 `user_id` 字段，新代码不再使用。

**解决方案**：
- 删除旧表并重建（见上方"数据库处理"部分）
- 或等待系统自动创建新表（如果表不存在）

### Q3: 模块导入失败

**解决方案**：
- 确认所有文件都已正确提交到 GitHub
- 检查 `requirements.txt` 是否包含所有依赖
- 查看 Railway 部署日志

## 环境变量检查

确保 Railway 上设置了以下环境变量：

```bash
DATABASE_URL=sqlite+aiosqlite:///./ndx_users.db
SECRET_KEY=your-secret-key
ADMIN_EMAIL=your-admin-email
ADMIN_PASSWORD=your-admin-password
```

## 回滚方案

如果遇到严重问题需要回滚：

```bash
# 使用 Railway CLI
railway rollback

# 或在 Railway Dashboard 中
# Deployments → 选择上一个成功的部署 → Redeploy
```

## 联系支持

如有问题，请检查：
1. `Web/backend/BUGFIX.md` - 详细的修复说明
2. Railway Logs - 查看运行时错误
3. GitHub Issues - 提交问题报告

---

**最后更新**：2025年12月1日

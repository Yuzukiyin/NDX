# Railway 数据持久化完整指南

## 问题说明

Railway 的**免费容器没有持久化存储**。SQLite 数据库在重启后会丢失。

## ✅ 推荐方案：使用 PostgreSQL（完全免费且持久化）

Railway 提供**免费的 PostgreSQL 数据库**，这是最佳的持久化解决方案。

### 步骤 1：在 Railway 添加 PostgreSQL

1. 进入 Railway Dashboard
2. 点击你的项目（NDX）
3. 点击 **"+ New"** 按钮
4. 选择 **"Database" → "Add PostgreSQL"**
5. Railway 会自动创建数据库并设置环境变量 `DATABASE_URL`

### 步骤 2：修改依赖

在 `requirements.txt` 添加 PostgreSQL 驱动：

```txt
asyncpg
psycopg2-binary
```

### 步骤 3：验证环境变量

PostgreSQL 添加后，Railway 会自动在你的后端服务中注入 `DATABASE_URL`，格式为：
```
postgresql://user:password@host:port/database
```

**无需任何额外配置！** `config.py` 已经支持通过环境变量 `DATABASE_URL` 覆盖默认的 SQLite。

### 步骤 4：重新部署

添加 PostgreSQL 后，Railway 会自动触发重新部署。

### 步骤 5：初始化管理员

PostgreSQL 是全新的数据库，需要重新创建管理员。在 Railway 的环境变量中设置：

```
ADMIN_EMAIL=your-email@example.com
ADMIN_PASSWORD=your-secure-password
ADMIN_USERNAME=admin
```

应用会在启动时自动创建管理员账号。

## ⚠️ 备选方案：接受 SQLite 数据丢失（简单但有风险）

如果你不想用 PostgreSQL，可以接受以下限制：
- ✅ 配置文件 `auto_invest_setting.json` 会从 Git 仓库读取（不会丢失）
- ❌ 用户数据、交易记录在重启后丢失
- ❌ 抓取的历史净值在重启后丢失

只需确保 `auto_invest_setting.json` 已提交到 Git 仓库即可。

## 📊 方案对比

| 特性 | PostgreSQL | SQLite (当前) |
|------|-----------|---------------|
| 数据持久化 | ✅ 完全持久化 | ❌ 重启丢失 |
| 性能 | ✅ 更好 | ⚠️ 一般 |
| 并发支持 | ✅ 优秀 | ❌ 有限 |
| 配置复杂度 | ✅ 自动配置 | ✅ 简单 |
| Railway 成本 | 🆓 免费 | 🆓 免费 |
| 推荐度 | ⭐⭐⭐⭐⭐ | ⭐⭐ |

## 🚀 推荐操作流程

1. **立即添加 PostgreSQL**（在 Railway Dashboard）
2. **添加 asyncpg 依赖**到 `requirements.txt`
3. **设置管理员环境变量**
4. **等待自动部署完成**
5. **重新导入交易数据**（从 CSV）

完成后你的系统将拥有**完全持久化的数据存储**！🎉

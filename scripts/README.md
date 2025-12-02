# NDX 维护脚本

此目录包含用于数据库管理和维护的实用脚本。

## 脚本说明

### 🗄️ 数据库管理
- **`db_manager.py`** - 统一的数据库管理工具
  - 初始化数据库结构
  - 创建管理员账户
  - 显示数据库统计
  - 备份/重置数据库

### 📊 数据同步
- **`sync_nav_data.py`** - 定期同步净值数据
  - 适合设置为定时任务(cron/scheduled task)
  - 自动抓取最新净值
  - 更新待确认交易

### 🔧 本地开发
- **`local_manager.py`** - 本地开发辅助工具
  - 手动抓取净值历史
  - 导入CSV交易记录
  - 更新待确认交易
  - 检查交易日

### 🔄 数据迁移
- **`migrate_sqlite_to_postgres.py`** - SQLite到PostgreSQL迁移工具
  - 一次性迁移历史数据
  - 仅在首次部署时使用

### 🧹 清理工具
- **`cleanup_redundant_files.py`** - 清理冗余文件
  - 删除过时的脚本和数据库文件
  - 已执行完成,可以删除此脚本

## 使用说明

### 环境变量
所有脚本都需要设置 `DATABASE_URL` 环境变量:

```bash
# Windows PowerShell
$env:DATABASE_URL="postgresql://user:password@host:port/database"

# Linux/Mac
export DATABASE_URL="postgresql://user:password@host:port/database"
```

### 运行示例

```bash
# 数据库管理
python scripts/db_manager.py

# 同步净值数据(定时任务)
python scripts/sync_nav_data.py

# 本地开发工具
python scripts/local_manager.py
```

## 注意事项

⚠️ **生产环境**: 
- 大部分功能已集成到Web应用中
- 定投计划和交易记录请通过前端UI管理
- 这些脚本主要用于维护和特殊情况

✅ **推荐使用Web界面**:
- 添加交易: 前端"交易"页面
- 管理定投: 前端"定投管理"页面
- 查看数据: 前端"工作台"页面

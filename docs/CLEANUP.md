# 项目清理指南

本文档说明如何清理重构后的冗余文件。

## 为什么需要清理？

重构后，根目录的许多文件已被Web应用或scripts目录的工具取代，这些文件：
- 占用磁盘空间
- 可能造成混淆
- 不利于项目维护

## 清理前准备

### 1. 确保代码已提交到Git
```bash
cd d:\AAAStudy\NDX
git status
git add .
git commit -m "refactor: 项目重构完成"
git push origin main
```

### 2. 备份重要数据（可选）
```bash
# 备份数据库
mkdir backup_$(date +%Y%m%d)
copy fund.db backup_*
copy ndx_users.db backup_*

# 备份CSV
copy transactions*.csv backup_*
```

## 执行清理

### 方法1: 使用清理脚本（推荐）

```bash
# 激活环境
conda activate NDX

# 运行清理脚本
python scripts\cleanup_redundant_files.py
```

脚本会：
1. 列出所有将要删除的文件
2. 显示文件大小
3. 要求确认（输入`yes`）
4. 删除文件
5. 提示后续操作

### 方法2: 手动删除

如果你想手动控制，按以下顺序删除：

#### 第一批：旧的管理脚本（已被取代）
```bash
del AAAfund_manager.py
del check_db.py
del check_fund_db.py
del export_fund_data.py
del nav_plot.py
del upload_to_railway.py
```

#### 第二批：重复的核心模块
```bash
del fetch_history_nav.py
del import_transactions.py
del import_auto_invest.py
del init_database.py
del tradeDate.py
del update_pending_transactions.py
```

#### 第三批：导出和临时文件
```bash
del bought.sql
del nav_history_export.json
del transactions_export.json
del transactions_new.csv
del transactions_old.csv
```

#### 第四批：本地数据库（可选）
```bash
# 注意：删除前确保数据已迁移到PostgreSQL
del fund.db
del ndx_users.db
```

#### 第五批：旧的依赖文件
```bash
del requirements.txt
```

## 清理后验证

### 1. 检查项目结构
```bash
dir
```

应该看到：
```
Web/
scripts/
docs/
README.md
.env.example
.gitignore
REFACTORING.md
transactions.csv (模板)
auto_invest_setting.json
```

### 2. 测试核心功能

#### 后端测试
```bash
cd Web\backend
python start.py
```
访问 http://localhost:8000/docs 确认API正常

#### 前端测试
```bash
cd Web\frontend
npm run dev
```
访问 http://localhost:5173 确认界面正常

#### 脚本测试
```bash
cd scripts
python local_manager.py
```
测试各项功能

### 3. 提交清理结果
```bash
git status
git add .
git commit -m "chore: 清理冗余文件"
git push origin main
```

## 释放的空间

预计清理后可释放：
- Python脚本: ~100KB
- 数据库文件: ~1MB (如删除.db文件)
- 导出文件: ~1MB
- 总计: ~2MB+

## 恢复文件（如果需要）

如果删除后需要恢复：

### 从Git恢复
```bash
# 查看删除的文件
git log --diff-filter=D --summary

# 恢复特定文件
git checkout HEAD~1 -- AAAfund_manager.py

# 恢复所有删除的文件
git checkout HEAD~1 .
```

### 从备份恢复
```bash
# 恢复数据库
copy backup_20241202\fund.db .
copy backup_20241202\ndx_users.db .
```

## 注意事项

### 不要删除的文件
- ✅ `Web/` 目录（核心应用）
- ✅ `scripts/` 目录（维护工具）
- ✅ `docs/` 目录（文档）
- ✅ `README.md`
- ✅ `.env.example`
- ✅ `.gitignore`
- ✅ `transactions.csv`（作为模板）
- ✅ `auto_invest_setting.json`（配置文件）

### 可选删除
- ⚠️ `fund.db` - 仅在数据已迁移到PostgreSQL后删除
- ⚠️ `ndx_users.db` - 同上
- ⚠️ 导出的JSON/CSV - 可重新生成

### 特殊情况

#### 如果还在使用SQLite
暂时保留：
- `fund.db`
- `ndx_users.db`

等迁移到PostgreSQL后再删除

#### 如果需要参考旧脚本
可以暂时保留在单独的目录：
```bash
mkdir archive
move AAAfund_manager.py archive\
move check_db.py archive\
# ...
```

## 清理后的项目结构

```
NDX/
├── Web/
│   ├── backend/          # ✅ FastAPI后端
│   └── frontend/         # ✅ React前端
├── scripts/              # ✅ 维护工具
├── docs/                 # ✅ 完整文档
├── README.md             # ✅ 项目说明
├── .env.example          # ✅ 环境变量模板
├── .gitignore            # ✅ Git配置
├── REFACTORING.md        # ✅ 重构说明
├── transactions.csv      # ✅ CSV模板
└── auto_invest_setting.json  # ✅ 定投配置
```

清爽、简洁、易维护！

## 常见问题

### Q: 删除后导入交易功能失败？
A: 检查是否误删了`Web/backend/import_transactions.py`，应该保留的是这个文件，删除的是根目录的同名文件。

### Q: 脚本找不到模块？
A: 确保在正确的目录执行：
```bash
# 错误：在根目录执行后端脚本
python fetch_history_nav.py  # ❌

# 正确：使用scripts目录的工具
python scripts\local_manager.py  # ✅
```

### Q: 如何确认删除是否安全？
A: 参考`.gitignore`文件，所有被忽略的文件都可以安全删除。

### Q: 清理后项目还能正常工作吗？
A: 是的！所有功能都已迁移到：
- Web应用（主要功能）
- scripts目录（维护工具）
- 删除的只是冗余文件

## 下一步

清理完成后，建议：
1. ✅ 阅读 [快速开始指南](docs/QUICKSTART.md)
2. ✅ 配置生产环境（参考 [部署指南](docs/DEPLOYMENT.md)）
3. ✅ 设置定时任务同步净值数据
4. ✅ 开始使用系统管理基金！

---

享受整洁的项目结构带来的便利吧！🎉

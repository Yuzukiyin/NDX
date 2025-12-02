# PostgreSQL 数据迁移完整步骤

## 前提条件
确保已安装 psycopg2：
```powershell
conda activate NDX
conda install -c conda-forge psycopg2
# 或者
pip install psycopg2-binary
```

## 步骤 1：清空 PostgreSQL 现有数据
```powershell
cd d:\AAAStudy\NDX\Web\backend
$env:DATABASE_URL="postgresql://postgres:pFmrwDwvBlpdMRCMZkpSNhzYCylgxIGi@metro.proxy.rlwy.net:51615/railway"
python scripts/clean_postgres_fund_data.py
# 输入 yes 确认
```

## 步骤 2：迁移 fund.db 数据到 PostgreSQL
```powershell
# 继续使用上面设置的 DATABASE_URL
python scripts/migrate_sqlite_to_postgres.py --sqlite-path ../../fund.db --user-id 1
```

## 步骤 3：验证迁移结果
脚本会自动显示：
- 交易记录数量
- 历史净值数量
- 基金持仓列表

## 常见问题

### 1. 如果连接超时
Railway 的公网连接可能较慢，建议：
- 耐心等待（可能需要几分钟）
- 或者使用 Railway CLI 在云端执行

### 2. 如果提示缺少 psycopg2
```powershell
pip install psycopg2-binary
```

### 3. 如果想重新迁移
重新执行步骤 1 清空数据，再执行步骤 2

## 一键执行脚本（复制粘贴到 PowerShell）
```powershell
# 设置环境变量
$env:DATABASE_URL="postgresql://postgres:pFmrwDwvBlpdMRCMZkpSNhzYCylgxIGi@metro.proxy.rlwy.net:51615/railway"

# 进入目录
cd d:\AAAStudy\NDX\Web\backend

# 执行清空（需要手动输入 yes）
python scripts/clean_postgres_fund_data.py

# 执行迁移
python scripts/migrate_sqlite_to_postgres.py --sqlite-path ../../fund.db --user-id 1
```

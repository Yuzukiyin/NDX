# 迁移到 Railway PostgreSQL（备选方案）

如果 Railway Volume 功能不可用，可以使用 PostgreSQL 实现持久化。

## 步骤

### 1. 在 Railway 添加 PostgreSQL 服务

1. Railway Dashboard → New → Database → PostgreSQL
2. Railway 会自动设置 `DATABASE_URL` 环境变量

### 2. 修改依赖

```powershell
# 添加 PostgreSQL 驱动
cd d:\AAAStudy\NDX\Web\backend
echo asyncpg >> requirements.txt
echo psycopg2-binary >> requirements.txt
```

### 3. 修改 config.py

```python
# 支持 PostgreSQL 和 SQLite
DATABASE_URL: str = Field(
    default="sqlite+aiosqlite:////app/data/ndx_users.db",
    env="DATABASE_URL"
)

# Railway PostgreSQL 会自动注入 DATABASE_URL，格式：
# postgresql://user:pass@host:port/dbname
# 需要改为异步格式：postgresql+asyncpg://...
```

### 4. 数据迁移

但这个方案**比较复杂**，优先建议使用 Volume！

# 开发环境部署指南

## 本地开发环境设置

### 1. 环境准备

#### 必需软件
- Python 3.10+
- Node.js 18+
- PostgreSQL 14+ (本地开发) 或 Railway账号 (云部署)
- Git

#### 创建Conda环境
```bash
conda create -n NDX python=3.10
conda activate NDX
```

### 2. 后端设置

#### 安装依赖
```bash
cd Web/backend
pip install -r requirements.txt
```

#### 配置环境变量

创建 `Web/backend/.env` 文件：
```bash
# 本地开发使用PostgreSQL
DATABASE_URL=postgresql+asyncpg://postgres:password@localhost:5432/ndx

# 或使用SQLite（仅测试）
# DATABASE_URL=sqlite+aiosqlite:///./ndx.db

SECRET_KEY=dev-secret-key-change-in-production
DEBUG=true

# 管理员账号（首次启动自动创建）
ADMIN_EMAIL=admin@example.com
ADMIN_PASSWORD=admin123
ADMIN_USERNAME=admin

CORS_ORIGINS=http://localhost:5173,http://localhost:3000
```

#### 初始化数据库

```bash
# 方法1: 使用Railway数据库
# 从Railway复制DATABASE_URL到.env

# 方法2: 本地PostgreSQL
psql -U postgres
CREATE DATABASE ndx;
\q

# 运行数据库迁移（自动创建表结构）
cd Web/backend
python -c "from app.utils.database import init_db; import asyncio; asyncio.run(init_db())"
```

#### 创建管理员账号
```bash
python init_admin.py
```

#### 启动开发服务器
```bash
# 开发模式（自动重载）
uvicorn app.main:app --reload --port 8000

# 或使用启动脚本
python start.py
```

访问：
- API文档: http://localhost:8000/docs
- 健康检查: http://localhost:8000/health

### 3. 前端设置

#### 安装依赖
```bash
cd Web/frontend
npm install
```

#### 配置环境变量

创建 `Web/frontend/.env` 文件：
```bash
VITE_API_URL=http://localhost:8000
```

#### 启动开发服务器
```bash
npm run dev
```

访问: http://localhost:5173

## 数据导入

### 1. 导入定投计划

方法A: 通过Web界面
1. 登录系统
2. 进入"定投计划"页面
3. 点击"添加计划"

方法B: 从配置文件同步
```bash
cd Web/backend
python sync_auto_invest_config.py
```

### 2. 导入历史交易

准备CSV文件 `transactions.csv`（新格式）：
```csv
fund_code,transaction_date,transaction_type,amount,note
000001,2024-01-01,买入,1000,定投
```

或旧格式：
```csv
fund_code,fund_name,transaction_date,transaction_type,shares,unit_nav,note
000001,华夏成长,2024-01-01,买入,100,1.5000,定投
```

导入方式：
- Web界面: 工具 -> 导入交易
- 命令行: `python scripts/local_manager.py` 选择选项2

### 3. 抓取净值数据

```bash
# 使用本地工具
python scripts/local_manager.py
# 选择选项1

# 或直接调用
python -c "from Web.backend.fetch_history_nav import fetch_nav_history; fetch_nav_history()"
```

## 常见开发任务

### 更新数据库Schema

1. 修改 `Web/backend/app/models/` 中的模型
2. 生成迁移脚本（如使用Alembic）
3. 应用迁移

### 添加新的API端点

1. 在 `Web/backend/app/routes/` 添加路由
2. 在 `Web/backend/app/services/` 添加业务逻辑
3. 在 `Web/backend/app/models/schemas.py` 添加数据模型
4. 更新API文档注释

### 前端开发

```bash
# 类型检查
npm run type-check

# 代码格式化
npm run format

# 构建生产版本
npm run build

# 预览生产构建
npm run preview
```

## 测试

### 后端测试
```bash
cd Web/backend
pytest tests/
```

### 前端测试
```bash
cd Web/frontend
npm test
```

## 常见问题

### 1. 数据库连接失败
- 检查PostgreSQL服务是否运行
- 验证DATABASE_URL格式
- 确认数据库已创建

### 2. CORS错误
- 检查后端CORS_ORIGINS配置
- 确认前端API_URL正确

### 3. 依赖安装失败
```bash
# Python依赖问题
conda activate NDX
pip install --upgrade pip
pip install -r requirements.txt --force-reinstall

# Node依赖问题
rm -rf node_modules package-lock.json
npm install
```

### 4. 净值数据抓取失败
- 检查网络连接
- 验证基金代码正确性
- fundSpider模块可能需要更新

## 调试技巧

### 后端调试
```python
# 在代码中添加断点
import pdb; pdb.set_trace()

# 或使用VS Code调试配置
```

### 前端调试
- 使用浏览器DevTools
- React DevTools扩展
- 查看Network面板检查API调用

### 数据库调试
```bash
# PostgreSQL
psql $DATABASE_URL

# 查看表结构
\dt
\d+ users

# 查看数据
SELECT * FROM users;
```

## 性能优化

### 后端
- 使用数据库连接池
- 添加查询索引
- 使用Redis缓存（可选）

### 前端
- 代码分割
- 懒加载组件
- 优化图片资源

## 安全检查清单

- [ ] 修改默认SECRET_KEY
- [ ] 修改管理员密码
- [ ] 限制CORS_ORIGINS
- [ ] 启用HTTPS
- [ ] 定期备份数据库
- [ ] 检查依赖漏洞: `pip-audit`, `npm audit`

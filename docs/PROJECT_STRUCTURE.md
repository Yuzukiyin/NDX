# 项目结构说明

## 目录组织

```
NDX/
├── Web/                          # Web应用主目录
│   ├── backend/                  # FastAPI后端（Railway部署）
│   │   ├── app/                  # 应用核心代码
│   │   │   ├── __init__.py
│   │   │   ├── main.py           # FastAPI应用入口
│   │   │   ├── config.py         # 配置管理
│   │   │   ├── db/               # 数据库schema
│   │   │   │   ├── fund_multitenant.sql          # SQLite schema
│   │   │   │   └── fund_multitenant_postgres.sql # PostgreSQL schema
│   │   │   ├── models/           # 数据模型
│   │   │   │   ├── user.py       # 用户模型（SQLAlchemy）
│   │   │   │   ├── schemas.py    # API数据模型（Pydantic）
│   │   │   │   └── auto_invest_schemas.py
│   │   │   ├── routes/           # API路由
│   │   │   │   ├── auth.py       # 认证端点
│   │   │   │   ├── funds.py      # 基金数据端点
│   │   │   │   └── auto_invest.py # 定投计划端点
│   │   │   ├── services/         # 业务逻辑
│   │   │   │   ├── auth_service.py
│   │   │   │   ├── fund_service.py
│   │   │   │   └── auto_invest_service.py
│   │   │   └── utils/            # 工具函数
│   │   │       ├── auth.py       # 认证工具
│   │   │       └── database.py   # 数据库连接
│   │   ├── fundSpider/           # 基金数据爬虫
│   │   │   ├── __init__.py
│   │   │   └── fund_info.py      # 净值数据抓取
│   │   ├── scripts/              # 后端维护脚本
│   │   │   ├── migrate_sqlite_to_postgres.py
│   │   │   ├── migrate_nav_history.py
│   │   │   └── verify_migration.py
│   │   ├── fetch_history_nav.py  # 净值抓取模块
│   │   ├── import_transactions.py # 交易导入模块
│   │   ├── tradeDate.py          # 交易日判断
│   │   ├── update_pending_transactions.py # 待确认交易更新
│   │   ├── init_admin.py         # 管理员初始化
│   │   ├── start.py              # 启动脚本
│   │   ├── run.py                # Railway启动入口
│   │   ├── requirements.txt      # Python依赖
│   │   ├── runtime.txt           # Python版本
│   │   ├── Procfile              # Railway配置
│   │   └── railway.toml          # Railway设置
│   │
│   └── frontend/                 # React前端（Vercel部署）
│       ├── src/
│       │   ├── main.tsx          # React入口
│       │   ├── App.tsx           # 应用根组件
│       │   ├── components/       # 可复用组件
│       │   │   └── Layout.tsx
│       │   ├── pages/            # 页面组件
│       │   │   ├── LoginPage.tsx
│       │   │   ├── RegisterPage.tsx
│       │   │   ├── DashboardPage.tsx
│       │   │   ├── FundsPage.tsx
│       │   │   ├── TransactionsPage.tsx
│       │   │   ├── AutoInvestPage.tsx
│       │   │   └── ToolsPage.tsx
│       │   ├── stores/           # 状态管理（Zustand）
│       │   │   ├── authStore.ts
│       │   │   └── fundStore.ts
│       │   ├── lib/              # 工具库
│       │   │   └── api.ts        # API客户端
│       │   └── types/            # TypeScript类型定义
│       │       └── index.ts
│       ├── index.html
│       ├── package.json          # Node依赖
│       ├── tsconfig.json         # TypeScript配置
│       ├── vite.config.ts        # Vite配置
│       ├── tailwind.config.js    # TailwindCSS配置
│       └── vercel.json           # Vercel部署配置
│
├── scripts/                      # 项目级脚本
│   ├── local_manager.py          # 本地开发工具
│   ├── sync_nav_data.py          # 定时同步脚本
│   ├── db_manager.py             # 数据库管理工具
│   └── cleanup_redundant_files.py # 清理冗余文件
│
├── docs/                         # 项目文档
│   ├── API.md                    # API文档
│   ├── DEVELOPMENT.md            # 开发指南
│   ├── DEPLOYMENT.md             # 部署指南
│   └── DATABASE_MIGRATION.md     # 数据库迁移
│
├── README.md                     # 项目说明
├── .env.example                  # 环境变量模板
├── .gitignore                    # Git忽略文件
└── transactions.csv              # 交易数据模板（被.gitignore）

```

## 核心文件说明

### 后端关键文件

#### `Web/backend/app/main.py`
- FastAPI应用主入口
- 配置CORS、路由、中间件
- 健康检查端点

#### `Web/backend/app/config.py`
- 统一配置管理
- 环境变量加载
- 数据库URL处理

#### `Web/backend/app/utils/database.py`
- 异步数据库引擎
- Session管理
- 数据库初始化

#### `Web/backend/fetch_history_nav.py`
- 基金净值数据抓取
- 支持SQLite和PostgreSQL
- 增量更新机制

#### `Web/backend/import_transactions.py`
- CSV交易导入
- 支持新旧格式
- 自动净值匹配

#### `Web/backend/tradeDate.py`
- 交易日判断
- 中国节假日数据
- 下一交易日计算

#### `Web/backend/update_pending_transactions.py`
- 待确认交易处理
- 自动净值填充
- 份额计算

### 前端关键文件

#### `Web/frontend/src/main.tsx`
- React应用入口
- 路由配置
- 全局样式

#### `Web/frontend/src/lib/api.ts`
- Axios封装
- Token自动刷新
- 请求/响应拦截

#### `Web/frontend/src/stores/authStore.ts`
- 用户认证状态
- Token管理
- 登录/登出逻辑

### 配置文件

#### `Web/backend/requirements.txt`
```txt
fastapi==0.104.1
uvicorn[standard]==0.24.0
sqlalchemy==2.0.23
asyncpg==0.29.0
psycopg2-binary==2.9.9
python-jose[cryptography]==3.3.0
passlib[bcrypt]==1.7.4
pandas>=1.2.0
beautifulsoup4>=4.9.3
requests>=2.25.1
```

#### `Web/backend/Procfile`
```
web: uvicorn app.main:app --host 0.0.0.0 --port $PORT
```

#### `Web/frontend/package.json`
核心依赖：
- react + react-router-dom
- axios
- zustand (状态管理)
- recharts (图表)
- tailwindcss (样式)

## 数据流

### 1. 用户认证流程
```
前端 -> POST /auth/login 
     -> 后端验证密码
     -> 返回JWT tokens
     -> 前端存储到localStorage
     -> 所有请求带Token
```

### 2. 净值数据更新流程
```
定时任务/手动触发
     -> fetch_history_nav.py
     -> fundSpider抓取数据
     -> 写入fund_nav_history表
     -> 触发update_pending_transactions
     -> 更新待确认交易
```

### 3. 交易导入流程
```
用户上传CSV
     -> import_transactions.py
     -> 验证格式
     -> 查询净值（如有）
     -> 计算份额
     -> 写入transactions表
```

### 4. 定投计划执行
```
每日定时检查
     -> tradeDate判断是否交易日
     -> 根据计划生成交易
     -> 调用import_transactions
     -> 记录到数据库
```

## 数据库设计

### 核心表

#### `users` - 用户表
```sql
- id (主键)
- email (唯一)
- username
- hashed_password
- is_active
- is_verified
- created_at
```

#### `auto_invest_plans` - 定投计划表
```sql
- id (主键)
- user_id (外键)
- plan_name
- fund_code
- fund_name
- amount
- frequency (daily/weekly/monthly/quarterly)
- start_date
- end_date
- enabled
```

#### `fund_nav_history` - 基金净值历史（多租户共享）
```sql
- nav_id (主键)
- fund_code
- fund_name
- price_date
- unit_nav
- cumulative_nav
- daily_growth_rate
- data_source
- fetched_at
- UNIQUE(fund_code, price_date, data_source)
```

#### `transactions` - 交易记录表
```sql
- id (主键)
- user_id (外键)
- fund_code
- fund_name
- transaction_date
- nav_date
- transaction_type (买入/卖出)
- shares
- unit_nav
- amount
- target_amount (待确认用)
- note
```

## 部署架构

```
用户浏览器
    ↓
Vercel CDN (前端)
    ↓ HTTPS
Railway (后端API)
    ↓
Railway PostgreSQL
```

### 环境变量

**后端 (Railway)**
- `DATABASE_URL` - PostgreSQL连接（自动提供）
- `SECRET_KEY` - JWT密钥
- `CORS_ORIGINS` - 允许的前端域名

**前端 (Vercel)**
- `VITE_API_URL` - 后端API地址

## 开发工作流

### 本地开发
```bash
# 后端
conda activate NDX
cd Web/backend
uvicorn app.main:app --reload

# 前端
cd Web/frontend
npm run dev
```

### 提交代码
```bash
git add .
git commit -m "feat: 添加新功能"
git push origin main
```

### 自动部署
- Railway监听main分支，自动部署后端
- Vercel监听main分支，自动部署前端

## 维护任务

### 每日
- 定时同步净值数据（cron job）
- 更新待确认交易

### 每周
- 检查错误日志
- 数据库备份

### 每月
- 更新依赖包
- 安全审计
- 性能分析

## 扩展点

### 后端
- 添加新的API端点：`app/routes/`
- 添加业务逻辑：`app/services/`
- 添加数据模型：`app/models/`

### 前端
- 添加新页面：`src/pages/`
- 添加组件：`src/components/`
- 添加状态：`src/stores/`

### 数据库
- 添加表：修改`app/db/fund_multitenant_postgres.sql`
- 添加索引：数据库迁移脚本

## 故障排查

### 日志位置
- Railway: Dashboard -> Logs
- Vercel: Dashboard -> Deployments -> Logs
- 本地: 终端输出

### 常见问题
参考 `docs/DEVELOPMENT.md` 和 `docs/DEPLOYMENT.md`

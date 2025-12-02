# NDX 基金管理系统

一个现代化的基金投资管理系统，支持定投计划、交易记录、净值查询等功能。

## 项目架构

```
NDX/
├── Web/
│   ├── backend/          # FastAPI后端（部署在Railway）
│   └── frontend/         # React前端（部署在Vercel）
├── scripts/              # 数据库迁移和维护脚本
├── docs/                 # 项目文档
└── .env.example          # 环境变量模板
```

## 技术栈

### 后端
- **框架**: FastAPI
- **数据库**: PostgreSQL (Railway)
- **认证**: JWT
- **ORM**: SQLAlchemy 2.0

### 前端
- **框架**: React + TypeScript
- **构建工具**: Vite
- **UI**: TailwindCSS
- **状态管理**: Zustand

## 快速开始

### 环境要求
- Python 3.10+
- Node.js 18+
- PostgreSQL (Railway自动提供)
- Conda环境: NDX

### 后端设置

1. 激活conda环境：
```bash
conda activate NDX
```

2. 安装依赖：
```bash
cd Web/backend
pip install -r requirements.txt
```

3. 配置环境变量（在Railway中设置）：
```bash
DATABASE_URL=postgresql://...  # Railway自动提供
SECRET_KEY=your-secret-key
```

4. 初始化数据库：
```bash
python -m app.utils.database init
```

5. 创建管理员账户：
```bash
python init_admin.py
```

6. 启动开发服务器：
```bash
uvicorn app.main:app --reload
```

### 前端设置

1. 安装依赖：
```bash
cd Web/frontend
npm install
```

2. 配置环境变量：
```bash
# .env
VITE_API_URL=http://localhost:8000
```

3. 启动开发服务器：
```bash
npm run dev
```

## 部署

### 后端（Railway）
1. 连接GitHub仓库
2. 设置环境变量：DATABASE_URL, SECRET_KEY
3. Railway自动检测并部署

### 前端（Vercel）
1. 连接GitHub仓库
2. 设置环境变量：VITE_API_URL
3. Vercel自动构建并部署

## 核心功能

### 1. 定投计划管理
- 创建/编辑/删除定投计划
- 支持多种定投频率（每日/每周/每月/每季度）
- 自动生成定投交易记录

### 2. 交易记录
- 手动添加买入/卖出记录
- CSV批量导入
- 自动计算收益

### 3. 净值数据
- 自动抓取基金历史净值
- 支持多数据源
- 定期更新

### 4. 数据可视化
- 持仓分析
- 收益曲线
- 资产分布

## 数据库架构

### 用户系统
- `users` - 用户信息
- `auto_invest_plans` - 定投计划

### 基金数据（多租户共享）
- `fund_nav_history` - 基金净值历史
- `transactions` - 交易记录

## 维护脚本

位于 `scripts/` 目录：

- `migrate_to_postgres.py` - 数据迁移
- `sync_nav_data.py` - 同步净值数据
- `backup_database.py` - 数据库备份

## 开发指南

### 代码规范
- 后端：PEP 8
- 前端：ESLint + Prettier
- 提交：遵循Conventional Commits

### 测试
```bash
# 后端测试
pytest

# 前端测试
npm test
```

## 文档索引

### 快速开始
- 📖 [快速开始指南](./docs/QUICKSTART.md) - 5分钟快速体验
- 🔧 [开发环境配置](./docs/DEVELOPMENT.md) - 本地开发详细说明
- 🚀 [生产环境部署](./docs/DEPLOYMENT.md) - Railway + Vercel部署

### 使用指南
- 📊 [交易导入指南](./docs/IMPORT_TRANSACTIONS.md) - CSV批量导入说明
- 🗄️ [数据库迁移](./docs/DATABASE_MIGRATION.md) - SQLite到PostgreSQL迁移
- 📐 [项目结构说明](./docs/PROJECT_STRUCTURE.md) - 代码组织和架构

### API文档
- 🌐 [API接口文档](./docs/API.md) - 完整的API端点说明
- 💻 交互式文档: 启动后端后访问 `/docs`

### 其他
- 📝 [重构说明](./REFACTORING.md) - 本次重构的详细内容
- 📄 [环境变量模板](./.env.example) - 配置参考

## 常见问题

### 1. 如何添加新的基金？
在定投计划中添加即可，系统会自动抓取净值数据。详见 [快速开始指南](./docs/QUICKSTART.md)

### 2. 如何导入历史交易？
准备CSV文件，通过工具页面批量导入。格式和详细说明见 [交易导入指南](./docs/IMPORT_TRANSACTIONS.md)

### 3. 数据如何备份？
Railway自动备份PostgreSQL数据，也可使用 `scripts/db_manager.py` 手动备份。

### 4. 本地开发用什么数据库？
可以使用SQLite快速测试，生产环境必须用PostgreSQL。配置方法见 [开发环境配置](./docs/DEVELOPMENT.md)

### 5. 如何从旧版本升级？
参考 [重构说明](./REFACTORING.md) 和 [数据库迁移](./docs/DATABASE_MIGRATION.md)

## 许可证

MIT License

## 贡献

欢迎提交Issue和Pull Request！

## 联系方式

- GitHub: https://github.com/Yuzukiyin/NDX
- Issues: https://github.com/Yuzukiyin/NDX/issues

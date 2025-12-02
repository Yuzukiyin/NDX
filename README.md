# NDX 基金管理系统

现代化的个人基金投资管理系统,支持定投计划、交易记录管理、净值数据自动抓取等功能。

## 🚀 在线访问

- **前端**: https://ndx-khaki.vercel.app
- **后端API**: https://ndx-production.up.railway.app
- **API文档**: https://ndx-production.up.railway.app/docs

## ✨ 核心功能

- 📊 **交易管理**: 记录买入/卖出交易,自动计算收益
- 🔄 **定投计划**: 创建和管理定期投资计划
- 📈 **净值追踪**: 自动抓取基金净值数据
- 💰 **收益分析**: 实时计算持仓收益和收益率
- 📱 **响应式UI**: 支持桌面和移动设备

## 🛠️ 技术栈

**后端** (Railway):
- FastAPI + Python 3.10
- PostgreSQL
- SQLAlchemy 2.0
- JWT认证

**前端** (Vercel):
- React 18 + TypeScript
- Vite
- TailwindCSS
- Zustand状态管理

## 📚 文档

- [快速开始](docs/QUICKSTART.md) - 5分钟快速上手
- [开发指南](docs/DEVELOPMENT.md) - 本地开发环境配置
- [部署文档](docs/DEPLOYMENT.md) - Railway + Vercel部署
- [API文档](docs/API.md) - 完整API接口说明
- [项目结构](docs/PROJECT_STRUCTURE.md) - 代码组织架构
- [Railway配置](RAILWAY_CONFIG.md) - 生产环境配置
- [配置文件说明](docs/CONFIG_FILES.md) - 所有配置文件详解

## ⚡ 快速开始

### 本地开发

```bash
# 1. 克隆项目
git clone https://github.com/Yuzukiyin/NDX.git
cd NDX

# 2. 后端设置
cd Web/backend
pip install -r requirements.txt
python start.py

# 3. 前端设置 (新终端)
cd Web/frontend
npm install
npm run dev
```

访问 http://localhost:3000

### 登录信息
- 邮箱: 1712008344@qq.com
- 密码: Lzy171200

## 📁 项目结构

```
NDX/
├── Web/
│   ├── backend/          # FastAPI后端
│   │   ├── app/          # 应用代码
│   │   ├── fundSpider/   # 基金数据爬虫
│   │   └── start.py      # 启动脚本
│   └── frontend/         # React前端
│       └── src/          # 源代码
├── scripts/              # 维护脚本
│   ├── db_manager.py     # 数据库管理
│   ├── local_manager.py  # 本地开发工具
│   └── sync_nav_data.py  # 数据同步
└── docs/                 # 项目文档
```

## 🔧 维护脚本

位于 `scripts/` 目录,用于数据库管理和数据同步:

```bash
# 数据库管理
python scripts/db_manager.py

# 同步净值数据
python scripts/sync_nav_data.py

# 本地开发工具
python scripts/local_manager.py
```

详见: [scripts/README.md](scripts/README.md)

## 🌐 部署

### Railway (后端)
- 自动检测 `Web/backend/`
- 读取 `railway.toml` 配置
- 环境变量在Railway控制台设置

### Vercel (前端)
- 自动检测 `Web/frontend/`
- 读取 `vercel.json` 配置
- 环境变量: `VITE_API_BASE_URL`

详见: [DEPLOYMENT.md](docs/DEPLOYMENT.md)

## 📝 许可证

MIT License

## 🤝 贡献

欢迎提交 Issue 和 Pull Request!

---

**开发者**: Yuzukiyin  
**最后更新**: 2025-12-02

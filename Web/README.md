# NDX基金管理系统 - Web应用开发指南

## 项目概述

NDX基金管理Web应用是一个现代化的全栈Web应用,包含:
- **后端**: FastAPI (Python)
- **前端**: React + TypeScript + Vite
- **UI框架**: TailwindCSS + Framer Motion
- **状态管理**: Zustand
- **数据库**: SQLite (用户数据) + 原有fund.db(基金数据)

## 技术栈

### 后端
- FastAPI - 高性能异步Web框架
- SQLAlchemy - ORM数据库操作
- Pydantic - 数据验证
- Python-JOSE - JWT认证
- Passlib - 密码加密

### 前端
- React 18 - UI库
- TypeScript - 类型安全
- Vite - 快速构建工具
- TailwindCSS - 实用CSS框架
- Framer Motion - 动画库
- Recharts - 图表库
- Axios - HTTP客户端
- Zustand - 状态管理

## 前置要求

### 后端开发环境
1. **Python 3.10+**
   - 下载: https://www.python.org/downloads/
   - 安装时勾选"Add Python to PATH"

2. **pip** (Python包管理器,通常随Python安装)

3. **虚拟环境工具**
   ```bash
   pip install virtualenv
   ```

### 前端开发环境
1. **Node.js 18+**
   - 下载: https://nodejs.org/
   - 推荐使用LTS版本

2. **npm** 或 **yarn** (Node包管理器,随Node.js安装)

## 安装和运行

### 后端设置

#### 1. 创建虚拟环境
```bash
cd D:\AAAStudy\NDX\Web\backend

# 创建虚拟环境
python -m venv venv

# 激活虚拟环境
# Windows CMD:
venv\Scripts\activate
# Windows PowerShell:
venv\Scripts\Activate.ps1
# macOS/Linux:
source venv/bin/activate
```

#### 2. 安装依赖
```bash
pip install -r requirements.txt
```

#### 3. 配置环境变量
```bash
# 复制示例环境变量文件
copy .env.example .env

# 编辑.env文件,修改SECRET_KEY等配置
```

#### 4. 运行后端服务
```bash
python run.py
```

后端将在 http://localhost:8000 启动

访问 http://localhost:8000/docs 查看API文档 (Swagger UI)

### 前端设置

#### 1. 安装依赖
```bash
cd D:\AAAStudy\NDX\Web\frontend

npm install
# 或使用 yarn
yarn install
```

#### 2. 运行开发服务器
```bash
npm run dev
# 或
yarn dev
```

前端将在 http://localhost:3000 启动

#### 3. 构建生产版本
```bash
npm run build
# 或
yarn build
```

构建文件将输出到 `dist/` 目录

## 项目结构

### 后端目录结构
```
backend/
├── app/
│   ├── __init__.py
│   ├── main.py                 # 主应用入口
│   ├── config.py               # 配置文件
│   ├── models/                 # 数据模型
│   │   ├── user.py            # 用户模型
│   │   └── schemas.py         # Pydantic模式
│   ├── routes/                 # API路由
│   │   ├── auth.py            # 认证相关
│   │   └── funds.py           # 基金数据相关
│   ├── services/               # 业务逻辑
│   │   ├── auth_service.py    # 认证服务
│   │   └── fund_service.py    # 基金服务
│   └── utils/                  # 工具函数
│       ├── auth.py            # 认证工具
│       └── database.py        # 数据库工具
├── requirements.txt            # Python依赖
├── run.py                      # 运行脚本
└── .env.example               # 环境变量示例
```

### 前端目录结构
```
frontend/
├── src/
│   ├── main.tsx               # 应用入口
│   ├── App.tsx                # 根组件
│   ├── index.css              # 全局样式
│   ├── components/            # 可复用组件
│   │   └── Layout.tsx         # 布局组件
│   ├── pages/                 # 页面组件
│   │   ├── LoginPage.tsx
│   │   ├── RegisterPage.tsx
│   │   ├── DashboardPage.tsx
│   │   ├── FundsPage.tsx
│   │   └── TransactionsPage.tsx
│   ├── stores/                # 状态管理
│   │   ├── authStore.ts       # 认证状态
│   │   └── fundStore.ts       # 基金数据状态
│   ├── lib/                   # 工具库
│   │   └── api.ts             # API客户端
│   └── types/                 # TypeScript类型
│       └── index.ts
├── public/                    # 静态资源
├── index.html                 # HTML模板
├── package.json               # 项目配置
├── tsconfig.json              # TypeScript配置
├── tailwind.config.js         # TailwindCSS配置
└── vite.config.ts             # Vite配置
```

## API接口说明

### 认证接口

#### POST /auth/register
注册新用户
```json
{
  "email": "user@example.com",
  "username": "username",
  "password": "Password123"
}
```

#### POST /auth/login
用户登录
```json
{
  "email": "user@example.com",
  "password": "Password123"
}
```

#### GET /auth/me
获取当前用户信息(需要认证)

### 基金数据接口

#### GET /funds/overview
获取所有基金概览(需要认证)

#### GET /funds/overview/{fund_code}
获取特定基金详情(需要认证)

#### GET /funds/transactions
获取交易记录(需要认证)

#### GET /funds/nav-history/{fund_code}
获取历史净值数据(需要认证)

#### GET /funds/profit-summary
获取收益汇总(需要认证)

#### POST /funds/initialize-database
初始化用户基金数据库(需要认证)

#### POST /funds/fetch-nav
抓取历史净值(需要认证)

#### POST /funds/update-pending
更新待确认交易(需要认证)

## 功能特性

### 1. 用户认证
- ✅ 邮箱注册
- ✅ 密码强度验证(8位+大小写字母+数字)
- ✅ JWT令牌认证
- ✅ 刷新令牌自动续期
- ✅ 记住登录状态

### 2. 基金数据展示
- ✅ 基金概览卡片
- ✅ 收益统计
- ✅ 历史净值图表
- ✅ 交易记录列表
- ✅ 数据实时更新

### 3. UI/UX设计
- ✅ 极简主义设计
- ✅ 圆角卡片布局
- ✅ 柔和阴影效果
- ✅ 弹性动画(Spring/Elastic曲线)
- ✅ 响应式设计
- ✅ 深色模式支持(可扩展)

### 4. 原有功能集成
- ✅ 初始化数据库
- ✅ 抓取历史净值
- ✅ 导入交易记录
- ✅ 更新待确认交易
- ✅ 导出净值数据/图表

## 设计规范

### 颜色方案
- 主色调: 蓝色 (#0ea5e9)
- 辅助色: 紫色 (#a855f7)
- 成功: 绿色 (#10b981)
- 错误: 红色 (#ef4444)
- 背景: 灰白色 (#f9fafb)

### 圆角规范
- 小卡片: 1rem (16px)
- 中等卡片: 1.5rem (24px)
- 大卡片: 2rem (32px)

### 阴影规范
- 轻微: shadow-soft
- 明显: shadow-soft-lg

### 动画曲线
```css
/* Spring弹性 */
.spring-animation {
  transition-timing-function: cubic-bezier(0.68, -0.55, 0.265, 1.55);
}

/* Elastic弹性 */
.elastic-animation {
  transition-timing-function: cubic-bezier(0.175, 0.885, 0.32, 1.275);
}
```

## 开发建议

### 后端开发
1. 使用类型提示提高代码可读性
2. 遵循RESTful API设计原则
3. 添加适当的错误处理和日志
4. 编写API文档和测试

### 前端开发
1. 使用TypeScript确保类型安全
2. 组件化开发,提高代码复用
3. 使用React Hooks管理状态
4. 优化性能(懒加载、代码分割)

## 部署指南

### 后端部署
1. 使用Gunicorn + Uvicorn Workers
2. 配置Nginx反向代理
3. 使用HTTPS(Let's Encrypt)
4. 设置环境变量

```bash
gunicorn app.main:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000
```

### 前端部署
1. 构建生产版本
2. 部署到静态托管服务(Vercel、Netlify)
3. 或使用Nginx提供静态文件

```bash
npm run build
```

## 常见问题

### Q: 后端启动失败
A: 
1. 检查Python版本(需要3.10+)
2. 确认所有依赖已安装
3. 查看错误日志

### Q: 前端无法连接后端
A:
1. 确保后端服务已启动
2. 检查代理配置(vite.config.ts)
3. 查看浏览器控制台错误

### Q: CORS错误
A:
1. 检查backend/app/config.py中的CORS_ORIGINS配置
2. 确保前端地址在允许列表中

### Q: 数据库错误
A:
1. 检查数据库文件路径
2. 确保有写入权限
3. 尝试重新初始化数据库

## 扩展功能建议

- [ ] 邮箱验证
- [ ] 密码重置
- [ ] 双因素认证
- [ ] 文件上传(CSV导入)
- [ ] 数据导出(Excel/PDF)
- [ ] 消息通知
- [ ] 深色模式切换
- [ ] 多语言支持

## 资源链接

- FastAPI文档: https://fastapi.tiangolo.com/
- React文档: https://react.dev/
- TailwindCSS: https://tailwindcss.com/
- Framer Motion: https://www.framer.com/motion/
- TypeScript: https://www.typescriptlang.org/

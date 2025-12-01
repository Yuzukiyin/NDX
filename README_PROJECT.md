# NDX基金管理系统 - 完整开发指南

## 项目概述

NDX基金管理系统是一个全栈应用,支持Web端和Android端,用于管理个人基金投资组合。

### 核心功能
1. **用户认证系统**
   - 邮箱注册(强密码要求)
   - JWT令牌认证
   - 自动刷新令牌
   - 记住登录状态

2. **基金数据管理**
   - 基金概览展示
   - 交易记录查询
   - 历史净值图表
   - 收益统计分析

3. **原有功能集成**
   - 初始化数据库
   - 抓取历史净值
   - 导入交易数据
   - 更新待确认交易
   - 导出数据/图表

### 设计理念
- **极简主义**: 简洁清爽的界面
- **圆角卡片**: 现代化的卡片设计
- **柔和阴影**: 精致的视觉层次
- **弹性动画**: Spring/Elastic动画曲线

## 快速开始

### Web应用

#### 前置要求
- Python 3.10+
- Node.js 18+
- pip 和 npm

#### 启动步骤

**1. 启动后端服务**
```bash
cd Web/backend

# 创建虚拟环境
python -m venv venv

# 激活虚拟环境
venv\Scripts\activate  # Windows
# source venv/bin/activate  # macOS/Linux

# 安装依赖
pip install -r requirements.txt

# 配置环境变量
copy .env.example .env

# 运行服务
python run.py
```

后端运行在: http://localhost:8000

**2. 启动前端服务**
```bash
cd Web/frontend

# 安装依赖
npm install

# 运行开发服务器
npm run dev
```

前端运行在: http://localhost:3000

**3. 访问应用**
- 打开浏览器访问: http://localhost:3000
- 注册新账户或登录
- 初始化基金数据库
- 开始使用!

### Android应用

#### 前置要求
- Android Studio Hedgehog+ (2023.1.1+)
- JDK 17+
- Android SDK (API 24+)

#### 开发步骤

1. **安装Android Studio**
   - 下载: https://developer.android.com/studio
   - 选择Standard安装
   
2. **打开项目**
   - File → Open
   - 选择 `Android/` 目录
   - 等待Gradle同步完成

3. **配置API地址**
   ```kotlin
   // 修改 ApiConfig.kt
   const val BASE_URL = "http://10.0.2.2:8000/api/"
   ```

4. **运行应用**
   - 创建模拟器或连接真机
   - 点击运行按钮

详细说明请查看: [Android/README.md](./Android/README.md)

## 项目结构

```
NDX/
├── Web/                        # Web应用
│   ├── backend/                # FastAPI后端
│   │   ├── app/
│   │   │   ├── main.py        # 主应用
│   │   │   ├── config.py      # 配置
│   │   │   ├── models/        # 数据模型
│   │   │   ├── routes/        # API路由
│   │   │   ├── services/      # 业务逻辑
│   │   │   └── utils/         # 工具函数
│   │   ├── requirements.txt
│   │   └── run.py
│   ├── frontend/               # React前端
│   │   ├── src/
│   │   │   ├── App.tsx
│   │   │   ├── components/    # 组件
│   │   │   ├── pages/         # 页面
│   │   │   ├── stores/        # 状态管理
│   │   │   ├── lib/           # API客户端
│   │   │   └── types/         # 类型定义
│   │   ├── package.json
│   │   └── vite.config.ts
│   └── README.md              # Web文档
├── Android/                    # Android应用
│   ├── app/
│   │   └── src/main/
│   │       ├── java/com/ndx/fundmanager/
│   │       │   ├── MainActivity.kt
│   │       │   ├── ui/        # UI组件
│   │       │   ├── data/      # 数据层
│   │       │   └── di/        # 依赖注入
│   │       └── res/           # 资源文件
│   ├── build.gradle.kts
│   └── README.md              # Android文档
├── 原有文件/                   # 原NDX基金管理系统
│   ├── AAAfund_manager.py
│   ├── init_database.py
│   ├── fetch_history_nav.py
│   └── ...
└── README_PROJECT.md          # 本文档
```

## 技术栈详情

### Web后端
| 技术 | 版本 | 用途 |
|------|------|------|
| Python | 3.10+ | 编程语言 |
| FastAPI | 0.104+ | Web框架 |
| SQLAlchemy | 2.0+ | ORM |
| Pydantic | 2.5+ | 数据验证 |
| python-jose | 3.3+ | JWT |
| passlib | 1.7+ | 密码加密 |

### Web前端
| 技术 | 版本 | 用途 |
|------|------|------|
| React | 18.2 | UI库 |
| TypeScript | 5.2+ | 类型系统 |
| Vite | 5.0+ | 构建工具 |
| TailwindCSS | 3.3+ | CSS框架 |
| Framer Motion | 10.16+ | 动画库 |
| Zustand | 4.4+ | 状态管理 |
| Axios | 1.6+ | HTTP客户端 |
| Recharts | 2.10+ | 图表库 |

### Android
| 技术 | 版本 | 用途 |
|------|------|------|
| Kotlin | 1.9+ | 编程语言 |
| Jetpack Compose | 2023.10+ | UI框架 |
| Material 3 | - | 设计系统 |
| Retrofit | 2.9+ | 网络请求 |
| Room | 2.6+ | 本地数据库 |
| Hilt | 2.48+ | 依赖注入 |
| Coroutines | 1.7+ | 异步编程 |

## API接口概览

### 认证接口
- `POST /auth/register` - 用户注册
- `POST /auth/login` - 用户登录
- `POST /auth/refresh` - 刷新令牌
- `GET /auth/me` - 获取当前用户

### 基金数据接口
- `GET /funds/overview` - 获取基金概览
- `GET /funds/overview/{code}` - 获取基金详情
- `GET /funds/transactions` - 获取交易记录
- `GET /funds/nav-history/{code}` - 获取历史净值
- `GET /funds/profit-summary` - 获取收益汇总

### 功能接口
- `POST /funds/initialize-database` - 初始化数据库
- `POST /funds/fetch-nav` - 抓取历史净值
- `POST /funds/update-pending` - 更新待确认交易

详细API文档: http://localhost:8000/docs

## 数据库设计

### 用户数据库 (ndx_users.db)
- `users` - 用户表
- `refresh_tokens` - 刷新令牌表

### 基金数据库 (user_X_fund.db)
每个用户独立的基金数据库,包含:
- `transactions` - 交易记录
- `fund_overview` - 基金概览
- `fund_nav_history` - 历史净值
- `fund_realtime_overview` - 实时概览视图
- `profit_summary` - 收益汇总视图

## 安全特性

### 密码安全
- 最小长度: 8字符
- 必须包含: 大写字母、小写字母、数字
- Bcrypt加密存储

### 认证安全
- JWT令牌认证
- 访问令牌: 30分钟有效期
- 刷新令牌: 7天有效期
- 自动令牌刷新机制

### 数据隔离
- 每个用户独立数据库
- 基于用户ID的数据访问控制
- API请求需要有效令牌

## 开发工具推荐

### 代码编辑器
- **VS Code** (推荐)
  - Python插件
  - ESLint插件
  - Prettier插件
  - TailwindCSS IntelliSense
  
- **PyCharm Professional** (Python开发)
- **WebStorm** (前端开发)
- **Android Studio** (Android开发)

### API测试
- **Postman** - API测试工具
- **Insomnia** - REST客户端
- Swagger UI (内置: http://localhost:8000/docs)

### 数据库管理
- **DB Browser for SQLite** - SQLite可视化工具
- **DBeaver** - 通用数据库工具

## 部署选项

### Web应用

**后端部署**
- **服务器**: 阿里云、腾讯云、AWS
- **容器**: Docker + Docker Compose
- **服务**: Gunicorn + Nginx
- **域名**: 配置HTTPS证书

**前端部署**
- **静态托管**: Vercel、Netlify、Cloudflare Pages
- **CDN**: 阿里云OSS、七牛云
- **服务器**: Nginx静态文件服务

### Android应用

**发布渠道**
- Google Play Store
- 华为应用市场
- 小米应用商店
- OPPO软件商店
- vivo应用商店

**打包发布**
```bash
./gradlew assembleRelease
# 生成APK: app/build/outputs/apk/release/app-release.apk
```

## 常见问题

### 1. 后端无法启动
- 检查Python版本
- 确认虚拟环境已激活
- 验证所有依赖已安装

### 2. 前端无法连接后端
- 确保后端服务运行在8000端口
- 检查CORS配置
- 查看浏览器控制台错误

### 3. Android应用无法编译
- 更新Android Studio
- Sync Gradle files
- Clean & Rebuild项目

### 4. 数据库初始化失败
- 检查文件权限
- 确认数据库路径正确
- 查看错误日志

## 性能优化建议

### 后端优化
- 使用连接池
- 添加缓存(Redis)
- 数据库查询优化
- 异步处理耗时任务

### 前端优化
- 代码分割(Code Splitting)
- 懒加载(Lazy Loading)
- 图片优化
- 缓存策略

### Android优化
- ProGuard代码混淆
- 资源优化
- 网络请求缓存
- 内存管理

## 测试建议

### 后端测试
```bash
pip install pytest pytest-asyncio
pytest tests/
```

### 前端测试
```bash
npm install --save-dev vitest
npm run test
```

### Android测试
```bash
./gradlew test
```

## 贡献指南

1. Fork项目
2. 创建特性分支
3. 提交更改
4. 推送到分支
5. 创建Pull Request

## 许可证

本项目采用MIT许可证

## 联系方式

如有问题,请查看:
- Web文档: [Web/README.md](./Web/README.md)
- Android文档: [Android/README.md](./Android/README.md)

## 更新日志

### v1.0.0 (2024-12-01)
- ✅ 初始版本发布
- ✅ Web端完整功能
- ✅ Android端基础架构
- ✅ 用户认证系统
- ✅ 基金数据管理
- ✅ 极简UI设计

## 后续计划

- [ ] 邮箱验证功能
- [ ] 密码重置功能
- [ ] 数据导出(Excel/PDF)
- [ ] 推送通知
- [ ] 深色模式
- [ ] 多语言支持
- [ ] 移动端优化
- [ ] PWA支持

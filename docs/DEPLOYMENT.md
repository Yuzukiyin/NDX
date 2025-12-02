# 部署指南

## Railway后端部署

### 1. 准备工作

#### 注册Railway账号
访问 https://railway.app 并注册

#### 连接GitHub仓库
1. 在Railway创建新项目
2. 选择 "Deploy from GitHub repo"
3. 授权并选择NDX仓库

### 2. 配置Railway

#### 设置根目录
Railway Settings -> Source:
- Root Directory: `Web/backend`

#### 环境变量配置
Railway Settings -> Variables:

```bash
# Railway自动提供DATABASE_URL，无需手动设置
# DATABASE_URL=postgresql://...

# 必需配置
SECRET_KEY=your-super-secret-random-key-here
DEBUG=false
APP_NAME=NDX Fund Manager

# 管理员账号（首次部署）
ADMIN_EMAIL=your-email@example.com
ADMIN_PASSWORD=secure-password
ADMIN_USERNAME=admin

# CORS（添加你的Vercel域名）
CORS_ORIGINS=https://your-app.vercel.app,https://ndx-git-main-yuzukiyins-projects.vercel.app

# 可选：邮件服务
MAIL_USERNAME=
MAIL_PASSWORD=
MAIL_FROM=
MAIL_SERVER=smtp.gmail.com
MAIL_PORT=587
```

#### 生成安全的SECRET_KEY
```bash
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

### 3. 数据库配置

Railway会自动提供PostgreSQL数据库：
1. 在项目中添加 "PostgreSQL" 服务
2. Railway自动设置 `DATABASE_URL` 环境变量
3. 应用会自动连接到数据库

### 4. 部署

#### 自动部署
- 推送代码到GitHub main分支
- Railway自动检测并部署

#### 手动部署
Railway Dashboard -> Deploy -> Deploy Now

#### 检查部署状态
Railway Dashboard -> Deployments
- 查看构建日志
- 检查运行状态

### 5. 数据库初始化

部署后首次访问会自动：
1. 创建数据库表结构
2. 创建管理员账号（如设置了环境变量）

或手动初始化：
```bash
# 在Railway shell中执行
python init_admin.py
```

### 6. 配置定时任务（可选）

同步净值数据的定时任务：

方法A: 使用Railway Cron
1. 创建新服务
2. 设置定时执行 `python scripts/sync_nav_data.py`

方法B: 使用外部服务
- 使用GitHub Actions
- 使用cron-job.org定时访问API端点

## Vercel前端部署

### 1. 准备工作

#### 注册Vercel账号
访问 https://vercel.com 并注册

#### 连接GitHub仓库
1. 创建新项目
2. 导入GitHub仓库
3. 选择NDX仓库

### 2. 配置Vercel

#### 项目设置
- Framework Preset: Vite
- Root Directory: `Web/frontend`
- Build Command: `npm run build`
- Output Directory: `dist`

#### 环境变量
Vercel Settings -> Environment Variables:

```bash
VITE_API_URL=https://your-railway-app.railway.app
```

替换为你的Railway后端URL

### 3. 部署

#### 自动部署
- 推送到main分支自动部署到生产环境
- 推送到其他分支创建预览部署

#### 手动部署
Vercel Dashboard -> Deployments -> Redeploy

### 4. 域名配置（可选）

#### 自定义域名
1. Vercel Settings -> Domains
2. 添加自定义域名
3. 配置DNS记录
4. 等待SSL证书生成

#### 更新CORS
将新域名添加到Railway的CORS_ORIGINS环境变量

## 监控和维护

### 1. 日志查看

#### Railway日志
- Dashboard -> Logs
- 实时查看应用日志
- 过滤错误信息

#### Vercel日志
- Dashboard -> Deployments -> Logs
- 查看构建和运行时日志

### 2. 性能监控

#### Railway
- Dashboard -> Metrics
- CPU/内存使用情况
- 响应时间

#### Vercel
- Analytics标签页
- 访问量统计
- Core Web Vitals

### 3. 数据库备份

#### Railway自动备份
Railway Pro计划包含自动备份

#### 手动备份
```bash
# 本地执行
pg_dump $DATABASE_URL > backup_$(date +%Y%m%d).sql

# 恢复
psql $DATABASE_URL < backup_20240101.sql
```

### 4. 更新部署

#### 更新依赖
```bash
# 后端
pip install --upgrade package-name
pip freeze > requirements.txt

# 前端
npm update
npm audit fix
```

#### 推送更新
```bash
git add .
git commit -m "Update dependencies"
git push origin main
```

Railway和Vercel会自动重新部署

## 故障排查

### 1. 部署失败

#### Railway构建失败
- 检查requirements.txt格式
- 查看构建日志错误信息
- 验证Python版本兼容性

#### Vercel构建失败
- 检查package.json
- 查看构建日志
- 验证Node版本

### 2. 数据库连接问题

```python
# 测试数据库连接
import asyncio
from sqlalchemy import create_engine, text

async def test_db():
    engine = create_engine(DATABASE_URL)
    with engine.connect() as conn:
        result = conn.execute(text("SELECT 1"))
        print(result.fetchone())

asyncio.run(test_db())
```

### 3. CORS错误

确认：
1. Railway CORS_ORIGINS包含Vercel域名
2. 前端VITE_API_URL正确
3. 协议匹配（https）

### 4. 404错误

#### 前端路由404
Vercel Settings -> Rewrites:
```json
{
  "source": "/(.*)",
  "destination": "/index.html"
}
```

#### API 404
- 检查Railway应用是否运行
- 验证API URL正确
- 查看Railway日志

## 成本优化

### Railway
- Hobby计划: $5/月
- 包含512MB RAM
- 1GB存储
- PostgreSQL数据库

### Vercel
- Hobby计划: 免费
- 包含100GB带宽
- 无限部署

### 总成本
约$5-10/月（取决于使用量）

## 安全最佳实践

### 1. 环境变量
- ✅ 使用强随机SECRET_KEY
- ✅ 不在代码中硬编码密码
- ✅ 定期轮换密钥

### 2. 数据库
- ✅ 使用SSL连接
- ✅ 定期备份
- ✅ 限制公网访问

### 3. API
- ✅ 启用JWT认证
- ✅ 限制CORS来源
- ✅ 设置速率限制

### 4. 前端
- ✅ 使用HTTPS
- ✅ 启用CSP
- ✅ 定期更新依赖

## 扩展建议

### 1. 添加Redis缓存
Railway -> Add Service -> Redis
- 缓存净值数据
- Session存储

### 2. 添加对象存储
用于存储文件：
- Railway S3
- Cloudflare R2

### 3. 添加CDN
加速静态资源：
- Vercel内置CDN
- Cloudflare

### 4. 监控告警
- Sentry错误追踪
- UptimeRobot可用性监控
- Email/Slack告警

## 更新检查清单

部署新版本前：
- [ ] 本地测试通过
- [ ] 数据库迁移脚本准备
- [ ] 环境变量确认
- [ ] 备份数据库
- [ ] 通知用户维护窗口
- [ ] 准备回滚方案

部署后：
- [ ] 检查健康端点
- [ ] 测试核心功能
- [ ] 查看错误日志
- [ ] 监控性能指标
- [ ] 用户反馈收集

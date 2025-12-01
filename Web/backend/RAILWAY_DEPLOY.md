# Railway 后端部署指南

## 方式一：通过 Railway 网站部署（推荐）

### 1. 准备工作
确保代码已推送到 GitHub：
```powershell
cd d:\AAAStudy\NDX
git add .
git commit -m "Add Railway deployment config"
git push
```

### 2. 创建 Railway 项目

1. **访问**: https://railway.app
2. **登录**: 使用 GitHub 账号登录
3. **新建项目**: 
   - 点击 "New Project"
   - 选择 "Deploy from GitHub repo"
   - 选择你的仓库 `NDX`
   - 点击 "Deploy Now"

### 3. 配置项目

Railway 会自动检测到 Python 项目，但需要手动配置：

#### 3.1 设置 Root Directory
1. 在项目设置中找到 "Settings"
2. 找到 "Root Directory" 设置
3. 填写: `Web/backend`
4. 保存

#### 3.2 添加环境变量
在 "Variables" 标签页添加：

```env
# 必需的环境变量
SECRET_KEY=你的32位随机密钥生成方法见下方
DATABASE_URL=sqlite:///./ndx_users.db
CORS_ORIGINS=https://ndx-khaki.vercel.app

# 可选的邮件配置（如果需要）
MAIL_USERNAME=your-email@gmail.com
MAIL_PASSWORD=your-app-password
MAIL_FROM=your-email@gmail.com
MAIL_PORT=587
MAIL_SERVER=smtp.gmail.com
```

**生成 SECRET_KEY**:
```powershell
# 在本地运行
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

#### 3.3 配置启动命令（可选）
Railway 会自动使用 `Procfile`，但也可以在设置中手动指定：
- Start Command: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`

### 4. 部署

1. Railway 会自动开始构建
2. 等待构建完成（约 2-3 分钟）
3. 部署成功后，点击 "Settings" → "Domains"
4. 点击 "Generate Domain" 生成公网域名
5. 记录下域名，例如: `https://your-app.railway.app`

### 5. 初始化管理员账户

部署成功后，需要在 Railway 运行初始化脚本：

1. 在 Railway 项目页面，进入 "Deployments" 标签
2. 点击最新的部署
3. 找到 "Shell" 或者使用 Railway CLI：

```bash
# 安装 Railway CLI（本地执行）
npm install -g @railway/cli

# 登录
railway login

# 链接到项目
railway link

# 运行初始化
railway run python init_admin.py
```

或者手动创建管理员：
```bash
# 在 Railway Shell 中执行
python init_admin.py
```

### 6. 测试后端 API

访问你的 Railway 域名测试：
- API 文档: `https://your-app.railway.app/docs`
- 健康检查: `https://your-app.railway.app/api/health`

## 方式二：使用 Railway CLI 部署

```powershell
# 1. 安装 Railway CLI
npm install -g @railway/cli

# 2. 登录
railway login

# 3. 进入后端目录
cd d:\AAAStudy\NDX\Web\backend

# 4. 初始化项目
railway init

# 5. 添加环境变量
railway variables set SECRET_KEY=你的密钥
railway variables set DATABASE_URL=sqlite:///./ndx_users.db
railway variables set CORS_ORIGINS=https://ndx-khaki.vercel.app

# 6. 部署
railway up

# 7. 生成域名
railway domain

# 8. 初始化管理员
railway run python init_admin.py
```

## 方式三：使用 Render 部署

### 1. 创建 Render 账号
访问: https://render.com

### 2. 新建 Web Service
1. 点击 "New" → "Web Service"
2. 连接 GitHub 仓库 `NDX`
3. 配置：
   - Name: `ndx-backend`
   - Root Directory: `Web/backend`
   - Environment: `Python 3`
   - Build Command: `pip install -r requirements.txt`
   - Start Command: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`

### 3. 添加环境变量
在 "Environment" 标签页添加：
- `SECRET_KEY`: 生成的密钥
- `DATABASE_URL`: `sqlite:///./ndx_users.db`
- `CORS_ORIGINS`: `https://ndx-khaki.vercel.app`

### 4. 部署
点击 "Create Web Service"，等待部署完成。

## 最后一步：更新前端配置

部署后端成功后，需要更新 Vercel 前端的环境变量：

### 在 Vercel 项目中
1. 进入项目设置 Settings
2. 找到 Environment Variables
3. 添加/更新：
   ```
   VITE_API_BASE_URL = https://your-app.railway.app
   ```
4. 保存后，重新部署前端：
   - 进入 Deployments
   - 选择最新部署
   - 点击 "Redeploy"

## 常见问题

### Q: 数据库怎么办？
A: Railway 支持 SQLite 文件，但推荐使用 PostgreSQL（Railway 免费提供）：
```bash
# 添加 PostgreSQL
railway add

# 选择 PostgreSQL
# Railway 会自动设置 DATABASE_URL
```

然后修改 `Web/backend/app/config.py` 支持 PostgreSQL。

### Q: 用户数据库隔离怎么处理？
A: Railway 的文件系统是持久化的（与 Vercel 不同），SQLite 文件会保留。

### Q: 如何查看日志？
A: 
- Railway: 项目页面 → Deployments → View Logs
- Render: 项目页面 → Logs 标签

### Q: 如何更新部署？
A: 推送代码到 GitHub，Railway/Render 会自动重新部署：
```bash
git push
```

## 完整流程总结

```powershell
# 1. 推送代码
cd d:\AAAStudy\NDX
git add .
git commit -m "Add backend deployment config"
git push

# 2. 在 Railway 网站部署
# - 访问 railway.app
# - 连接 GitHub 仓库
# - 设置 Root Directory: Web/backend
# - 添加环境变量
# - 生成域名

# 3. 初始化数据
# - 使用 Railway Shell 或 CLI
# - 运行: python init_admin.py

# 4. 更新 Vercel 前端
# - 设置 VITE_API_BASE_URL
# - 重新部署

# 5. 访问应用
# - 前端: https://ndx-khaki.vercel.app
# - 后端: https://your-app.railway.app
# - 登录: 1712008344@qq.com / Lzy171200
```

## 需要帮助？

如果部署过程中遇到问题：
1. 检查 Railway 部署日志
2. 确认环境变量设置正确
3. 测试 API 文档页面: `/docs`
4. 查看 CORS 配置是否包含前端域名

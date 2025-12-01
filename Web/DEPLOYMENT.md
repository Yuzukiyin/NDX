# Vercel部署指南

## 前置要求
- GitHub账号
- Vercel账号 (可用GitHub登录)

## 步骤1: 准备Git仓库

```bash
cd D:\AAAStudy\NDX
git add .
git commit -m "Prepare for Vercel deployment"
git push origin main
```

## 步骤2: 部署前端到Vercel

### 方法1: 通过Vercel网站部署

1. **登录Vercel**: https://vercel.com
2. **导入项目**:
   - 点击 "Add New" → "Project"
   - 选择您的GitHub仓库 `NDX`
   - 点击 "Import"

3. **配置项目**:
   - Framework Preset: `Vite` (自动检测,因为前端使用Vite构建React应用)
   - Root Directory: `Web/frontend`
   - Build Command: `npm run build`
   - Output Directory: `dist`
   - Install Command: `npm install`
   
   > 💡 **说明**: 虽然是React应用,但Vercel检测到Vite配置文件,所以显示"Vite"。
   > Vite是构建工具,React是UI框架,两者配合使用。

4. **环境变量**:
   - 添加 `VITE_API_BASE_URL`: `https://your-backend-url.com`
   
5. **部署**: 点击 "Deploy"

### 方法2: 使用Vercel CLI

```bash
# 安装Vercel CLI
npm install -g vercel

# 登录
vercel login

# 进入前端目录
cd Web/frontend

# 部署
vercel

# 生产部署
vercel --prod
```

## 步骤3: 部署后端

### 选项A: 使用Railway (推荐)

1. **访问**: https://railway.app
2. **新建项目**: New Project → Deploy from GitHub
3. **选择仓库**: NDX
4. **配置**:
   - Root Directory: `Web/backend`
   - Start Command: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
   - 添加环境变量:
     - `SECRET_KEY`: 生成一个32位随机字符串
     - `DATABASE_URL`: Railway会自动提供PostgreSQL

### 选项B: 使用Render

1. **访问**: https://render.com
2. **新建Web Service**
3. **连接仓库**: NDX
4. **配置**:
   - Root Directory: `Web/backend`
   - Build Command: `pip install -r requirements.txt`
   - Start Command: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`

### 选项C: 使用Fly.io

```bash
# 安装Fly CLI
powershell -Command "irm https://fly.io/install.ps1 | iex"

# 登录
fly auth login

# 进入后端目录
cd Web/backend

# 初始化
fly launch

# 部署
fly deploy
```

## 步骤4: 更新前端API地址

部署后端后,获取后端URL,然后:

1. **在Vercel项目设置中**:
   - Settings → Environment Variables
   - 更新 `VITE_API_BASE_URL` 为后端URL
   - 例如: `https://your-app.railway.app`

2. **重新部署前端**:
   - Deployments → 最新部署 → Redeploy

## 步骤5: 配置CORS

在后端 `.env` 中添加前端域名:

```env
CORS_ORIGINS=https://your-app.vercel.app
```

## 访问应用

- 前端: `https://your-app.vercel.app`
- 后端: `https://your-backend.railway.app`

## 本地测试

```bash
# 测试前端
cd Web/frontend
npm run build
npm run preview

# 测试后端
cd Web/backend
python run.py
```

## 常见问题

### Q: API请求失败?
A: 检查CORS配置,确保前端域名在后端白名单中

### Q: 数据库连接问题?
A: Vercel不支持SQLite,后端需要使用PostgreSQL或MySQL

### Q: 环境变量不生效?
A: 确保变量名以 `VITE_` 开头,重新构建项目

## 注意事项

⚠️ **SQLite限制**: Vercel和大多数云平台不支持SQLite文件数据库
- 推荐使用: PostgreSQL, MySQL
- 或使用: PlanetScale, Neon, Supabase (免费PostgreSQL)

⚠️ **文件存储**: Vercel是无状态的,不能保存用户上传的文件
- 推荐使用: Cloudflare R2, AWS S3, Vercel Blob

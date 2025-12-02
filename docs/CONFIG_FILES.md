# 配置文件说明

## ✅ 保留的配置文件

### Backend (Web/backend/)

#### `railway.toml` - Railway部署配置 ✅
```toml
[build]
builder = "nixpacks"  # 使用Nixpacks构建

[deploy]
startCommand = "uvicorn app.main:app --host 0.0.0.0 --port $PORT"
restartPolicyType = "on_failure"
restartPolicyMaxRetries = 10
```
**作用**: Railway平台的部署配置
**必须保留**: ✅ Railway部署需要

---

#### `.env` - 环境变量配置 ✅
包含:
- `DATABASE_URL`: PostgreSQL连接字符串
- `SECRET_KEY`: JWT加密密钥
- `ADMIN_EMAIL/PASSWORD/USERNAME`: 管理员账户
- `CORS_ORIGINS`: 允许的前端域名

**作用**: 本地开发和生产环境的实际配置
**必须保留**: ✅ 应用运行必需
**安全**: ✅ 已在.gitignore中,不会提交到Git

---

#### `requirements.txt` - Python依赖 ✅
**作用**: 定义后端Python包依赖
**必须保留**: ✅ Railway安装依赖需要

---

#### `runtime.txt` - Python版本 ✅
```
python-3.11.6
```
**作用**: 指定Python运行时版本
**必须保留**: ✅ Railway构建需要

---

### Frontend (Web/frontend/)

#### `.env.development` - 本地开发配置 ✅
```env
VITE_API_BASE_URL=http://localhost:8000
```
**作用**: 本地开发时指向本地后端
**必须保留**: ✅ 本地开发需要

---

#### `.env.production` - 生产环境配置 ✅
```env
VITE_API_BASE_URL=https://ndx-production.up.railway.app
```
**作用**: 生产构建时指向Railway后端
**必须保留**: ✅ Vercel部署需要

---

#### `vercel.json` - Vercel部署配置 ✅
```json
{
  "buildCommand": "npm run build",
  "outputDirectory": "dist",
  "framework": "vite",
  "env": {
    "VITE_API_BASE_URL": "https://ndx-production.up.railway.app"
  },
  "rewrites": [...]  // SPA路由支持
}
```
**作用**: Vercel平台的构建和部署配置
**必须保留**: ✅ Vercel部署需要

---

#### `vite.config.ts` - Vite构建配置 ✅
```ts
export default defineConfig({
  plugins: [react()],
  server: {
    port: 3000,
    proxy: {
      '/api': {
        target: 'http://localhost:8000',
        changeOrigin: true,
      },
    },
  },
})
```
**作用**: 
- 开发服务器配置
- API代理设置(解决CORS)
- React插件配置

**必须保留**: ✅ Vite构建需要

---

#### `tsconfig.json` - TypeScript主配置 ✅
**作用**: TypeScript编译器配置
**必须保留**: ✅ TypeScript项目必需

---

#### `tsconfig.node.json` - Vite配置的TS设置 ✅
```json
{
  "compilerOptions": {
    "composite": true,
    "module": "ESNext",
    "moduleResolution": "bundler"
  },
  "include": ["vite.config.ts"]
}
```
**作用**: 专门用于编译vite.config.ts文件
**必须保留**: ✅ Vite需要

---

#### `package.json` - 项目依赖和脚本 ✅
```json
{
  "scripts": {
    "dev": "vite",
    "build": "vite build",
    "preview": "vite preview"
  },
  "dependencies": {...},
  "devDependencies": {...}
}
```
**作用**: 
- NPM包依赖管理
- 构建脚本定义
- 项目元数据

**必须保留**: ✅ Node.js项目必需

---

#### `tailwind.config.js` - Tailwind CSS配置 ✅
**作用**: Tailwind CSS样式框架配置
**必须保留**: ✅ 前端样式需要

---

#### `postcss.config.js` - PostCSS配置 ✅
**作用**: CSS处理器配置(Tailwind依赖)
**必须保留**: ✅ Tailwind需要

---

## ❌ 已删除的过时文件

### Backend
- ❌ `fund.db` - SQLite数据库(已迁移到PostgreSQL)
- ❌ `ndx_users.db` - SQLite数据库(已迁移到PostgreSQL)
- ❌ `.env.example` - 示例文件(含过时的SQLite配置)
- ❌ `Procfile` - Heroku配置(Railway不需要)
- ❌ `railway.json` - 旧格式(已用railway.toml替代)

### Root
- ❌ `.env.example` - 已删除(直接使用实际.env)

---

## 📝 配置文件更新记录

### Backend `.env` 已同步Railway配置 ✅
包含所有Railway环境变量:
- ✅ DATABASE_URL (PostgreSQL内部地址)
- ✅ SECRET_KEY (JWT密钥)
- ✅ ADMIN_* (管理员信息)
- ✅ CORS_ORIGINS (前端地址)

### Frontend 环境变量已配置 ✅
- ✅ `.env.development` → 本地后端
- ✅ `.env.production` → Railway后端
- ✅ `vercel.json` → Railway后端

---

## 🎯 总结

**保留文件数**: 13个配置文件
**删除文件数**: 6个过时文件

**所有保留的配置文件都是必需的**:
- Backend: Railway部署、环境变量、Python依赖
- Frontend: Vercel部署、Vite构建、TypeScript编译、样式配置

**没有冗余配置文件** ✅

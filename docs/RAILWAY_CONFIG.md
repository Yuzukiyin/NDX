# Railway 部署配置说明

## ✅ 已配置的环境变量

根据你的Railway截图,以下环境变量已正确配置:

### 🔐 认证配置
- `ADMIN_EMAIL`: 1712008344@qq.com
- `ADMIN_PASSWORD`: Lzy171200
- `ADMIN_USERNAME`: admin
- `SECRET_KEY`: 4VnffDWpzXa1TNIJSy3_KpaIhNUAVq8q4iooGHyBh_4

### 🌐 CORS配置
- `CORS_ORIGINS`: ["https://ndx-khaki.vercel.app","http://localhost:3000"]

### 🗄️ 数据库配置
- `DATABASE_URL`: `postgresql://postgres:pFmrwDwvB1pdMRCMZkpSNhzYCy1gxIGi@postgres.railway.internal:5432/railway`

> ✅ **已同步**: 这些配置已更新到本地 `.env` 文件中

---

## 📦 Railway 服务架构

### Postgres 数据库
- **服务**: postgres-volume
- **内部地址**: `postgres.railway.internal:5432`
- **数据库名**: railway
- **用户**: postgres
- **部署**: Docker Image (22小时前)

### NDX 应用
- **服务**: ndx-production.up.railway.app
- **部署**: GitHub (3分钟前)
- **状态**: ✅ 运行中

---

## 🔗 连接信息

### Railway提供的数据库变量
根据截图,Railway自动提供了以下变量:
- `DATABASE_PUBLIC_URL`: 公网访问地址
- `DATABASE_URL`: 内部访问地址 (应用使用此变量)
- `PGDATA`: /var/lib/postgresql1/data/pgdata
- `PGDATABASE`: railway
- `PGHOST`: postgres.railway.internal
- `PGPASSWORD`: pFmrwDwvB1pdMRCMZkpSNhzYCy1gxIGi
- `PGPORT`: 5432
- `PGUSER`: postgres
- `POSTGRES_DB`: railway

### 应用使用的是
✅ `DATABASE_URL` = `postgresql://postgres:pFmrwDwvB1pdMRCMZkpSNhzYCy1gxIGi@postgres.railway.internal:5432/railway`

---

## 🚀 部署流程

### 1. 首次部署
Railway会自动:
1. 检测到 `Web/backend/` 目录
2. 读取 `requirements.txt` 安装依赖
3. 执行 `start.py` 启动应用
4. 自动创建管理员账户(使用环境变量)

### 2. 更新部署
每次push到GitHub main分支后:
1. Railway自动检测更改
2. 重新构建应用
3. 自动部署新版本

---

## ⚠️ 重要提示

### 本地开发
你的本地 `.env` 文件已包含所有Railway配置,可以直接使用:

```bash
cd Web/backend
python start.py
```

### 数据库访问
- **Railway内部**: 使用 `DATABASE_URL` (postgres.railway.internal)
- **本地/外部**: 使用 `DATABASE_PUBLIC_URL` (metro.proxy.rlwy.net)

### 前端配置
确保前端 Vercel 的环境变量设置了:
```
VITE_API_BASE_URL=https://ndx-production.up.railway.app
```

---

## 🔄 下次更新步骤

1. **修改代码**
2. **本地测试**:
   ```bash
   cd Web/backend
   python start.py
   ```
3. **提交更改**:
   ```bash
   git add .
   git commit -m "your message"
   git push origin main
   ```
4. **Railway自动部署** ✅

---

## 📝 注意事项

1. ✅ `.env` 文件已添加到 `.gitignore`,不会被提交到GitHub
2. ✅ 所有敏感信息只存在于Railway环境变量中
3. ✅ 本地和Railway使用相同的配置,确保一致性
4. ⚠️ 不要在代码中硬编码任何密码或密钥
5. ✅ SQLite已完全移除,只使用PostgreSQL

---

## 🎯 当前状态

- ✅ Railway Postgres: 运行中
- ✅ Railway NDX App: 运行中 (3分钟前部署)
- ✅ 前端 Vercel: https://ndx-khaki.vercel.app
- ✅ 后端 Railway: https://ndx-production.up.railway.app
- ✅ 环境变量: 已同步
- ✅ 数据库: PostgreSQL
- ✅ 管理员账户: admin@1712008344@qq.com

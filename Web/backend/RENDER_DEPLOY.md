# Render 部署指南（无需信用卡）

## ✨ 为什么选择 Render

- ✅ **完全免费**: 无需信用卡，注册即用
- ✅ **永久使用**: 免费套餐无时间限制
- ✅ **PostgreSQL**: 免费提供 100MB PostgreSQL 数据库
- ⚠️ **冷启动**: 15 分钟无访问会休眠，首次访问需 30 秒启动

---

## 🚀 部署步骤（10 分钟完成）

### 第 1 步: 推送代码到 GitHub

```powershell
cd d:\AAAStudy\NDX
git add .
git commit -m "Add Render deployment support"
git push
```

### 第 2 步: 注册 Render

1. 访问: https://render.com
2. 点击 "Get Started"
3. 选择 "Sign up with GitHub"
4. 授权 Render 访问你的 GitHub

### 第 3 步: 创建 PostgreSQL 数据库

1. 在 Render Dashboard，点击 "New +"
2. 选择 "PostgreSQL"
3. 配置:
   - Name: `ndx-database`
   - Database: `ndx_fund` (自动生成)
   - User: `ndx_fund_user` (自动生成)
   - Region: 选择 **Oregon (US West)** (离中国最近)
   - Instance Type: 选择 **Free**
4. 点击 "Create Database"
5. **等待 2-3 分钟**数据库创建完成
6. 创建完成后，进入数据库页面，找到 "Internal Database URL"
7. **复制这个 URL**（格式: `postgres://user:pass@host/db`）

### 第 4 步: 部署后端服务

1. 返回 Dashboard，点击 "New +" → "Web Service"
2. 选择 "Build and deploy from a Git repository"
3. 点击 "Connect" 你的 GitHub 账号
4. 选择 `NDX` 仓库
5. 点击 "Connect"

#### 配置服务:

**Basic 设置**:
- Name: `ndx-backend`
- Region: **Oregon (US West)** (与数据库同一区域)
- Branch: `main`
- Root Directory: `Web/backend`
- Runtime: **Python 3**
- Build Command: `pip install -r requirements.txt`
- Start Command: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`

**Instance Type**:
- 选择 **Free**

#### 环境变量 (Environment Variables):

点击 "Add Environment Variable"，添加以下变量:

```env
# 必需的环境变量
SECRET_KEY=生成的密钥见下方
DATABASE_URL=刚才复制的PostgreSQL Internal URL
CORS_ORIGINS=https://ndx-khaki.vercel.app
```

**生成 SECRET_KEY**:
```powershell
python -c "import secrets; print(secrets.token_urlsafe(32))"
# 输出: 4VnffDWpzXaITNIJSy3_KpaIhNUAVq8q4iooGHyBh_4
```

将生成的密钥填入 `SECRET_KEY`。

**重要**: `DATABASE_URL` 必须使用第 3 步复制的 PostgreSQL URL！

6. 点击 "Create Web Service"
7. **等待 5-10 分钟**构建和部署

### 第 5 步: 初始化数据库

部署成功后，需要创建管理员账户：

#### 方式 1: 使用 Render Shell（推荐）

1. 在你的 Web Service 页面，点击顶部的 "Shell" 标签
2. 等待 Shell 加载完成
3. 运行:
   ```bash
   python init_admin.py
   ```
4. 看到 "✅ 管理员账户创建成功" 即可

#### 方式 2: 使用 API 直接创建（备选）

访问你的后端 API 文档页面手动注册：
- URL: `https://ndx-backend.onrender.com/docs`
- 找到 `/api/auth/register` 接口
- 点击 "Try it out"
- 填写:
  ```json
  {
    "email": "1712008344@qq.com",
    "username": "admin",
    "password": "Lzy171200"
  }
  ```
- 点击 "Execute"

### 第 6 步: 获取后端 URL

部署成功后:
1. 在 Web Service 页面顶部，找到你的服务 URL
2. 格式: `https://ndx-backend.onrender.com`
3. **复制这个 URL**

### 第 7 步: 更新 Vercel 前端

1. 访问 https://vercel.com
2. 进入你的项目 `NDX`
3. 点击 "Settings" → "Environment Variables"
4. 添加/更新变量:
   ```
   名称: VITE_API_BASE_URL
   值: https://ndx-backend.onrender.com
   ```
5. 保存后，点击 "Deployments" 标签
6. 找到最新的部署，点击右侧的 "⋮" → "Redeploy"
7. 等待 2-3 分钟重新部署完成

### 第 8 步: 测试应用 🎉

1. 访问你的前端: https://ndx-khaki.vercel.app
2. 登录:
   - 邮箱: `1712008344@qq.com`
   - 密码: `Lzy171200`
3. 成功！🎊

---

## 🔧 常见问题

### Q1: 为什么登录后看不到基金数据？

A: **这是正常的！** 因为你现在使用的是全新的 PostgreSQL 数据库，需要导入数据：

#### 导入已有数据的方法:

**方式 1: 使用 Shell 导入 CSV**
```bash
# 在 Render Shell 中
python -c "
from app.services.fund_service import FundService
service = FundService(user_id=1)
service.import_transactions_from_csv('../../../transactions.csv')
"
```

**方式 2: 在本地准备数据**
你可以先在本地使用原来的 `fund.db`，然后通过 API 逐步添加数据。

### Q2: 服务响应很慢怎么办？

A: Render 免费版会在 15 分钟无访问后休眠，首次访问需要 30 秒启动。

**解决方案**:
- 使用定时 Ping 服务保持唤醒（如 UptimeRobot, cron-job.org）
- 升级到付费版（$7/月，无休眠）
- 或者继续使用 Railway（需要信用卡验证）

### Q3: 数据库空间不够怎么办？

A: Render 免费版提供 100MB PostgreSQL 空间，对于基金管理够用。

如果不够:
- 定期清理历史数据
- 升级到付费版（$7/月，10GB 空间）

### Q4: 如何查看日志？

1. 进入 Web Service 页面
2. 点击 "Logs" 标签
3. 实时查看运行日志

### Q5: 如何更新代码？

```powershell
# 本地修改代码后
git add .
git commit -m "Update code"
git push

# Render 会自动检测并重新部署
```

### Q6: 用户数据隔离怎么办？

当前代码已支持:
- 管理员 (user_id=1) 使用主数据库
- 其他用户数据存储在 PostgreSQL 中（通过 JSON 或单独表）

如果需要完整的 SQLite 文件隔离，建议使用 Railway。

---

## 📊 Render vs Railway 对比

| 特性 | Render (免费) | Railway (免费) |
|------|--------------|---------------|
| 需要信用卡 | ❌ 不需要 | ✅ 需要 |
| 数据库 | PostgreSQL (100MB) | SQLite + PostgreSQL |
| 冷启动 | 有 (30秒) | 无 |
| 运行时间 | 750小时/月 | 500小时/月 ($5) |
| 国内访问 | 较慢 | 较快 |
| 适合场景 | 学习/演示 | 生产环境 |

---

## 🎯 下一步优化建议

1. **添加定时任务**: 每 10 分钟 Ping 一次，避免休眠
   ```bash
   # 使用 https://uptimerobot.com
   # 添加监控: https://ndx-backend.onrender.com/api/health
   ```

2. **配置自定义域名**: 
   - Render 支持免费绑定自定义域名
   - Settings → Custom Domains

3. **启用 HTTPS**: Render 自动提供免费 SSL 证书

4. **监控性能**: 
   - Dashboard 查看请求量
   - Logs 查看错误日志

---

## 💡 成本说明

- **Render 免费版**: $0/月
  - 750 小时运行时间
  - 100MB PostgreSQL
  - 有冷启动延迟

- **Render 付费版**: $7/月
  - 无限运行时间
  - 无冷启动
  - 10GB PostgreSQL

**学生建议**: 
- 学习阶段用 Render 免费版
- 正式使用找家长借信用卡用 Railway
- 或等以后有收入再升级

---

## 📞 需要帮助？

如果部署过程中遇到问题:

1. 检查 Render Logs 查看错误信息
2. 确认环境变量设置正确
3. 测试 API: `https://你的域名.onrender.com/docs`
4. 检查 PostgreSQL 连接状态

祝部署顺利！🚀

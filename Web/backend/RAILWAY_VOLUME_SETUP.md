# Railway 持久化配置指南

## 问题原因

Railway 容器使用的是**临时文件系统**，每次重启后数据会丢失。需要使用 **Volume** 来持久化数据库和配置文件。

## 立即配置步骤

### 1. 添加 Volume（重要！）

1. 进入 Railway Dashboard
2. 选择你的 NDX 后端服务
3. 点击 **"Settings"** 标签
4. 向下滚动找到 **"Volumes"** 部分
5. 点击 **"New Volume"**
6. 设置：
   - **Mount Path**: `/app/data`
   - **Size**: 1 GB（足够使用）
7. 点击 **"Add"**

### 2. 上传配置文件到 Volume

等待部署完成后，使用 Railway CLI 上传配置文件：

```powershell
# 在本地执行
cd d:\AAAStudy\NDX\Web\backend

# 确保已登录
railway login

# 链接项目
railway link

# 上传配置文件到 Volume
railway run bash -c "mkdir -p /app/data && cp auto_invest_setting.json /app/data/"
```

### 3. 重新部署

添加 Volume 后，Railway 会自动重新部署。等待部署完成。

### 4. 验证配置

部署完成后测试：

1. 登录系统
2. 点击「抓取历史净值」- 应该能成功抓取
3. 点击「更新待确认交易」- 应该能填充净值
4. 重启服务 - 数据应该保留

## 检查 Volume 是否生效

使用 Railway CLI：

```powershell
# 查看数据库文件
railway run ls -lh /app/data/

# 查看数据库内容
railway run sqlite3 /app/data/ndx_users.db "SELECT COUNT(*) FROM fund_nav_history;"
```

## 已修改的配置

1. **railway.toml**: 定义 Volume 挂载点 `/app/data`
2. **config.py**: 数据库路径改为 `/app/data/ndx_users.db`
3. **fund_service.py**: 使用统一的配置文件路径查找逻辑

## 环境变量（可选）

如果需要覆盖默认路径，可以在 Railway Settings → Variables 中添加：

```
DATABASE_URL=sqlite+aiosqlite:////app/data/ndx_users.db
AUTO_INVEST_CONFIG_PATH=/app/data/auto_invest_setting.json
```

## 故障排查

### 数据仍然丢失？

检查 Volume 是否正确挂载：
```powershell
railway run df -h | grep /app/data
```

### 配置文件找不到？

检查文件是否存在：
```powershell
railway run cat /app/data/auto_invest_setting.json
```

如果不存在，重新上传：
```powershell
railway run bash -c "cat > /app/data/auto_invest_setting.json << 'EOF'
{
  \"plans\": [
    {
      \"plan_name\": \"纳指100定投计划\",
      \"fund_code\": \"021000\",
      \"fund_name\": \"南方纳斯达克100指数A\",
      \"amount\": 30.0,
      \"frequency\": \"每周四\",
      \"start_date\": \"2025-11-21\",
      \"end_date\": \"2099-12-31\",
      \"enabled\": true
    },
    {
      \"plan_name\": \"纳指100ETF联接定投\",
      \"fund_code\": \"270042\",
      \"fund_name\": \"广发纳斯达克100ETF联接A人民币\",
      \"amount\": 10.0,
      \"frequency\": \"每周四\",
      \"start_date\": \"2025-11-21\",
      \"end_date\": \"2099-12-31\",
      \"enabled\": true
    }
  ]
}
EOF"
```

## 预期结果

配置完成后：
- ✅ 数据库数据持久化，重启不丢失
- ✅ 历史净值正常抓取
- ✅ 交易记录永久保存
- ✅ 定投计划配置生效

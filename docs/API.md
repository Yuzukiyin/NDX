# API文档

## 基础信息

- **Base URL**: `https://your-app.railway.app` (生产) 或 `http://localhost:8000` (开发)
- **认证方式**: JWT Bearer Token
- **数据格式**: JSON

## 认证端点

### 注册用户
```http
POST /auth/register
Content-Type: application/json

{
  "email": "user@example.com",
  "username": "username",
  "password": "password123"
}
```

响应：
```json
{
  "access_token": "eyJ...",
  "refresh_token": "eyJ...",
  "token_type": "bearer",
  "user": {
    "id": 1,
    "email": "user@example.com",
    "username": "username"
  }
}
```

### 登录
```http
POST /auth/login
Content-Type: application/json

{
  "email": "user@example.com",
  "password": "password123"
}
```

### 刷新Token
```http
POST /auth/refresh
Authorization: Bearer <refresh_token>
```

### 获取当前用户
```http
GET /auth/me
Authorization: Bearer <access_token>
```

## 定投计划端点

### 获取所有定投计划
```http
GET /auto-invest/plans
Authorization: Bearer <access_token>
```

响应：
```json
[
  {
    "id": 1,
    "plan_name": "沪深300定投",
    "fund_code": "000001",
    "fund_name": "华夏成长",
    "amount": 1000.0,
    "frequency": "monthly",
    "start_date": "2024-01-01",
    "end_date": "2025-12-31",
    "enabled": true,
    "user_id": 1
  }
]
```

### 创建定投计划
```http
POST /auto-invest/plans
Authorization: Bearer <access_token>
Content-Type: application/json

{
  "plan_name": "沪深300定投",
  "fund_code": "000001",
  "fund_name": "华夏成长",
  "amount": 1000.0,
  "frequency": "monthly",
  "start_date": "2024-01-01",
  "end_date": "2025-12-31",
  "enabled": true
}
```

频率选项：
- `daily` - 每日
- `weekly` - 每周
- `monthly` - 每月
- `quarterly` - 每季度

### 更新定投计划
```http
PUT /auto-invest/plans/{plan_id}
Authorization: Bearer <access_token>
Content-Type: application/json

{
  "amount": 1500.0,
  "enabled": false
}
```

### 删除定投计划
```http
DELETE /auto-invest/plans/{plan_id}
Authorization: Bearer <access_token>
```

## 基金数据端点

### 获取基金列表
```http
GET /funds
Authorization: Bearer <access_token>
```

响应：
```json
[
  {
    "fund_code": "000001",
    "fund_name": "华夏成长",
    "latest_nav": 1.5000,
    "latest_date": "2024-12-01"
  }
]
```

### 获取基金详情
```http
GET /funds/{fund_code}
Authorization: Bearer <access_token>
```

### 获取基金净值历史
```http
GET /funds/{fund_code}/nav-history?start_date=2024-01-01&end_date=2024-12-31
Authorization: Bearer <access_token>
```

响应：
```json
[
  {
    "price_date": "2024-01-01",
    "unit_nav": 1.5000,
    "cumulative_nav": 2.0000,
    "daily_growth_rate": 0.5
  }
]
```

### 手动更新基金净值
```http
POST /funds/{fund_code}/update-nav
Authorization: Bearer <access_token>
Content-Type: application/json

{
  "start_date": "2024-01-01",
  "end_date": "2024-12-31"
}
```

## 交易记录端点

### 获取交易记录
```http
GET /transactions?fund_code=000001&start_date=2024-01-01&end_date=2024-12-31
Authorization: Bearer <access_token>
```

查询参数：
- `fund_code` (可选): 基金代码
- `start_date` (可选): 开始日期 YYYY-MM-DD
- `end_date` (可选): 结束日期 YYYY-MM-DD
- `transaction_type` (可选): 买入/卖出
- `skip` (可选): 分页跳过数量，默认0
- `limit` (可选): 分页限制数量，默认100

响应：
```json
{
  "total": 100,
  "transactions": [
    {
      "id": 1,
      "fund_code": "000001",
      "fund_name": "华夏成长",
      "transaction_date": "2024-01-01",
      "nav_date": "2024-01-02",
      "transaction_type": "买入",
      "shares": 100.00,
      "unit_nav": 1.5000,
      "amount": 150.00,
      "note": "定投"
    }
  ]
}
```

### 添加交易记录
```http
POST /transactions
Authorization: Bearer <access_token>
Content-Type: application/json

{
  "fund_code": "000001",
  "transaction_date": "2024-01-01",
  "transaction_type": "买入",
  "amount": 1000.0,
  "note": "定投"
}
```

注：系统会自动查询净值并计算份额

### 批量导入交易
```http
POST /transactions/import
Authorization: Bearer <access_token>
Content-Type: multipart/form-data

file: transactions.csv
```

CSV格式：
```csv
fund_code,transaction_date,transaction_type,amount,note
000001,2024-01-01,买入,1000,定投
```

### 获取持仓统计
```http
GET /transactions/holdings
Authorization: Bearer <access_token>
```

响应：
```json
[
  {
    "fund_code": "000001",
    "fund_name": "华夏成长",
    "total_shares": 1000.00,
    "total_cost": 15000.00,
    "average_cost": 1.5000,
    "current_nav": 1.6000,
    "current_value": 16000.00,
    "profit": 1000.00,
    "profit_rate": 6.67
  }
]
```

### 获取收益曲线
```http
GET /transactions/profit-curve?start_date=2024-01-01&end_date=2024-12-31
Authorization: Bearer <access_token>
```

响应：
```json
[
  {
    "date": "2024-01-01",
    "total_cost": 1000.00,
    "total_value": 1050.00,
    "total_profit": 50.00,
    "profit_rate": 5.00
  }
]
```

## 工具端点

### 健康检查
```http
GET /health
```

响应：
```json
{
  "status": "healthy",
  "version": "1.0.0"
}
```

### 更新待确认交易
```http
POST /tools/update-pending
Authorization: Bearer <access_token>
```

处理所有净值未确认的交易记录

### 同步定投交易
```http
POST /tools/sync-auto-invest
Authorization: Bearer <access_token>
Content-Type: application/json

{
  "start_date": "2024-01-01",
  "end_date": "2024-12-31"
}
```

根据定投计划生成交易记录

## 错误响应

所有端点可能返回以下错误：

### 400 Bad Request
```json
{
  "detail": "Invalid request parameters"
}
```

### 401 Unauthorized
```json
{
  "detail": "Could not validate credentials"
}
```

### 403 Forbidden
```json
{
  "detail": "Not enough permissions"
}
```

### 404 Not Found
```json
{
  "detail": "Resource not found"
}
```

### 422 Validation Error
```json
{
  "detail": [
    {
      "loc": ["body", "email"],
      "msg": "field required",
      "type": "value_error.missing"
    }
  ]
}
```

### 500 Internal Server Error
```json
{
  "detail": "Internal server error"
}
```

## 速率限制

- 认证端点: 10请求/分钟
- 其他端点: 100请求/分钟

超过限制返回 429 Too Many Requests

## 测试工具

### 使用curl
```bash
# 登录获取token
TOKEN=$(curl -X POST http://localhost:8000/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"user@example.com","password":"password"}' \
  | jq -r '.access_token')

# 使用token调用API
curl http://localhost:8000/auto-invest/plans \
  -H "Authorization: Bearer $TOKEN"
```

### 使用Python
```python
import requests

# 登录
response = requests.post(
    "http://localhost:8000/auth/login",
    json={"email": "user@example.com", "password": "password"}
)
token = response.json()["access_token"]

# 调用API
headers = {"Authorization": f"Bearer {token}"}
response = requests.get(
    "http://localhost:8000/auto-invest/plans",
    headers=headers
)
plans = response.json()
```

### 使用FastAPI Swagger UI
访问 `http://localhost:8000/docs` 查看交互式API文档

## WebSocket (未来功能)

计划支持实时净值推送：
```javascript
const ws = new WebSocket('ws://localhost:8000/ws/nav-updates');
ws.onmessage = (event) => {
  const data = JSON.parse(event.data);
  console.log('净值更新:', data);
};
```

## Webhooks (未来功能)

计划支持配置webhook接收事件通知：
- 定投执行完成
- 净值更新
- 收益达标提醒

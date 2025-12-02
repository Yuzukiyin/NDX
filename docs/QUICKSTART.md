# 快速开始指南

## 5分钟快速体验

### 前置条件
- ✅ Python 3.10+
- ✅ Node.js 18+
- ✅ Git

### Step 1: 克隆项目
```bash
git clone https://github.com/Yuzukiyin/NDX.git
cd NDX
```

### Step 2: 后端设置（约2分钟）

#### 2.1 创建conda环境
```bash
conda create -n NDX python=3.10
conda activate NDX
```

#### 2.2 安装依赖
```bash
cd Web/backend
pip install -r requirements.txt
```

#### 2.3 配置环境变量
```bash
# Windows
copy .env.example .env

# macOS/Linux  
cp .env.example .env
```

编辑 `.env` 文件：
```bash
# 使用SQLite快速开始（生产环境用PostgreSQL）
DATABASE_URL=sqlite+aiosqlite:///./ndx.db

# 修改密钥（重要！）
SECRET_KEY=your-random-secret-key-here

# 管理员账号
ADMIN_EMAIL=admin@example.com
ADMIN_PASSWORD=admin123
ADMIN_USERNAME=admin
```

#### 2.4 初始化数据库
```bash
python init_admin.py
```

#### 2.5 启动后端
```bash
python start.py
```

✅ 后端已启动: http://localhost:8000

### Step 3: 前端设置（约2分钟）

打开新终端：

#### 3.1 安装依赖
```bash
cd Web/frontend
npm install
```

#### 3.2 配置环境
创建 `.env` 文件：
```bash
VITE_API_URL=http://localhost:8000
```

#### 3.3 启动前端
```bash
npm run dev
```

✅ 前端已启动: http://localhost:5173

### Step 4: 登录系统

1. 访问 http://localhost:5173
2. 使用管理员账号登录：
   - 邮箱: `admin@example.com`
   - 密码: `admin123`

### Step 5: 添加第一个定投计划

1. 进入"定投计划"页面
2. 点击"添加计划"
3. 填写信息：
   - 计划名称: `沪深300定投`
   - 基金代码: `000001`
   - 基金名称: `华夏成长`
   - 投资金额: `1000`
   - 定投频率: `每月`
   - 开始日期: `2024-01-01`
4. 保存

### Step 6: 抓取净值数据

1. 进入"工具"页面
2. 点击"同步净值数据"
3. 等待抓取完成（约30秒）

✅ 恭喜！系统已成功运行

## 下一步

### 导入历史交易

创建 `transactions.csv`：
```csv
fund_code,transaction_date,transaction_type,amount,note
000001,2024-01-01,买入,1000,定投
000001,2024-02-01,买入,1000,定投
```

通过"工具"页面导入

### 查看持仓分析

进入"交易记录"页面，查看：
- 持仓明细
- 收益统计
- 收益曲线图

### 设置定时任务（可选）

#### Windows任务计划程序
```cmd
schtasks /create /tn "NDX同步净值" /tr "conda activate NDX && python scripts/sync_nav_data.py" /sc daily /st 09:00
```

#### macOS/Linux crontab
```bash
# 每天9:00执行
0 9 * * * conda activate NDX && python /path/to/NDX/scripts/sync_nav_data.py
```

## 生产环境部署

参考详细文档：
- [部署指南](./DEPLOYMENT.md)
- [开发文档](./DEVELOPMENT.md)

快速部署步骤：

### 1. Railway后端部署
1. 访问 https://railway.app
2. 连接GitHub仓库
3. 添加PostgreSQL服务
4. 设置环境变量
5. 自动部署完成

### 2. Vercel前端部署
1. 访问 https://vercel.com
2. 导入GitHub仓库
3. 设置 `VITE_API_URL`
4. 自动部署完成

## 常见问题

### Q: 后端启动失败？
**A**: 检查：
1. Python版本是否3.10+
2. 所有依赖是否安装：`pip list`
3. DATABASE_URL是否正确
4. 端口8000是否被占用

### Q: 前端无法连接后端？
**A**: 检查：
1. 后端是否启动
2. VITE_API_URL是否正确
3. CORS配置是否包含前端域名
4. 浏览器控制台错误信息

### Q: 净值数据抓取失败？
**A**: 可能原因：
1. 网络连接问题
2. 基金代码错误
3. fundSpider需要更新
4. 查看后端日志详细错误

### Q: 如何重置系统？
**A**: 
```bash
# 方法1: 使用数据库管理工具
python scripts/db_manager.py
# 选择选项5

# 方法2: 手动删除数据库
rm ndx.db
python init_admin.py
```

### Q: 忘记管理员密码？
**A**:
```bash
# 重置密码
python scripts/db_manager.py
# 选择选项2创建新管理员
```

## 性能优化建议

### 本地开发
- 使用SQLite快速测试
- 限制净值数据日期范围
- 定期清理测试数据

### 生产环境
- 使用PostgreSQL
- 启用数据库索引
- 配置Redis缓存（可选）
- 使用CDN加速

## 获取帮助

### 文档
- [API文档](./API.md) - API端点详细说明
- [项目结构](./PROJECT_STRUCTURE.md) - 代码组织
- [数据库迁移](./DATABASE_MIGRATION.md) - 数据迁移指南

### 在线资源
- FastAPI文档: https://fastapi.tiangolo.com
- React文档: https://react.dev
- Railway文档: https://docs.railway.app
- Vercel文档: https://vercel.com/docs

### 社区支持
- GitHub Issues: https://github.com/Yuzukiyin/NDX/issues
- 提交Bug报告
- 功能建议

## 开发技巧

### 调试后端
```python
# 在代码中添加断点
import pdb; pdb.set_trace()

# 或使用VS Code调试
# 创建 .vscode/launch.json
```

### 调试前端
```javascript
// 浏览器DevTools
console.log('调试信息')

// React DevTools扩展
// 查看组件状态和Props
```

### 查看API文档
访问 http://localhost:8000/docs
- 交互式API测试
- 自动生成的文档
- 支持在线调试

## 贡献代码

欢迎提交PR！请遵循：
1. Fork仓库
2. 创建特性分支：`git checkout -b feature/xxx`
3. 提交改动：`git commit -m "feat: xxx"`
4. 推送分支：`git push origin feature/xxx`
5. 提交Pull Request

## 许可证

MIT License - 自由使用和修改

---

开始你的基金管理之旅吧！🚀

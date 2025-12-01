# 快速开始指南

## 5分钟快速启动

### Web应用

#### 1. 启动后端 (2分钟)
```bash
# 进入后端目录
cd Web\backend

# 创建并激活虚拟环境
python -m venv venv
venv\Scripts\activate

# 安装依赖
pip install -r requirements.txt

# 复制环境配置
copy .env.example .env

# 启动服务
python run.py
```

✅ 后端启动成功! 访问 http://localhost:8000

#### 2. 启动前端 (2分钟)
```bash
# 新开一个终端,进入前端目录
cd Web\frontend

# 安装依赖(首次需要)
npm install

# 启动开发服务器
npm run dev
```

✅ 前端启动成功! 访问 http://localhost:3000

#### 3. 开始使用 (1分钟)
1. 打开浏览器: http://localhost:3000
2. 点击"立即注册"
3. 填写信息(密码需8位+大小写+数字)
4. 登录后点击"初始化数据库"
5. 享受使用!

---

### Android应用

#### 准备工作
1. 安装 Android Studio Hedgehog+
2. 下载地址: https://developer.android.com/studio

#### 开发步骤
1. 打开Android Studio
2. File → Open → 选择 `Android/` 目录
3. 等待Gradle同步完成
4. 创建模拟器或连接真机
5. 点击运行按钮

---

## 关键配置

### 后端环境变量 (.env)
```bash
SECRET_KEY=your-secret-key-min-32-chars
DEBUG=True
DATABASE_URL=sqlite+aiosqlite:///./ndx_users.db
```

### Android API配置
```kotlin
// 模拟器
const val BASE_URL = "http://10.0.2.2:8000/api/"

// 真机(同WiFi)
const val BASE_URL = "http://192.168.x.x:8000/api/"
```

---

## 故障排除

### 问题: 后端启动失败
```bash
# 检查Python版本
python --version  # 需要3.10+

# 重新安装依赖
pip install --upgrade -r requirements.txt
```

### 问题: 前端无法连接
1. 确保后端运行在8000端口
2. 检查浏览器控制台错误
3. 尝试清除浏览器缓存

### 问题: Android无法连接后端
1. 确认API地址配置
2. 检查防火墙设置
3. 验证网络连接

---

## 下一步

- 📖 阅读完整文档: [README_PROJECT.md](./README_PROJECT.md)
- 🌐 Web详细文档: [Web/README.md](./Web/README.md)
- 📱 Android详细文档: [Android/README.md](./Android/README.md)
- 📚 API文档: http://localhost:8000/docs

---

## 需要帮助?

遇到问题请查看:
1. 各目录下的README文档
2. 常见问题章节
3. 在线文档资源

祝您使用愉快! 🎉

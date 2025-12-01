# NDX基金管理系统

一个现代化的全栈基金投资组合管理应用,支持Web端和Android端。

## ✨ 特性

- 🔐 **安全的用户认证** - JWT令牌 + 密码强度验证
- 📊 **实时数据展示** - 基金概览、交易记录、收益统计
- 📈 **图表可视化** - 历史净值走势图
- 🎨 **极简设计** - 圆角卡片 + 柔和阴影 + 弹性动画
- 📱 **多平台支持** - Web浏览器 + Android应用
- 🔄 **数据同步** - 自动抓取历史净值

## 🚀 快速开始

### Web应用

```bash
# 后端
cd Web/backend
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
python run.py

# 前端(新终端)
cd Web/frontend
npm install
npm run dev
```

访问: http://localhost:3000

### Android应用

1. 安装Android Studio
2. 打开 `Android/` 目录
3. 运行应用

详见: [快速开始指南](./QUICKSTART.md)

## 📁 项目结构

```
NDX/
├── Web/          # Web应用(FastAPI + React)
├── Android/      # Android应用(Kotlin + Compose)
└── 原有文件/      # 原NDX系统
```

## 🛠 技术栈

**后端**: FastAPI, SQLAlchemy, JWT

**前端**: React, TypeScript, TailwindCSS, Framer Motion

**移动端**: Kotlin, Jetpack Compose, Material 3

## 📖 文档

- [完整项目文档](./README_PROJECT.md)
- [Web应用文档](./Web/README.md)
- [Android应用文档](./Android/README.md)
- [快速开始](./QUICKSTART.md)

## 🎯 功能

- ✅ 用户注册登录
- ✅ 基金数据管理
- ✅ 交易记录查询
- ✅ 收益统计分析
- ✅ 历史净值图表
- ✅ 数据导入导出

## 📸 界面预览

极简主义设计 | 圆角卡片布局 | 弹性动画效果

## 📝 开发状态

- [x] Web后端API
- [x] Web前端界面
- [x] Android项目结构
- [ ] Android完整功能
- [ ] 部署文档
- [ ] 测试覆盖

## 🤝 贡献

欢迎提交Issue和Pull Request!

## 📄 许可证

MIT License

---

**开始使用**: 查看 [快速开始指南](./QUICKSTART.md) 仅需5分钟! 🚀

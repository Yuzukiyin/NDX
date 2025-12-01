# NDX基金管理系统 - Android应用开发指南

## 项目概述

NDX基金管理Android应用采用现代化的Android开发技术栈,包括:
- **Kotlin** - 主要编程语言
- **Jetpack Compose** - 声明式UI框架
- **Material 3** - UI设计系统
- **Retrofit** - 网络请求
- **Room** - 本地数据库
- **Hilt** - 依赖注入
- **Coroutines & Flow** - 异步编程

## 必需软件和工具

### 1. Android Studio
- 版本: Android Studio Hedgehog | 2023.1.1 或更高
- 下载地址: https://developer.android.com/studio
- 包含内容:
  - Android SDK
  - Android Emulator
  - Gradle构建工具
  - Kotlin插件

### 2. JDK (Java Development Kit)
- 版本: JDK 17 或更高
- Android Studio通常自带,无需单独安装

### 3. Android SDK
- 最低SDK版本: API 24 (Android 7.0)
- 目标SDK版本: API 34 (Android 14)
- 需要安装的组件:
  - Android SDK Platform 34
  - Android SDK Build-Tools 34.0.0
  - Android Emulator
  - Intel x86 Emulator Accelerator (HAXM installer)

## 项目结构

```
Android/
├── app/
│   ├── build.gradle.kts          # 应用级构建配置
│   └── src/
│       └── main/
│           ├── java/com/ndx/fundmanager/
│           │   ├── MainActivity.kt            # 主Activity
│           │   ├── ui/
│           │   │   ├── theme/                 # 主题配置
│           │   │   ├── screens/               # 屏幕组件
│           │   │   │   ├── LoginScreen.kt
│           │   │   │   ├── RegisterScreen.kt
│           │   │   │   ├── DashboardScreen.kt
│           │   │   │   ├── FundsScreen.kt
│           │   │   │   └── TransactionsScreen.kt
│           │   │   └── components/            # 可复用组件
│           │   ├── data/
│           │   │   ├── remote/                # 网络API
│           │   │   │   ├── ApiService.kt
│           │   │   │   └── dto/               # 数据传输对象
│           │   │   ├── local/                 # 本地数据库
│           │   │   │   └── AppDatabase.kt
│           │   │   └── repository/            # 数据仓库
│           │   ├── domain/
│           │   │   └── model/                 # 领域模型
│           │   ├── di/                        # 依赖注入
│           │   │   └── AppModule.kt
│           │   └── util/                      # 工具类
│           ├── AndroidManifest.xml
│           └── res/
│               ├── values/
│               │   ├── strings.xml
│               │   ├── colors.xml
│               │   └── themes.xml
│               └── drawable/                   # 图标资源
├── build.gradle.kts              # 项目级构建配置
├── settings.gradle.kts
└── gradle/
    └── libs.versions.toml        # 依赖版本管理
```

## 开发环境配置步骤

### 步骤1: 安装Android Studio
1. 下载Android Studio
2. 运行安装程序
3. 选择"Standard"安装类型
4. 等待SDK组件下载完成

### 步骤2: 创建项目
1. 打开Android Studio
2. 选择 "New Project"
3. 选择 "Empty Activity (Compose)"
4. 配置:
   - Name: NDX Fund Manager
   - Package name: com.ndx.fundmanager
   - Save location: D:\AAAStudy\NDX\Android
   - Language: Kotlin
   - Minimum SDK: API 24
   - Build configuration language: Kotlin DSL

### 步骤3: 配置依赖
在 `app/build.gradle.kts` 中添加以下依赖:

```kotlin
dependencies {
    // Compose BOM
    implementation(platform("androidx.compose:compose-bom:2023.10.01"))
    implementation("androidx.compose.ui:ui")
    implementation("androidx.compose.material3:material3")
    implementation("androidx.compose.ui:ui-tooling-preview")
    
    // Navigation
    implementation("androidx.navigation:navigation-compose:2.7.5")
    
    // Retrofit for networking
    implementation("com.squareup.retrofit2:retrofit:2.9.0")
    implementation("com.squareup.retrofit2:converter-gson:2.9.0")
    implementation("com.squareup.okhttp3:logging-interceptor:4.11.0")
    
    // Room for local database
    implementation("androidx.room:room-runtime:2.6.1")
    implementation("androidx.room:room-ktx:2.6.1")
    ksp("androidx.room:room-compiler:2.6.1")
    
    // Hilt for dependency injection
    implementation("com.google.dagger:hilt-android:2.48.1")
    kapt("com.google.dagger:hilt-compiler:2.48.1")
    implementation("androidx.hilt:hilt-navigation-compose:1.1.0")
    
    // Coroutines
    implementation("org.jetbrains.kotlinx:kotlinx-coroutines-android:1.7.3")
    
    // DataStore for preferences
    implementation("androidx.datastore:datastore-preferences:1.0.0")
    
    // Charts library
    implementation("com.patrykandpatrick.vico:compose:1.13.1")
    implementation("com.patrykandpatrick.vico:compose-m3:1.13.1")
}
```

### 步骤4: 配置权限
在 `AndroidManifest.xml` 中添加:

```xml
<uses-permission android:name="android.permission.INTERNET" />
<uses-permission android:name="android.permission.ACCESS_NETWORK_STATE" />
```

## 运行应用

### 使用模拟器
1. 在Android Studio中,点击 "Device Manager"
2. 点击 "Create Device"
3. 选择设备型号 (推荐: Pixel 6)
4. 选择系统镜像 (推荐: Android 13/API 33)
5. 完成创建
6. 点击绿色运行按钮启动应用

### 使用真机
1. 在手机上启用"开发者选项":
   - 设置 → 关于手机 → 连续点击"版本号"7次
2. 启用"USB调试"
3. 用USB线连接手机到电脑
4. 手机上允许USB调试授权
5. 在Android Studio选择你的设备并运行

## 后端API配置

在应用中需要配置后端API地址:

```kotlin
// app/src/main/java/com/ndx/fundmanager/data/remote/ApiService.kt
object ApiConfig {
    // 本地开发(使用模拟器)
    const val BASE_URL = "http://10.0.2.2:8000/api/"
    
    // 本地开发(使用真机,需要同一WiFi)
    // const val BASE_URL = "http://192.168.x.x:8000/api/"
    
    // 生产环境
    // const val BASE_URL = "https://your-domain.com/api/"
}
```

注意:
- 模拟器访问电脑localhost使用 `10.0.2.2`
- 真机需要使用电脑的局域网IP地址

## 设计规范

### 极简主义设计
- 大量留白空间
- 简洁的排版
- 最小化UI元素

### 圆角卡片
```kotlin
Card(
    shape = RoundedCornerShape(24.dp),
    elevation = CardDefaults.cardElevation(4.dp)
)
```

### 柔和阴影
```kotlin
elevation = CardDefaults.cardElevation(
    defaultElevation = 4.dp,
    pressedElevation = 8.dp
)
```

### 弹性动画
```kotlin
animateFloatAsState(
    targetValue = target,
    animationSpec = spring(
        dampingRatio = Spring.DampingRatioMediumBouncy,
        stiffness = Spring.StiffnessLow
    )
)
```

## 常见问题

### Q: 模拟器启动失败
A: 确保在BIOS中启用了虚拟化技术(VT-x/AMD-V)

### Q: Gradle同步失败
A: 
1. 检查网络连接
2. 使用国内镜像源(阿里云、腾讯云)
3. 在 `gradle.properties` 中添加代理配置

### Q: 应用无法连接后端
A: 
1. 确保后端服务已启动
2. 检查防火墙设置
3. 验证API地址配置

### Q: 编译错误
A:
1. Clean Project (Build → Clean Project)
2. Rebuild Project (Build → Rebuild Project)
3. Invalidate Caches (File → Invalidate Caches / Restart)

## 下一步

1. 阅读 `IMPLEMENTATION.md` 了解具体实现细节
2. 查看 `DESIGN_GUIDE.md` 了解UI设计规范
3. 运行示例代码熟悉开发流程

## 联系支持

遇到问题可以:
1. 查看Android官方文档: https://developer.android.com
2. Jetpack Compose文档: https://developer.android.com/jetpack/compose
3. Kotlin文档: https://kotlinlang.org/docs/home.html

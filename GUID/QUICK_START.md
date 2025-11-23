# 快速开始 - Windows EXE 打包

## 最快的方式（3步）

### 1️⃣ 打开命令提示符或 PowerShell

在项目目录中打开命令行工具

### 2️⃣ 运行打包脚本

**方式A：命令提示符（推荐）**
```bash
build_exe.bat
```

**方式B：PowerShell**
```powershell
.\build_exe.ps1
```

### 3️⃣ 等待打包完成

脚本会自动：
- ✓ 创建虚拟环境
- ✓ 安装所有依赖
- ✓ 打包成 EXE 文件

## 打包完成后

生成的文件位置：
```
dist/
└── TZ_War_Robot.exe
```

## 运行应用

**方式1：双击运行**
- 在文件管理器中找到 `dist\TZ_War_Robot.exe`
- 双击即可启动

**方式2：命令行运行**
```bash
dist\TZ_War_Robot.exe
```

## 常见问题

### ❓ 脚本无法执行？

**PowerShell 权限问题：**
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

### ❓ 打包失败？

检查以下几点：
1. Python 是否已安装（`python --version`）
2. 是否在项目根目录运行脚本
3. 前端是否已构建（`frontend/dist` 目录存在）

### ❓ EXE 文件很大？

这是正常的，包含了 Python 解释器和所有依赖。大小通常在 100-150 MB。

### ❓ 应用启动很慢？

首次启动会慢一些（需要解压文件），后续启动会更快。

## 分发应用

只需分发 `dist\TZ_War_Robot.exe` 文件即可，用户无需安装 Python。

## 详细文档

更多信息请查看 `WINDOWS_BUILD_GUIDE.md`

---

**需要帮助？** 查看 `WINDOWS_BUILD_GUIDE.md` 中的故障排除部分。

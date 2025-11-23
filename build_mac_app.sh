#!/bin/bash
# TZ War Robot - macOS 独立应用打包脚本

set -e  # 遇到错误立即退出

echo "=========================================="
echo "🚀 TZ War Robot - macOS 应用打包"
echo "=========================================="

# 颜色定义
GREEN='\033[0;32m'
BLUE='\033[0;34m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# 1. 检查并构建前端
echo ""
echo -e "${BLUE}📦 步骤 1/4: 构建前端资源${NC}"
echo "------------------------------------------"
cd frontend

# 检查 node_modules 是否存在
if [ ! -d "node_modules" ]; then
    echo "安装前端依赖..."
    npm install
fi

# 构建前端
echo "构建前端资源..."
npm run build

if [ $? -eq 0 ]; then
    echo -e "${GREEN}✓ 前端构建完成${NC}"
else
    echo -e "${RED}✗ 前端构建失败${NC}"
    exit 1
fi

cd ..

# 2. 安装 Python 打包依赖
echo ""
echo -e "${BLUE}📦 步骤 2/4: 安装打包依赖${NC}"
echo "------------------------------------------"

# 检查是否已安装 pyinstaller
if ! python -c "import PyInstaller" 2>/dev/null; then
    echo "安装 PyInstaller..."
    pip install pyinstaller
else
    echo "PyInstaller 已安装"
fi

# 确保所有后端依赖都已安装
echo "确认后端依赖..."
pip install -r backend/requirements.txt

echo -e "${GREEN}✓ 依赖安装完成${NC}"

# 3. 清理旧的构建文件
echo ""
echo -e "${BLUE}📦 步骤 3/4: 清理旧文件${NC}"
echo "------------------------------------------"

if [ -d "build" ]; then
    echo "删除旧的 build 目录..."
    rm -rf build
fi

if [ -d "dist" ]; then
    echo "删除旧的 dist 目录..."
    rm -rf dist
fi

echo -e "${GREEN}✓ 清理完成${NC}"

# 4. 使用 PyInstaller 打包
echo ""
echo -e "${BLUE}📦 步骤 4/4: 打包应用${NC}"
echo "------------------------------------------"

echo "开始打包（这可能需要几分钟）..."
pyinstaller TZ_Game.spec --clean --noconfirm

if [ $? -eq 0 ]; then
    echo ""
    echo "=========================================="
    echo -e "${GREEN}✅ 打包成功！${NC}"
    echo "=========================================="
    echo ""
    echo "应用位置: $(pwd)/dist/TZ_War_Robot.app"
    echo ""
    echo "📝 使用说明："
    echo "1. 打开 Finder，导航到 dist 目录"
    echo "2. 双击 TZ_War_Robot.app 运行"
    echo "3. 如果遇到安全提示，请到 系统偏好设置 > 安全性与隐私 中允许运行"
    echo ""
    echo "💡 提示："
    echo "- 可以将 .app 拖到 应用程序 文件夹"
    echo "- 首次运行可能需要几秒钟启动"
    echo ""
    
    # 显示应用大小
    APP_SIZE=$(du -sh dist/TZ_War_Robot.app | cut -f1)
    echo "应用大小: ${APP_SIZE}"
    echo ""
else
    echo ""
    echo -e "${RED}✗ 打包失败${NC}"
    echo "请查看上面的错误信息"
    exit 1
fi

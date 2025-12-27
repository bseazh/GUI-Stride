#!/bin/bash
# 反盗版系统快速启动脚本

# 激活虚拟环境
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "$SCRIPT_DIR/venv/bin/activate"

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo "================================================"
echo "🛡️  反盗版自动巡查系统 - 快速启动"
echo "================================================"
echo ""

# 检查 Python 环境
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}❌ 未找到 Python3,请先安装 Python${NC}"
    exit 1
fi

echo -e "${GREEN}✅ Python 环境检查通过${NC}"

# 检查 ADB
if ! command -v adb &> /dev/null; then
    echo -e "${YELLOW}⚠️  未找到 ADB 工具${NC}"
    echo "   请安装 Android Platform Tools:"
    echo "   macOS: brew install android-platform-tools"
    echo "   Linux: sudo apt install android-tools-adb"
else
    echo -e "${GREEN}✅ ADB 工具已安装${NC}"

    # 检查设备连接
    DEVICE_COUNT=$(adb devices | grep -w "device" | wc -l)
    if [ $DEVICE_COUNT -gt 0 ]; then
        echo -e "${GREEN}✅ 已连接 $DEVICE_COUNT 个设备${NC}"
        adb devices
    else
        echo -e "${YELLOW}⚠️  未检测到连接的设备${NC}"
        echo "   请确保:"
        echo "   1. 手机已开启 USB 调试"
        echo "   2. USB 线连接正常"
        echo "   3. 手机上点击了'允许 USB 调试'"
    fi
fi

echo ""
echo "================================================"
echo "选择操作:"
echo "================================================"
echo "1. 添加正版商品到数据库"
echo "2. 查看数据库统计信息"
echo "3. 开始巡查(测试模式)"
echo "4. 开始巡查(正式模式)"
echo "5. 导出举报记录"
echo "0. 退出"
echo ""
read -p "请选择 (0-5): " choice

case $choice in
    1)
        echo ""
        echo "=== 添加正版商品 ==="
        python3 main_anti_piracy.py --add-product
        ;;
    2)
        echo ""
        echo "=== 数据库统计 ==="
        python3 main_anti_piracy.py --show-stats
        ;;
    3)
        echo ""
        echo "=== 开始巡查(测试模式) ==="
        read -p "目标平台 (xiaohongshu/xianyu/taobao) [xiaohongshu]: " platform
        platform=${platform:-xiaohongshu}

        read -p "搜索关键词 [得到]: " keyword
        keyword=${keyword:-得到}

        read -p "最多检查商品数 [10]: " max_items
        max_items=${max_items:-10}

        echo ""
        echo "开始巡查..."
        python3 main_anti_piracy.py \
            --platform $platform \
            --keyword "$keyword" \
            --max-items $max_items \
            --test-mode
        ;;
    4)
        echo ""
        echo "=== 开始巡查(正式模式) ==="
        echo -e "${RED}警告: 正式模式将实际执行举报操作!${NC}"
        read -p "是否继续? (y/N): " confirm

        if [ "$confirm" != "y" ] && [ "$confirm" != "Y" ]; then
            echo "已取消"
            exit 0
        fi

        read -p "目标平台 (xiaohongshu/xianyu/taobao) [xiaohongshu]: " platform
        platform=${platform:-xiaohongshu}

        read -p "搜索关键词 [得到]: " keyword
        keyword=${keyword:-得到}

        read -p "最多检查商品数 [10]: " max_items
        max_items=${max_items:-10}

        echo ""
        echo "开始巡查..."
        python3 main_anti_piracy.py \
            --platform $platform \
            --keyword "$keyword" \
            --max-items $max_items
        ;;
    5)
        echo ""
        echo "=== 导出举报记录 ==="
        read -p "输出文件路径 [report.txt]: " output_path
        output_path=${output_path:-report.txt}

        python3 main_anti_piracy.py --export-report "$output_path"
        ;;
    0)
        echo "退出"
        exit 0
        ;;
    *)
        echo -e "${RED}无效的选择${NC}"
        exit 1
        ;;
esac

echo ""
echo "================================================"
echo "操作完成!"
echo "================================================"

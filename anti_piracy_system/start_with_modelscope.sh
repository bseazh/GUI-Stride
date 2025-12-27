#!/bin/bash
# 使用 ModelScope API 启动反盗版系统

# 切换到项目目录
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# 激活虚拟环境
source venv/bin/activate

# 加载环境变量
if [ -f .env ]; then
    export $(cat .env | grep -v '^#' | xargs)
    echo "✅ 已加载 ModelScope API 配置"
else
    echo "❌ 未找到 .env 文件"
    exit 1
fi

# 颜色定义
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo ""
echo "================================================"
echo "🛡️  反盗版自动巡查系统"
echo "================================================"
echo "配置信息:"
echo "  API: ModelScope"
echo "  模型: $PHONE_AGENT_MODEL"
echo "  地址: $PHONE_AGENT_BASE_URL"
echo "================================================"
echo ""

# 显示菜单
echo "选择操作:"
echo "1. 查看数据库统计"
echo "2. 添加正版商品"
echo "3. 运行诊断测试"
echo "4. 开始巡查(测试模式 - 推荐)"
echo "5. 开始巡查(正式模式)"
echo "6. 运行检测逻辑演示(无需手机)"
echo "0. 退出"
echo ""
read -p "请选择 (0-6): " choice

case $choice in
    1)
        echo ""
        echo "=== 数据库统计 ==="
        python main_anti_piracy.py --show-stats
        ;;
    2)
        echo ""
        echo "=== 添加正版商品 ==="
        python main_anti_piracy.py --add-product
        ;;
    3)
        echo ""
        echo "=== 运行诊断测试 ==="
        python diagnose_model_service.py
        ;;
    4)
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
        python main_anti_piracy.py \
            --base-url "$PHONE_AGENT_BASE_URL" \
            --model "$PHONE_AGENT_MODEL" \
            --apikey "$PHONE_AGENT_API_KEY" \
            --platform "$platform" \
            --keyword "$keyword" \
            --max-items "$max_items" \
            --test-mode
        ;;
    5)
        echo ""
        echo "=== 开始巡查(正式模式) ==="
        echo -e "${YELLOW}警告: 正式模式将实际执行举报操作!${NC}"
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
        python main_anti_piracy.py \
            --base-url "$PHONE_AGENT_BASE_URL" \
            --model "$PHONE_AGENT_MODEL" \
            --apikey "$PHONE_AGENT_API_KEY" \
            --platform "$platform" \
            --keyword "$keyword" \
            --max-items "$max_items"
        ;;
    6)
        echo ""
        echo "=== 检测逻辑演示 ==="
        python demo_detection.py
        ;;
    0)
        echo "退出"
        exit 0
        ;;
    *)
        echo "无效的选择"
        exit 1
        ;;
esac

echo ""
echo "================================================"
echo "操作完成!"
echo "================================================"

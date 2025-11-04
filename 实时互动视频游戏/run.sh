#!/bin/bash
# 启动脚本

echo "🎮 启动实时互动视频游戏..."
echo ""

# 检查是否安装了依赖
if [ ! -d "venv" ] && [ ! -d ".venv" ]; then
    echo "📦 创建虚拟环境..."
    python3 -m venv venv
    source venv/bin/activate
    echo "📦 安装依赖..."
    pip install -r requirements.txt
else
    if [ -d "venv" ]; then
        source venv/bin/activate
    elif [ -d ".venv" ]; then
        source .venv/bin/activate
    fi
fi

# 检查.env文件
if [ ! -f ".env" ]; then
    echo "⚠️  警告: 未找到.env文件"
    echo "请创建.env文件并配置以下环境变量："
    echo "  - DEEPSEEK_API_KEY"
    echo "  - DEEPSEEK_BASE_URL"
    echo "  - OPENAI_API_KEY"
    echo ""
fi

# 启动Streamlit应用
echo "🚀 启动应用..."
streamlit run app.py


#!/bin/bash

# 实时互动视频游戏 - 快速部署脚本
# 使用方法: ./deploy.sh

set -e

IMAGE_NAME="realtime-video-game"
CONTAINER_NAME="realtime-video-game"
PORT="8501"

echo "=========================================="
echo "实时互动视频游戏 - 部署脚本"
echo "=========================================="

# 检查Docker是否安装
if ! command -v docker &> /dev/null; then
    echo "❌ Docker未安装，请先安装Docker"
    echo "参考 DEPLOY.md 中的安装步骤"
    exit 1
fi

# 检查.env文件
if [ ! -f .env ]; then
    echo "⚠️  未找到.env文件，正在创建..."
    cat > .env << EOF
# DeepSeek API配置
DEEPSEEK_API_KEY=your_deepseek_api_key_here
DEEPSEEK_BASE_URL=https://api.deepseek.com

# OpenAI API配置（用于Sora2）
OPENAI_API_KEY=your_openai_api_key_here

# Gemini API配置（可选，用于封面图生成）
GEMINI_API_KEY=your_gemini_api_key_here
EOF
    echo "✅ 已创建.env文件，请编辑并填入正确的API密钥"
    echo "然后重新运行此脚本"
    exit 1
fi

# 检查是否已有同名容器运行
if docker ps -a | grep -q "$CONTAINER_NAME"; then
    echo "⚠️  发现已存在的容器: $CONTAINER_NAME"
    read -p "是否删除并重新创建? (y/n) " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        echo "🛑 停止并删除旧容器..."
        docker stop "$CONTAINER_NAME" 2>/dev/null || true
        docker rm "$CONTAINER_NAME" 2>/dev/null || true
    else
        echo "❌ 部署取消"
        exit 1
    fi
fi

# 创建数据目录
echo "📁 创建数据目录..."
mkdir -p data
chmod 755 data

# 构建Docker镜像
echo "🔨 构建Docker镜像..."
docker build -t "$IMAGE_NAME:latest" .

# 检查镜像是否构建成功
if ! docker images | grep -q "$IMAGE_NAME"; then
    echo "❌ 镜像构建失败"
    exit 1
fi

# 启动容器
echo "🚀 启动容器..."
docker run -d \
  --name "$CONTAINER_NAME" \
  --restart unless-stopped \
  -p "$PORT:8501" \
  --env-file .env \
  -v "$(pwd)/data:/app/data" \
  "$IMAGE_NAME:latest"

# 等待容器启动
echo "⏳ 等待容器启动..."
sleep 5

# 检查容器状态
if docker ps | grep -q "$CONTAINER_NAME"; then
    echo "✅ 容器已启动"
    echo ""
    echo "=========================================="
    echo "部署完成！"
    echo "=========================================="
    echo ""
    echo "应用访问地址："
    echo "  - 直接访问: http://localhost:$PORT"
    echo "  - 通过Nginx: http://your-domain/realtime-video-game/"
    echo ""
    echo "常用命令："
    echo "  查看日志: docker logs -f $CONTAINER_NAME"
    echo "  停止服务: docker stop $CONTAINER_NAME"
    echo "  启动服务: docker start $CONTAINER_NAME"
    echo "  重启服务: docker restart $CONTAINER_NAME"
    echo "  删除容器: docker rm $CONTAINER_NAME"
    echo ""
else
    echo "❌ 容器启动失败，请查看日志:"
    docker logs "$CONTAINER_NAME"
    exit 1
fi


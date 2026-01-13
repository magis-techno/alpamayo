#!/bin/bash
# Alpamayo-R1 部署环境初始化脚本

set -e

echo "========================================"
echo "Alpamayo-R1 部署环境初始化"
echo "========================================"
echo ""

# 检查是否在deploy目录
if [ ! -f "docker-compose.yml" ]; then
    echo "错误: 请在 deploy/ 目录下运行此脚本"
    exit 1
fi

# 创建必要的目录
echo "[1/5] 创建数据目录..."
mkdir -p data/models data/datasets output hf_cache deps
echo "✓ 目录创建完成"

# 检查.env文件
echo ""
echo "[2/5] 检查环境配置..."
if [ ! -f "../.env" ]; then
    echo "警告: 未找到 .env 文件"
    echo "请复制 deploy/env.example 到根目录并重命名为 .env"
    echo ""
    echo "  cp deploy/env.example .env"
    echo "  vim .env  # 编辑配置"
    echo ""
    read -p "是否现在创建 .env 文件？(y/n) " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        cp env.example ../.env
        echo "✓ 已创建 .env 文件，请编辑后继续"
        exit 0
    else
        echo "跳过 .env 创建"
    fi
else
    echo "✓ .env 文件已存在"
fi

# 检查Docker
echo ""
echo "[3/5] 检查Docker环境..."
if ! command -v docker &> /dev/null; then
    echo "错误: Docker 未安装"
    exit 1
fi

if ! docker compose version &> /dev/null; then
    echo "错误: docker compose 未安装"
    exit 1
fi

echo "✓ Docker 环境正常"

# 检查NVIDIA Docker
echo ""
echo "[4/5] 检查GPU支持..."
if ! docker run --rm --gpus all nvidia/cuda:12.0.0-base-ubuntu22.04 nvidia-smi &> /dev/null; then
    echo "警告: NVIDIA Docker 运行时未正确配置"
    echo "请安装 nvidia-container-toolkit"
else
    echo "✓ GPU支持正常"
fi

# 构建镜像
echo ""
echo "[5/5] 构建Docker镜像..."
read -p "是否现在构建Docker镜像？(y/n) " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    docker compose build
    echo "✓ 镜像构建完成"
else
    echo "跳过镜像构建"
fi

echo ""
echo "========================================"
echo "初始化完成！"
echo "========================================"
echo ""
echo "后续步骤："
echo "  1. 编辑 .env 文件配置OBS访问凭证"
echo "  2. (可选) 将模型放到 deploy/data/models/"
echo "  3. 运行 'docker compose up -d' 启动容器"
echo "  4. 运行 'docker exec -it alpamayo-r1 bash' 进入容器"
echo ""

#!/bin/bash
# Alpamayo-R1 推理运行脚本

set -e

# 默认参数
MODEL_PATH="${MODEL_PATH:-/data/models/Alpamayo-R1-10B}"
NUM_SAMPLES="${NUM_SAMPLES:-1}"
ATTN_IMPL="${ATTN_IMPL:-flash_attention_2}"
CLIP_ID="${CLIP_ID:-030c760c-ae38-49aa-9ad8-f5650a545d26}"

echo "========================================"
echo "Alpamayo-R1 推理运行"
echo "========================================"
echo "模型路径: $MODEL_PATH"
echo "Clip ID: $CLIP_ID"
echo "轨迹采样数: $NUM_SAMPLES"
echo "注意力实现: $ATTN_IMPL"
echo "========================================"
echo ""

# 检查模型是否存在
if [ ! -d "$MODEL_PATH" ]; then
    echo "错误: 模型目录不存在: $MODEL_PATH"
    echo ""
    echo "请先下载或准备模型文件："
    echo "  方式1: 从OBS下载 (参见 DEPLOYMENT.md)"
    echo "  方式2: 从HuggingFace下载"
    echo "  方式3: 手动复制到 deploy/data/models/"
    echo ""
    exit 1
fi

# 运行推理
echo "开始推理..."
python /app/src/alpamayo_r1/test_inference.py

echo ""
echo "推理完成！"

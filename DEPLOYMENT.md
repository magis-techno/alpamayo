# 🏔️ Alpamayo-R1 服务器部署指南

本文档详细介绍如何在服务器上部署和运行 Alpamayo-R1 模型，**支持从华为云OBS下载数据和模型**，适用于无法直接访问 HuggingFace 的内网环境。

---

## 目录

1. [环境要求](#1-环境要求)
2. [快速开始](#2-快速开始)
3. [从OBS下载模型和数据](#3-从obs下载模型和数据)
4. [手动准备模型（可选）](#4-手动准备模型可选)
5. [运行推理](#5-运行推理)
6. [常见问题](#6-常见问题)

---

## 1. 环境要求

### 硬件要求

| 组件 | 最低要求 | 推荐配置 |
|------|---------|---------|
| **GPU** | NVIDIA GPU 24GB+ 显存 | A100 40GB / H100 |
| **内存** | 32GB | 64GB+ |
| **存储** | 50GB（模型 22GB + 数据集） | 100GB+ SSD |
| **CUDA** | 12.0+ | 12.4+ |

### 软件要求

- Docker 20.10+ 和 `nvidia-container-toolkit`
- 配置好的华为云OBS访问凭证（如果需要从OBS下载）

---

## 2. 快速开始

### 步骤 1: 克隆项目

```bash
git clone <repository_url>
cd alpamayo
```

### 步骤 2: 初始化部署环境

```bash
# 运行初始化脚本
make setup

# 或手动执行
cd deploy
bash setup.sh
```

初始化脚本会：
- 创建必要的数据目录
- 检查Docker和GPU环境
- 提示配置环境变量

### 步骤 3: 配置环境变量

复制并编辑环境配置文件：

```bash
# 复制示例配置
cp deploy/env.example .env

# 编辑配置（填写OBS凭证）
vim .env
```

**必需配置（如果使用OBS）**：

```bash
# OBS配置
S3_ENDPOINT=https://obs.cn-southwest-2.myhuaweicloud.com
ACCESS_KEY_ID=your_access_key_here
SECRET_ACCESS_KEY=your_secret_key_here
```

### 步骤 4: 构建镜像

```bash
make build
```

### 步骤 5: 启动容器

```bash
make up
```

---

## 3. 从OBS下载模型和数据

如果模型和数据已存储在华为云OBS上，可以直接下载：

### 方式 A: 使用 Makefile（推荐）

```bash
# 下载模型
make download-obs MODEL=obs://your-bucket/models/Alpamayo-R1-10B/

# 下载数据集
make download-obs DATASET=obs://your-bucket/datasets/PhysicalAI-AV/

# 同时下载模型和数据集
make download-obs \
    MODEL=obs://your-bucket/models/Alpamayo-R1-10B/ \
    DATASET=obs://your-bucket/datasets/PhysicalAI-AV/
```

### 方式 B: 进入容器手动下载

```bash
# 进入容器
make shell

# 在容器内运行下载脚本
python /app/deploy/download_from_obs.py \
    --model obs://your-bucket/models/Alpamayo-R1-10B/ \
    --model-dir /data/models \
    --dataset obs://your-bucket/datasets/PhysicalAI-AV/ \
    --dataset-dir /data/datasets
```

### 方式 C: 使用 test_obs_upload.py 工具

项目根目录提供了通用的OBS工具：

```bash
# 下载模型目录
python test_obs_upload.py \
    --download obs://your-bucket/models/Alpamayo-R1-10B/ \
    --output deploy/data/models/Alpamayo-R1-10B

# 下载数据集
python test_obs_upload.py \
    --download obs://your-bucket/datasets/PhysicalAI-AV/ \
    --output deploy/data/datasets/PhysicalAI-AV
```

下载完成后，文件结构如下：

```
deploy/
├── data/
│   ├── models/
│   │   └── Alpamayo-R1-10B/       # 模型权重和配置
│   │       ├── config.json
│   │       ├── model.safetensors.index.json
│   │       ├── model-00001-of-00009.safetensors
│   │       └── ...
│   └── datasets/
│       └── PhysicalAI-AV/          # 数据集（可选）
└── ...
```

---

## 4. 手动准备模型（可选）

如果无法使用OBS，可以手动准备模型：

### 方法 1: 从 HuggingFace 下载（需要外网）

在有外网的机器上：

```bash
# 安装 huggingface_hub
pip install huggingface_hub

# 登录（需要先申请模型访问权限）
huggingface-cli login

# 下载模型
huggingface-cli download nvidia/Alpamayo-R1-10B \
    --local-dir ./Alpamayo-R1-10B

# 下载 Qwen Processor 配置
huggingface-cli download Qwen/Qwen3-VL-2B-Instruct \
    --local-dir ./Qwen3-VL-2B-Instruct \
    --include "*.json" "*.tiktoken" "*.txt"
```

然后传输到服务器：

```bash
# 打包
tar -czvf alpamayo_models.tar.gz Alpamayo-R1-10B/ Qwen3-VL-2B-Instruct/

# 传输到服务器
scp alpamayo_models.tar.gz user@server:/path/to/alpamayo/deploy/data/models/

# 在服务器上解压
cd /path/to/alpamayo/deploy/data/models/
tar -xzvf alpamayo_models.tar.gz
```

### 方法 2: 直接复制

如果已有模型文件，直接复制到 `deploy/data/models/` 目录。

---

## 5. 运行推理

### 方式 A: 使用测试脚本

```bash
# 进入容器
make shell

# 运行测试推理
python /app/src/alpamayo_r1/test_inference.py
```

### 方式 B: 使用 Makefile 命令

```bash
# 运行测试推理
make test

# 运行推理（使用 SDPA 注意力，如果 flash-attn 不可用）
make inference-sdpa
```

### 方式 C: 使用 Jupyter Notebook

```bash
# 启动 Jupyter 服务
make jupyter

# 浏览器访问 http://localhost:8888
# 打开 notebooks/inference.ipynb
```

### 方式 D: 自定义推理代码

```python
import torch
from alpamayo_r1.models.alpamayo_r1 import AlpamayoR1
from alpamayo_r1.load_physical_aiavdataset import load_physical_aiavdataset
from alpamayo_r1 import helper

# 加载模型（使用本地路径）
model_path = "/data/models/Alpamayo-R1-10B"
model = AlpamayoR1.from_pretrained(
    model_path,
    dtype=torch.bfloat16,
    attn_implementation="sdpa"  # 或 "flash_attention_2"
).to("cuda")

processor = helper.get_processor(model.tokenizer)

# 加载数据
clip_id = "030c760c-ae38-49aa-9ad8-f5650a545d26"
data = load_physical_aiavdataset(clip_id, maybe_stream=False)

# 准备输入
messages = helper.create_message(data["image_frames"].flatten(0, 1))
inputs = processor.apply_chat_template(
    messages,
    tokenize=True,
    add_generation_prompt=False,
    continue_final_message=True,
    return_dict=True,
    return_tensors="pt",
)

model_inputs = {
    "tokenized_data": inputs,
    "ego_history_xyz": data["ego_history_xyz"],
    "ego_history_rot": data["ego_history_rot"],
}
model_inputs = helper.to_device(model_inputs, "cuda")

# 推理
torch.cuda.manual_seed_all(42)
with torch.autocast("cuda", dtype=torch.bfloat16):
    pred_xyz, pred_rot, extra = model.sample_trajectories_from_data_with_vlm_rollout(
        data=model_inputs,
        top_p=0.98,
        temperature=0.6,
        num_traj_samples=1,
        max_generation_length=256,
        return_extra=True,
    )

print("Chain-of-Causation:", extra["cot"][0])
print("Predicted trajectory shape:", pred_xyz.shape)
```

---

## 6. 常见问题

### Q1: Flash Attention 安装失败

Flash Attention 需要编译，如果安装失败，使用 PyTorch 内置的 SDPA：

```python
model = AlpamayoR1.from_pretrained(
    model_path,
    dtype=torch.bfloat16,
    attn_implementation="sdpa"  # 使用 PyTorch SDPA
)
```

或使用命令：

```bash
make inference-sdpa
```

### Q2: CUDA Out of Memory

- 减少 `num_traj_samples` 参数（默认 1）
- 检查 GPU 显存：`make gpu`
- 使用更大显存的 GPU（推荐 40GB+）

### Q3: OBS下载失败

确保：
1. `.env` 文件中的OBS凭证正确
2. OBS路径正确（目录路径必须以 `/` 结尾）
3. 网络连接正常

测试OBS连接：

```bash
python test_obs_upload.py --download obs://your-bucket/test-file.txt
```

### Q4: 模型加载时报错 "Not Found"

确保：
1. 模型文件完整下载（检查所有 `.safetensors` 分片）
2. 路径正确（容器内路径 vs 宿主机路径）
3. 离线模式下设置了正确的环境变量

### Q5: 数据集加载失败

`physical_ai_av` 包默认会尝试从 HuggingFace 流式加载。离线使用时：

```python
import os
os.environ["HF_HOME"] = "/data/huggingface"
os.environ["HF_HUB_OFFLINE"] = "1"

# 禁用流式加载
data = load_physical_aiavdataset(clip_id, maybe_stream=False)
```

### Q6: Docker 权限问题

如果遇到权限错误，确保：

```bash
# 将用户添加到 docker 组
sudo usermod -aG docker $USER

# 重新登录或执行
newgrp docker
```

---

## 附录：Make 命令一览

```bash
make help              # 显示所有命令

# 初始化
make setup            # 初始化环境
make build            # 构建镜像

# 容器管理
make up               # 启动容器
make down             # 停止容器
make shell            # 进入容器
make logs             # 查看日志

# 推理
make test             # 运行测试
make inference        # 运行推理
make inference-sdpa   # 运行推理（SDPA模式）

# Jupyter
make jupyter          # 启动 Jupyter
make jupyter-stop     # 停止 Jupyter

# OBS
make download-obs MODEL=obs://... DATASET=obs://...

# GPU
make gpu              # 查看GPU状态
make gpu-watch        # 实时监控GPU

# 清理
make clean            # 清理容器和镜像
make clean-cache      # 清理缓存
```

---

## 参考资料

- [Alpamayo-R1 HuggingFace](https://huggingface.co/nvidia/Alpamayo-R1-10B)
- [PhysicalAI-AV Dataset](https://huggingface.co/datasets/nvidia/PhysicalAI-Autonomous-Vehicles)
- [论文: arXiv:2511.00088](https://arxiv.org/abs/2511.00088)
- [Reference: BUILD_AND_PUSH.md](reference/BUILD_AND_PUSH.md) - OBS工具使用参考

---

## 联系方式

如有问题，请提交 Issue 或参考项目 README。

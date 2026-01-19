# Alpamayo-R1 部署环境 Dockerfile
# 支持从OBS下载数据和模型

FROM nvcr.io/nvidia/pytorch:24.12-py3

# 设置环境变量
ENV DEBIAN_FRONTEND=noninteractive
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# 设置工作目录
WORKDIR /app

# 安装系统依赖
RUN apt-get update && apt-get install -y --no-install-recommends \
    vim \
    wget \
    curl \
    git \
    procps \
    net-tools \
    && rm -rf /var/lib/apt/lists/*

# 升级 pip 和安装 uv
RUN pip install --upgrade pip uv

# 复制项目文件
COPY pyproject.toml README.md ./
COPY src ./src
COPY notebooks ./notebooks

# 安装项目依赖（不含 flash-attn，会单独处理）
RUN pip install --no-cache-dir \
    accelerate>=1.12.0 \
    av>=16.0.1 \
    einops>=0.8.1 \
    hydra-colorlog>=1.2.0 \
    hydra-core>=1.3.2 \
    pandas>=2.3.3 \
    pillow>=12.0.0 \
    transformers==4.57.1 \
    scipy \
    matplotlib \
    mediapy \
    ipykernel \
    ipywidgets \
    jupyter \
    python-dotenv

# 安装 physical_ai_av 包
RUN pip install --no-cache-dir physical_ai_av>=0.1.0

# 尝试安装 flash-attn（如果失败则跳过，可使用 sdpa）
RUN pip install --no-cache-dir flash-attn>=2.8.3 || echo "Warning: flash-attn installation failed. Use sdpa instead."

# 安装OBS工具依赖（华为云内网）
# 注意：moxing_framework.whl 需要手动下载到 deploy/deps/ 目录
# 复制 deps 目录（目录必须存在，可以为空）
COPY deploy/deps/ /tmp/deps/

# 安装 moxing（如果 whl 文件存在）
RUN if ls /tmp/deps/moxing_framework-*.whl 1> /dev/null 2>&1; then \
        pip install --no-cache-dir /tmp/deps/moxing_framework-*.whl && \
        pip install --no-cache-dir coolname && \
        echo "✓ moxing_framework installed"; \
    else \
        echo "⚠ moxing_framework.whl not found, skipping OBS support"; \
    fi

# 复制OBS工具脚本
COPY deploy/common/ ./deploy/common/

# 以 editable 模式安装项目
RUN pip install --no-cache-dir -e .

# 创建数据和输出目录
RUN mkdir -p /data/models /data/datasets /output

# 配置 shell 别名
RUN echo 'alias ll="ls -lh --color=auto"' >> /root/.bashrc && \
    echo 'alias la="ls -lhA --color=auto"' >> /root/.bashrc

# 设置默认工作目录
WORKDIR /workspace

# 默认命令
CMD ["bash"]

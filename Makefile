# Alpamayo-R1 Makefile
# 简化部署和运行操作

.PHONY: help setup build up down restart shell exec logs ps \
        jupyter jupyter-stop jupyter-logs \
        test inference inference-sdpa \
        download-obs clean clean-cache clean-all gpu gpu-watch

# 默认目标
.DEFAULT_GOAL := help

# 变量定义
DOCKER_COMPOSE := docker compose --env-file ../.env -f docker-compose.yml
CONTAINER_NAME := alpamayo-r1
JUPYTER_CONTAINER := alpamayo-r1-jupyter
IMAGE_NAME := alpamayo-r1:latest
DEPLOY_DIR := deploy

# ========================================
# 帮助信息
# ========================================
help: ## 显示帮助信息
	@echo ""
	@echo "🏔️  Alpamayo-R1 Makefile"
	@echo "========================================"
	@echo ""
	@echo "使用方法: make [target]"
	@echo ""
	@echo "📦 可用命令:"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | \
		awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-20s\033[0m %s\n", $$1, $$2}'
	@echo ""

# ========================================
# 初始化与设置
# ========================================
setup: ## 初始化部署环境（创建目录 + 配置检查）
	@echo "🔧 初始化部署环境..."
	@cd $(DEPLOY_DIR) && bash setup.sh
	@echo "✅ 初始化完成"

# ========================================
# Docker 操作
# ========================================
build: ## 构建 Docker 镜像
	@echo "🔨 构建 Docker 镜像..."
	@cd $(DEPLOY_DIR) && $(DOCKER_COMPOSE) build

up: ## 启动主容器（后台运行）
	@echo "🚀 启动容器..."
	@cd $(DEPLOY_DIR) && $(DOCKER_COMPOSE) up -d $(CONTAINER_NAME)
	@echo "✅ 容器已启动"
	@echo "   运行 'make shell' 进入容器"

down: ## 停止所有容器
	@echo "🛑 停止容器..."
	@cd $(DEPLOY_DIR) && $(DOCKER_COMPOSE) down
	@echo "✅ 容器已停止"

restart: down up ## 重启容器

shell: ## 进入主容器 shell
	@echo "🐚 进入容器..."
	@docker exec -it $(CONTAINER_NAME) bash

exec: ## 在容器中执行命令 (用法: make exec CMD="python test.py")
	@docker exec -it $(CONTAINER_NAME) $(CMD)

logs: ## 查看容器日志
	@cd $(DEPLOY_DIR) && $(DOCKER_COMPOSE) logs -f $(CONTAINER_NAME)

ps: ## 查看容器状态
	@cd $(DEPLOY_DIR) && $(DOCKER_COMPOSE) ps

# ========================================
# Jupyter Notebook
# ========================================
jupyter: ## 启动 Jupyter Notebook 服务
	@echo "📓 启动 Jupyter Notebook..."
	@cd $(DEPLOY_DIR) && $(DOCKER_COMPOSE) up -d $(JUPYTER_CONTAINER)
	@echo "✅ Jupyter 已启动"
	@echo "   访问: http://localhost:8888"

jupyter-stop: ## 停止 Jupyter Notebook 服务
	@cd $(DEPLOY_DIR) && $(DOCKER_COMPOSE) stop $(JUPYTER_CONTAINER)

jupyter-logs: ## 查看 Jupyter 日志
	@cd $(DEPLOY_DIR) && $(DOCKER_COMPOSE) logs -f $(JUPYTER_CONTAINER)

# ========================================
# 运行推理
# ========================================
test: ## 运行测试推理脚本
	@echo "🧪 运行测试推理..."
	@docker exec -it $(CONTAINER_NAME) python /app/src/alpamayo_r1/test_inference.py

inference: ## 运行推理 (用法: make inference ARGS="...")
	@echo "🔮 运行推理..."
	@docker exec -it $(CONTAINER_NAME) bash /workspace/run_inference.sh $(ARGS)

inference-sdpa: ## 运行推理（使用 SDPA 注意力，无需 flash-attn）
	@echo "🔮 运行推理 (SDPA 模式)..."
	@docker exec -it $(CONTAINER_NAME) bash -c "ATTN_IMPL=sdpa bash /workspace/run_inference.sh"

# ========================================
# OBS 数据下载
# ========================================
download-obs: ## 从OBS下载模型/数据 (用法: make download-obs MODEL=obs://... DATASET=obs://...)
	@echo "📥 从OBS下载数据..."
	@if [ -z "$(MODEL)" ] && [ -z "$(DATASET)" ]; then \
		echo "错误: 请指定 MODEL 或 DATASET 参数"; \
		echo "示例: make download-obs MODEL=obs://bucket/models/Alpamayo-R1-10B/"; \
		exit 1; \
	fi
	@docker exec -it $(CONTAINER_NAME) python /app/deploy/download_from_obs.py \
		$(if $(MODEL),--model $(MODEL)) \
		$(if $(DATASET),--dataset $(DATASET))

# ========================================
# 清理
# ========================================
clean: ## 停止容器并清理镜像
	@echo "🧹 清理资源..."
	@cd $(DEPLOY_DIR) && $(DOCKER_COMPOSE) down --rmi local -v
	@echo "✅ 清理完成"

clean-cache: ## 清理 HuggingFace 缓存
	@echo "🧹 清理 HuggingFace 缓存..."
	@rm -rf $(DEPLOY_DIR)/hf_cache/*
	@echo "✅ 缓存清理完成"

clean-all: clean clean-cache ## 清理所有（容器 + 缓存）

# ========================================
# GPU 信息
# ========================================
gpu: ## 显示 GPU 状态
	@echo "🎮 GPU 状态:"
	@docker exec -it $(CONTAINER_NAME) nvidia-smi || nvidia-smi

gpu-watch: ## 实时监控 GPU
	@watch -n 1 nvidia-smi

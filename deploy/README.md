# Alpamayo-R1 部署文件

本目录包含 Alpamayo-R1 模型的 Docker 部署配置和脚本。

## 目录结构

```
deploy/
├── Dockerfile              # Docker镜像构建文件
├── docker-compose.yml      # Docker Compose配置
├── env.example             # 环境变量配置示例
├── setup.sh                # 初始化脚本
├── run_inference.sh        # 推理运行脚本
├── download_from_obs.py    # OBS下载工具
├── common/                 # OBS工具库
│   ├── io_obs.py          # OBS上传下载功能
│   ├── config.py          # 配置管理
│   └── ...
├── deps/                   # 依赖文件目录
│   └── (放置 moxing_framework.whl 等依赖)
├── data/                   # 数据目录（运行时创建）
│   ├── models/            # 模型存储
│   └── datasets/          # 数据集存储
├── output/                 # 输出目录（运行时创建）
└── hf_cache/               # HuggingFace缓存（运行时创建）
```

## 快速开始

1. **初始化环境**

```bash
cd deploy
bash setup.sh
```

2. **配置环境变量**

```bash
cp env.example ../.env
vim ../.env  # 编辑OBS凭证等配置
```

3. **构建并启动**

```bash
cd ..
make build
make up
```

4. **进入容器运行推理**

```bash
make shell
python /app/src/alpamayo_r1/test_inference.py
```

详细使用说明请参考 [DEPLOYMENT.md](../DEPLOYMENT.md)。

## 主要命令

| 命令 | 说明 |
|------|------|
| `make setup` | 初始化部署环境 |
| `make build` | 构建Docker镜像 |
| `make up` | 启动容器 |
| `make shell` | 进入容器 |
| `make test` | 运行测试推理 |
| `make download-obs MODEL=obs://...` | 从OBS下载模型 |
| `make gpu` | 查看GPU状态 |
| `make help` | 查看所有命令 |

## 注意事项

1. **OBS依赖**: 如果需要使用OBS功能，需要准备 `moxing_framework.whl` 文件到 `deps/` 目录
2. **GPU要求**: 需要至少 24GB 显存的 NVIDIA GPU
3. **环境变量**: 必须配置 `.env` 文件（不要提交到Git）
4. **数据目录**: `data/`, `output/`, `hf_cache/` 目录会自动创建，已加入 `.gitignore`

## 故障排查

常见问题请参考 [DEPLOYMENT.md § 常见问题](../DEPLOYMENT.md#6-常见问题)。

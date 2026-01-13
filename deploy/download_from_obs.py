#!/usr/bin/env python3
"""
从OBS下载模型和数据集到本地

使用方法:
    # 下载模型
    python download_from_obs.py --model obs://bucket/path/to/Alpamayo-R1-10B/
    
    # 下载数据集
    python download_from_obs.py --dataset obs://bucket/path/to/datasets/
    
    # 同时下载
    python download_from_obs.py --model obs://... --dataset obs://...
"""

import argparse
import logging
import sys
from pathlib import Path
import os

# 添加common目录到路径
sys.path.insert(0, str(Path(__file__).parent))

from common.io_obs import download_directory, init_moxing

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def main():
    parser = argparse.ArgumentParser(description='从OBS下载模型和数据集')
    parser.add_argument(
        '--model',
        type=str,
        help='OBS模型路径（目录，必须以/结尾）'
    )
    parser.add_argument(
        '--dataset',
        type=str,
        help='OBS数据集路径（目录，必须以/结尾）'
    )
    parser.add_argument(
        '--model-dir',
        type=str,
        default='./data/models',
        help='本地模型保存目录（默认: ./data/models）'
    )
    parser.add_argument(
        '--dataset-dir',
        type=str,
        default='./data/datasets',
        help='本地数据集保存目录（默认: ./data/datasets）'
    )
    
    args = parser.parse_args()
    
    if not args.model and not args.dataset:
        parser.error("至少需要指定 --model 或 --dataset")
    
    # 初始化OBS
    logger.info("初始化OBS连接...")
    try:
        init_moxing()
        logger.info("✓ OBS初始化成功")
    except Exception as e:
        logger.error(f"❌ OBS初始化失败: {e}")
        logger.error("请检查环境变量配置：S3_ENDPOINT, ACCESS_KEY_ID, SECRET_ACCESS_KEY")
        sys.exit(1)
    
    # 下载模型
    if args.model:
        logger.info("="*60)
        logger.info("下载模型")
        logger.info("="*60)
        
        model_dir = Path(args.model_dir)
        model_name = args.model.rstrip('/').split('/')[-1]
        local_model_path = model_dir / model_name
        
        logger.info(f"OBS路径: {args.model}")
        logger.info(f"本地路径: {local_model_path}")
        
        try:
            download_directory(args.model, local_model_path)
            logger.info(f"✓ 模型下载成功: {local_model_path}")
        except Exception as e:
            logger.error(f"❌ 模型下载失败: {e}")
            sys.exit(1)
    
    # 下载数据集
    if args.dataset:
        logger.info("="*60)
        logger.info("下载数据集")
        logger.info("="*60)
        
        dataset_dir = Path(args.dataset_dir)
        dataset_name = args.dataset.rstrip('/').split('/')[-1]
        local_dataset_path = dataset_dir / dataset_name
        
        logger.info(f"OBS路径: {args.dataset}")
        logger.info(f"本地路径: {local_dataset_path}")
        
        try:
            download_directory(args.dataset, local_dataset_path)
            logger.info(f"✓ 数据集下载成功: {local_dataset_path}")
        except Exception as e:
            logger.error(f"❌ 数据集下载失败: {e}")
            sys.exit(1)
    
    logger.info("="*60)
    logger.info("下载完成！")
    logger.info("="*60)


if __name__ == '__main__':
    main()

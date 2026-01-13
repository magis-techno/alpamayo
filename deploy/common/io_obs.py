import os
import logging
import tempfile
from datetime import datetime, timezone, timedelta
from pathlib import Path
from typing import Optional
from coolname import generate_slug
from spdatalab.common.config import getenv

logger = logging.getLogger(__name__)

# 全局初始化状态标志（单例模式）
_MOXING_INITIALIZED = False

def is_moxing_initialized() -> bool:
    """检查 moxing 是否已初始化
    
    Returns:
        bool: True 表示已初始化，False 表示未初始化
    """
    return _MOXING_INITIALIZED

def init_moxing():
    """初始化moxing环境（幂等操作，多次调用只初始化一次）
    
    需要配置的环境变量：
    - S3_ENDPOINT: OBS endpoint地址
    - S3_USE_HTTPS: 是否使用HTTPS（默认0）
    - ACCESS_KEY_ID: OBS访问密钥ID
    - SECRET_ACCESS_KEY: OBS访问密钥
    - ADS_DATALAKE_USERNAME: 业务层用户名（与ACCESS_KEY_ID保持一致）
    - ADS_DATALAKE_PASSWORD: 业务层密码（与SECRET_ACCESS_KEY保持一致）
    """
    global _MOXING_INITIALIZED
    
    # 如果已经初始化，直接返回（幂等性）
    if _MOXING_INITIALIZED:
        logger.debug("moxing已初始化，跳过重复初始化")
        return
    
    # 获取配置
    s3_endpoint = getenv('S3_ENDPOINT', required=True)
    s3_use_https = getenv('S3_USE_HTTPS', default='0')
    access_key = getenv('ACCESS_KEY_ID', required=True)
    secret_key = getenv('SECRET_ACCESS_KEY', required=True)
    
    logger.debug(f"初始化moxing: S3_ENDPOINT={s3_endpoint}")
    
    # 设置环境变量
    os.environ['S3_ENDPOINT'] = s3_endpoint
    os.environ['S3_USE_HTTPS'] = s3_use_https
    os.environ['ACCESS_KEY_ID'] = access_key
    os.environ['SECRET_ACCESS_KEY'] = secret_key
    
    # 取消代理
    os.environ.pop('http_proxy', None)
    os.environ.pop('https_proxy', None)
    
    # 导入moxing并切换
    import moxing as mox
    mox.file.shift('os', 'mox')
    
    # 标记为已初始化
    _MOXING_INITIALIZED = True
    logger.debug("moxing初始化完成")

def download(obs_path: str, local_path: Path, retries: int = 3):
    """下载OBS文件到本地
    
    Args:
        obs_path: OBS路径
        local_path: 本地保存路径
        retries: 重试次数
    """
    # 确保 moxing 已初始化
    init_moxing()
    import moxing as mox
    
    if not obs_path.startswith('obs://'):
        obs_path = f'obs://{obs_path}'
    local_path.parent.mkdir(parents=True, exist_ok=True)
    for i in range(retries):
        try:
            mox.file.copy(obs_path, str(local_path))
            if local_path.exists() and local_path.stat().st_size > 0:
                return
        except Exception as e:
            if i == retries -1:
                raise e

def upload(local_path: Path, obs_path: str, retries: int = 3):
    """上传本地文件到OBS
    
    Args:
        local_path: 本地文件路径
        obs_path: OBS目标路径
        retries: 重试次数
        
    Raises:
        FileNotFoundError: 本地文件不存在
        ValueError: 本地文件为空
        Exception: 上传失败
    """
    # 确保 moxing 已初始化
    init_moxing()
    import moxing as mox
    
    # 验证本地文件
    if not local_path.exists():
        raise FileNotFoundError(f"本地文件不存在: {local_path}")
    
    file_size = local_path.stat().st_size
    if file_size == 0:
        raise ValueError(f"本地文件为空: {local_path}")
    
    # 确保OBS路径格式正确
    if not obs_path.startswith('obs://'):
        obs_path = f'obs://{obs_path}'
    
    # 确保OBS目录存在（创建父目录）
    obs_dir = '/'.join(obs_path.split('/')[:-1]) + '/'
    if obs_dir != 'obs://':
        try:
            mox.file.makedirs(obs_dir)
        except Exception:
            pass  # 目录可能已存在，忽略错误
    
    # 重试上传（不打印每个文件的详细日志，减少日志量）
    for i in range(retries):
        try:
            mox.file.copy(str(local_path), obs_path)
            # 验证上传成功（检查OBS文件是否存在）
            if mox.file.exists(obs_path):
                return  # 成功，静默返回
            else:
                raise Exception(f"上传后验证失败，OBS文件不存在: {obs_path}")
        except Exception as e:
            if i == retries - 1:
                logger.error(f"❌ 上传失败（已重试{retries}次）: {local_path.name} -> {obs_path}: {e}")
                raise e
            # 只在重试时打印警告
            if i == 0:
                logger.warning(f"上传失败，重试 {i+1}/{retries}: {local_path.name}")


def upload_directory(local_dir: Path, obs_dir: str, retries: int = 3):
    """递归上传整个目录到OBS
    
    保持目录结构，上传目录中的所有文件到OBS对应路径。
    
    Args:
        local_dir: 本地目录路径
        obs_dir: OBS目标目录路径（必须以/结尾）
        retries: 每个文件的重试次数
        
    Raises:
        FileNotFoundError: 本地目录不存在
        Exception: 上传失败
    """
    if not local_dir.exists():
        raise FileNotFoundError(f"本地目录不存在: {local_dir}")
    
    if not local_dir.is_dir():
        raise ValueError(f"路径不是目录: {local_dir}")
    
    # 确保OBS目录格式正确
    if not obs_dir.startswith('obs://'):
        obs_dir = f'obs://{obs_dir}'
    if not obs_dir.endswith('/'):
        obs_dir = obs_dir + '/'
    
    # 确保 moxing 已初始化
    init_moxing()
    import moxing as mox
    
    # 确保OBS目录存在
    try:
        mox.file.makedirs(obs_dir)
    except Exception:
        pass  # 目录可能已存在，忽略错误
    
    # 统计文件数量（排除 index_parquet 目录）
    all_files = [f for f in local_dir.rglob('*') if f.is_file() and 'index_parquet' not in f.parts]
    total_files = len(all_files)
    
    if total_files == 0:
        logger.warning(f"目录中没有文件可上传: {local_dir}")
        return
    
    logger.info(f"上传目录到OBS: {local_dir.name} -> {obs_dir} (共 {total_files} 个文件)")
    
    # 遍历目录中的所有文件
    uploaded_count = 0
    failed_count = 0
    total_size = 0
    
    for file_path in all_files:
        # 计算相对路径
        relative_path = file_path.relative_to(local_dir)
        obs_file_path = obs_dir + str(relative_path).replace('\\', '/')
        
        try:
            file_size = file_path.stat().st_size
            total_size += file_size
            upload(file_path, obs_file_path, retries=retries)
            uploaded_count += 1
        except Exception as e:
            logger.error(f"上传文件失败: {file_path.name}: {e}")
            failed_count += 1
    
    # 只打印汇总信息
    size_mb = total_size / (1024 * 1024)
    logger.info(f"✓ 目录上传完成: 成功 {uploaded_count}/{total_files} 个文件 ({size_mb:.2f} MB), 失败 {failed_count} 个")
    
    if failed_count > 0:
        raise Exception(f"部分文件上传失败: {failed_count} 个文件")


def copy_obs(src_obs_path: str, dst_obs_path: str, retries: int = 3):
    """拷贝OBS文件到另一个OBS路径
    
    原理：由于moxing不支持OBS到OBS的直接拷贝，采用先下载到临时文件，再上传的方式。
    
    Args:
        src_obs_path: OBS源文件路径
        dst_obs_path: OBS目标文件路径
        retries: 重试次数
        
    Raises:
        ValueError: OBS源文件不存在
        Exception: 拷贝失败
    """
    # 确保 moxing 已初始化
    init_moxing()
    import moxing as mox
    
    # 确保OBS路径格式正确
    if not src_obs_path.startswith('obs://'):
        src_obs_path = f'obs://{src_obs_path}'
    if not dst_obs_path.startswith('obs://'):
        dst_obs_path = f'obs://{dst_obs_path}'
    
    # 验证源文件存在
    if not mox.file.exists(src_obs_path):
        raise ValueError(f"OBS源文件不存在: {src_obs_path}")
    
    # 创建临时文件用于中转
    with tempfile.NamedTemporaryFile(delete=False) as tmp_file:
        tmp_path = Path(tmp_file.name)
    
    try:
        # 先下载到临时文件
        download(src_obs_path, tmp_path, retries=retries)
        
        # 再上传到目标位置
        upload(tmp_path, dst_obs_path, retries=retries)
    finally:
        # 清理临时文件
        if tmp_path.exists():
            tmp_path.unlink()


def copy_obs_directory(src_obs_dir: str, dst_obs_dir: str, retries: int = 3):
    """递归拷贝OBS目录到另一个OBS路径
    
    保持目录结构，拷贝OBS目录中的所有文件到目标OBS路径。
    原理：由于moxing不支持OBS到OBS的直接拷贝，采用先下载到临时目录，再上传的方式。
    
    Args:
        src_obs_dir: OBS源目录路径（必须以/结尾）
        dst_obs_dir: OBS目标目录路径（必须以/结尾）
        retries: 每个文件的重试次数
        
    Raises:
        ValueError: OBS源目录不存在
        Exception: 拷贝失败
    """
    # 确保OBS目录格式正确
    if not src_obs_dir.startswith('obs://'):
        src_obs_dir = f'obs://{src_obs_dir}'
    if not src_obs_dir.endswith('/'):
        src_obs_dir = src_obs_dir + '/'
    
    if not dst_obs_dir.startswith('obs://'):
        dst_obs_dir = f'obs://{dst_obs_dir}'
    if not dst_obs_dir.endswith('/'):
        dst_obs_dir = dst_obs_dir + '/'
    
    # 确保 moxing 已初始化
    init_moxing()
    import moxing as mox
    
    # 验证源目录存在
    if not mox.file.exists(src_obs_dir):
        # 检查是否是文件路径（用户可能误输入）
        test_file_path = src_obs_dir.rstrip('/')
        if mox.file.exists(test_file_path):
            raise ValueError(f"路径是文件而非目录: {src_obs_dir}（提示：OBS目录路径必须以/结尾）")
        else:
            raise ValueError(f"OBS源目录不存在: {src_obs_dir}")
    
    # 创建临时目录用于中转
    with tempfile.TemporaryDirectory() as tmp_dir:
        tmp_path = Path(tmp_dir)
        
        try:
            # 先下载整个目录到临时目录
            download_directory(src_obs_dir, tmp_path, retries=retries)
            
            # 再上传到目标位置
            upload_directory(tmp_path, dst_obs_dir, retries=retries)
        except Exception as e:
            logger.error(f"OBS目录拷贝失败: {e}")
            raise


def download_directory(obs_dir: str, local_dir: Path, retries: int = 3):
    """递归下载OBS目录到本地
    
    保持目录结构，下载OBS目录中的所有文件到本地对应路径。
    
    Args:
        obs_dir: OBS目录路径（必须以/结尾）
        local_dir: 本地目标目录路径
        retries: 每个文件的重试次数
        
    Raises:
        ValueError: OBS目录不存在
        Exception: 下载失败
    """
    # 确保OBS目录格式正确
    if not obs_dir.startswith('obs://'):
        obs_dir = f'obs://{obs_dir}'
    if not obs_dir.endswith('/'):
        obs_dir = obs_dir + '/'
    
    # 确保 moxing 已初始化
    init_moxing()
    import moxing as mox
    
    # 验证OBS目录存在（改进检查）
    if not mox.file.exists(obs_dir):
        # 检查是否是文件路径（用户可能误输入）
        test_file_path = obs_dir.rstrip('/')
        if mox.file.exists(test_file_path):
            raise ValueError(f"路径是文件而非目录: {obs_dir}（提示：OBS目录路径必须以/结尾）")
        else:
            raise ValueError(f"OBS目录不存在: {obs_dir}")
    
    # 确保本地目录存在
    local_dir.mkdir(parents=True, exist_ok=True)
    
    # 递归列出所有文件
    all_files = []
    _list_obs_files_recursive(obs_dir, all_files)
    
    if len(all_files) == 0:
        logger.warning(f"OBS目录中没有文件可下载: {obs_dir}")
        return
    
    logger.info(f"下载目录到本地: {obs_dir} -> {local_dir} (共 {len(all_files)} 个文件)")
    
    # 下载每个文件
    downloaded_count = 0
    failed_count = 0
    total_size = 0
    
    for obs_file_path in all_files:
        # 计算相对路径
        relative_path = obs_file_path[len(obs_dir):]
        local_file_path = local_dir / relative_path
        
        # 确保父目录存在
        local_file_path.parent.mkdir(parents=True, exist_ok=True)
        
        try:
            download(obs_file_path, local_file_path, retries=retries)
            if local_file_path.exists():
                file_size = local_file_path.stat().st_size
                total_size += file_size
            downloaded_count += 1
        except Exception as e:
            logger.error(f"下载文件失败: {obs_file_path}: {e}")
            failed_count += 1
    
    # 只打印汇总信息
    size_mb = total_size / (1024 * 1024)
    logger.info(f"✓ 目录下载完成: 成功 {downloaded_count}/{len(all_files)} 个文件 ({size_mb:.2f} MB), 失败 {failed_count} 个")
    
    if failed_count > 0:
        # 改进错误处理：如果所有文件都失败才抛出异常，否则只警告
        if failed_count == len(all_files):
            raise Exception(f"所有文件下载失败: {failed_count} 个文件")
        else:
            logger.warning(f"部分文件下载失败: {failed_count}/{len(all_files)} 个文件，但继续处理（成功: {downloaded_count}）")
            # 对于评估场景，允许部分失败，不抛出异常


def _list_obs_files_recursive(obs_dir: str, file_list: list, max_depth: int = 20):
    """递归列出OBS目录中的所有文件（辅助函数）
    
    Args:
        obs_dir: OBS目录路径（必须以/结尾）
        file_list: 文件列表（输出）
        max_depth: 最大递归深度
    """
    if max_depth <= 0:
        logger.warning(f"达到最大递归深度，停止列出: {obs_dir}")
        return
    
    init_moxing()
    import moxing as mox
    
    try:
        # 确保目录路径以/结尾
        if not obs_dir.endswith('/'):
            obs_dir = obs_dir + '/'
        
        # 检查目录是否存在
        if not mox.file.exists(obs_dir):
            logger.warning(f"OBS目录不存在: {obs_dir}")
            return
        
        files = mox.file.list_directory(obs_dir, recursive=False)
        
        if not files:
            # 空目录，直接返回
            return
        
        for f in files:
            full_path = obs_dir + f
            
            # 检查是否是目录（OBS中目录通常以/结尾，但也要检查实际存在性）
            if f.endswith('/'):
                # 明确是目录，递归
                _list_obs_files_recursive(full_path, file_list, max_depth - 1)
            else:
                # 可能是文件，但也要检查（有些情况下目录名可能没有/）
                # 尝试检查是否是目录
                test_dir_path = full_path + '/'
                if mox.file.exists(test_dir_path):
                    # 实际上是目录，递归
                    _list_obs_files_recursive(test_dir_path, file_list, max_depth - 1)
                else:
                    # 确实是文件
                    file_list.append(full_path)
                    
    except Exception as e:
        logger.error(f"列出OBS目录失败 {obs_dir}: {e}")
        # 不要抛出异常，让调用者处理


def generate_task_directory_name(obs_base_path: str) -> str:
    """生成唯一的任务目录名：时间戳+随机单词
    
    格式：YYYYMMDD_HHMMSS_<random_slug>
    例如：20240101_120000_gentle-monkey
    
    Args:
        obs_base_path: OBS基础路径
        
    Returns:
        任务目录名（不含路径）
    """
    # 生成北京时区时间戳
    beijing_tz = timezone(timedelta(hours=8))
    timestamp = datetime.now(beijing_tz).strftime("%Y%m%d_%H%M%S")
    
    # 生成随机词（2个词组合，时间戳已保证唯一性）
    random_word = generate_slug(2)
    
    task_name = f"{timestamp}_{random_word}"
    return task_name


def create_task_directory(obs_base_path: str) -> str:
    """创建任务目录并返回完整路径
    
    Args:
        obs_base_path: OBS基础路径，例如 obs://bucket/path/
        
    Returns:
        完整的OBS任务目录路径，例如 obs://bucket/path/20240101_120000_gentle/
    """
    # 确保基础路径格式正确
    if not obs_base_path.startswith('obs://'):
        obs_base_path = f'obs://{obs_base_path}'
    if not obs_base_path.endswith('/'):
        obs_base_path = obs_base_path + '/'
    
    # 生成任务目录名
    task_name = generate_task_directory_name(obs_base_path)
    task_dir = obs_base_path + task_name + '/'
    
    logger.info(f"创建任务目录: {task_dir}")
    
    # 创建OBS目录
    try:
        init_moxing()
        import moxing as mox
        mox.file.makedirs(task_dir)
        logger.info(f"✓ 任务目录已创建: {task_dir}")
    except Exception as e:
        logger.warning(f"创建OBS目录失败（可能已存在）: {e}")
    
    return task_dir


def extract_task_dir_from_path(obs_path: str, obs_base_path: str) -> Optional[str]:
    """从OBS路径中提取任务目录
    
    例如：
    - 输入: obs://bucket/path/l00002951/20240101_120000_alpha/phase1/file.parquet
    - 返回: obs://bucket/path/l00002951/20240101_120000_alpha/
    
    Args:
        obs_path: OBS文件路径
        obs_base_path: OBS基础路径
        
    Returns:
        任务目录路径，如果无法提取则返回None
    """
    if not obs_path.startswith('obs://'):
        return None
    
    # 确保基础路径格式正确
    if not obs_base_path.startswith('obs://'):
        obs_base_path = f'obs://{obs_base_path}'
    if not obs_base_path.endswith('/'):
        obs_base_path = obs_base_path + '/'
    
    # 检查路径是否包含基础路径
    if not obs_path.startswith(obs_base_path):
        return None
    
    # 移除基础路径，获取剩余部分
    remaining = obs_path[len(obs_base_path):]
    
    # 提取第一个目录名（任务目录）
    parts = remaining.split('/')
    if not parts or not parts[0]:
        return None
    
    task_name = parts[0]
    
    # 验证格式：YYYYMMDD_HHMMSS_word
    import re
    pattern = r'^\d{8}_\d{6}_[a-z]+$'
    if not re.match(pattern, task_name):
        return None
    
    # 返回完整任务目录路径
    task_dir = obs_base_path + task_name + '/'
    return task_dir
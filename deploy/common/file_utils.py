"""文件读取工具模块，提供统一的文件读取接口。"""

import logging
from typing import Union, TextIO, BinaryIO, Optional
from pathlib import Path
from contextlib import contextmanager

logger = logging.getLogger(__name__)

@contextmanager
def open_file(path: Union[str, Path], mode: str = 'r') -> Union[TextIO, BinaryIO]:
    """统一的文件打开接口，支持本地文件和OBS文件。
    
    自动处理 moxing 初始化，用户无需手动调用 init_moxing()。
    
    Args:
        path: 文件路径，可以是本地路径或OBS路径（以obs://开头）
        mode: 打开模式，'r'为文本模式，'rb'为二进制模式
        
    Yields:
        文件对象，支持with语句
        
    Raises:
        FileNotFoundError: 文件不存在
        IOError: 文件打开失败
    """
    path = str(path)
    is_obs = path.startswith('obs://')
    
    logger.debug(f"打开文件: {Path(path).name if not is_obs else 'OBS文件'}")
    
    try:
        if is_obs:
            # 延迟导入并自动初始化 moxing
            from spdatalab.common.io_obs import init_moxing
            init_moxing()  # 幂等操作，多次调用只初始化一次
            
            # 延迟导入 moxing（确保在初始化之后）
            import moxing as mox
            file_obj = mox.file.File(path, mode)
        else:
            file_obj = open(path, mode)
            
        yield file_obj
        
    except Exception as e:
        error_type = type(e).__name__
        logger.error(f"❌ 文件打开失败: {Path(path).name}")
        logger.error(f"   错误: {error_type} - {str(e)}")
        logger.debug(f"   完整路径: {path}")
        raise
        
    finally:
        if 'file_obj' in locals():
            logger.debug(f"关闭文件: {Path(path).name if not is_obs else 'OBS文件'}")
            file_obj.close()

def is_obs_path(path: Union[str, Path]) -> bool:
    """判断是否为OBS路径。
    
    Args:
        path: 文件路径
        
    Returns:
        是否为OBS路径
    """
    return str(path).startswith('obs://')

def ensure_dir(path: Union[str, Path]) -> None:
    """确保目录存在，如果不存在则创建。
    
    Args:
        path: 目录路径
    """
    Path(path).mkdir(parents=True, exist_ok=True)

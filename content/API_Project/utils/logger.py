import sys
from datetime import datetime
from loguru import logger
from pathlib import Path

from .exceptionTools import common_exception
# 同层级导入模块必须.

test='你成功测试S'

@common_exception
def setup_logger():
    '''配置loguru'''
    # 清空日志器，避免串扰
    logger.remove()
    # 日志目录
    log_dir=Path(__file__).parent.parent / 'logs'
    # 确保日志目录存在
    log_dir.mkdir(exist_ok=True)
    # 错误日志目录
    error_log_dir=log_dir / 'error_logs'
    # 确保错误日志路径存在
    error_log_dir.mkdir(exist_ok=True)

    # 程序启动时生成固定时间戳
    run_id = datetime.now().strftime("%Y%m%d_%H%M%S")
    log_file = log_dir / f'httpbin_API_test_{run_id}.log'
    error_log_file=error_log_dir / f'httpbin_API_test_error_{run_id}.log'

    # 配置日志文件详细结构
    logger.add(
        str(log_file),
        level='DEBUG',
        format='{time:YYYY-MM-DD HH:mm:ss} | {level:<8} | {module:<20} | {function:<20} | {message}',
        # 设置时间 等级 文件名 函数|方法 日志消息
        # rotation='10MB',     # 日志轮转，每达到10MB开始清理旧日志
        retention=20,           # 只保留最近20个日志文件；同时满足，既可以非固定的日志文件名，又可以控制文件数量，防止日志爆炸
        encoding='utf-8'        # 防止乱码
    )

    # 控制台日志配置
    logger.add(
        sys.stderr,         # 输出至控制台
        level='DEBUG',       # 只显示比>=INFO级别的信息，INFO WARNING ERROR SUCCESS
        format='<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level:<8}</level> | <cyan>{module:<20}</cyan> | {function:<20} | {message:<}',
        # 进行颜色设置
        colorize=True
    )

    # 错误日志提纯
    logger.add(
        str(error_log_file),
        level='ERROR',      # 必须大写
        format='{time:YYYY-MM-DD HH:mm:ss} | {level:<8} | {module:<20} | {function:<20} | {message}',
        retention=20,           # 只保留最近20个日志文件；同时满足，既可以非固定的日志文件名，又可以控制文件数量，防止日志爆炸
        encoding='utf-8'        # 防止乱码
    )
    return logger
log=setup_logger()
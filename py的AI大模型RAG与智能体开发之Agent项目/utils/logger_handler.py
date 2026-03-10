import logging
# 导入 Python 标准库的 logging 模块，用于日志记录功能
# logging 是 Python 内置的日志库，提供灵活的日志记录能力

import os
# 导入 Python 标准库的 os 模块，用于操作系统相关的操作
# 此处用于创建日志目录

from utils.path_tool import get_abs_path

# 从路径工具模块导入 get_abs_path 函数
# 用于获取日志目录的绝对路径

# 日志保存的根目录 (行内注释)
LOG_ROOT = get_abs_path("logs")
# 定义日志根目录常量
# 调用 get_abs_path("logs") 获取 logs 目录的绝对路径
# 例如："D:\PycharmProjects\py 的 AI 大模型 RAG 与智能体开发之 Agent 项目\logs"

# 确保日志目录存在 (行内注释)
os.makedirs(LOG_ROOT, exist_ok=True)
# 创建日志目录，如果目录已存在也不会报错
# exist_ok=True 表示目录存在时不抛出异常
# 这样确保日志文件有保存的目录

# 日志格式配置 (行内注释)
DEFAULT_LOG_FORMAT = logging.Formatter(
    # 定义默认的日志格式器
    # logging.Formatter 用于设置日志输出的格式

    fmt="%(asctime)s %(levelname)s [%(name)s] [%(filename)s:%(lineno)d] - %(message)s",
    # fmt 参数定义日志消息的格式字符串
    # %(asctime)s: 日志时间戳，如 "2026-03-08 02:19:01"
    # %(levelname)s: 日志级别，如 "INFO", "ERROR", "WARNING"
    # %(name)s: logger 的名称，如 "agent"
    # %(filename)s: 源代码文件名，如 "vector_store.py"
    # %(lineno)d: 代码行号，如 71
    # %(message)s: 日志消息内容

    datefmt="%Y-%m-%d %H:%M:%S"
    # datefmt 参数定义时间格式
    # %Y: 四位年份 (2026)
    # %m: 两位月份 (03)
    # %d: 两位日期 (08)
    # %H: 24 小时制小时 (02)
    # %M: 分钟 (19)
    # %S: 秒 (01)
    # 最终时间格式："2026-03-08 02:19:01"
)


def get_logger(
        # 定义获取 logger 对象的函数

        name: str = "agent",
        # 参数 name: logger 的名称，默认为 "agent"
        # 用于标识不同的日志记录器

        console_level: int = logging.INFO,
        # 参数 console_level: 控制台日志级别，默认为 INFO
        # logging.INFO 表示只输出 INFO 及以上级别 (INFO, WARNING, ERROR, CRITICAL)
        # 低于 INFO 的 DEBUG 不会输出到控制台

        file_level: int = logging.DEBUG,
        # 参数 file_level: 文件日志级别，默认为 DEBUG
        # logging.DEBUG 表示记录所有级别的日志 (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        # 文件日志记录更详细的信息，便于调试

        log_file=None,
        # 参数 log_file: 日志文件路径，默认为 None
        # 如果为 None，会使用默认路径
) -> logging.Logger:
    # 返回类型为 logging.Logger 对象

    logger = logging.getLogger(name)
    # 获取指定名称的 logger 对象
    # logging.getLogger(name) 返回一个 logger 实例
    # 如果名称相同，多次调用返回同一个 logger 对象

    logger.setLevel(logging.DEBUG)
    # 设置 logger 的级别为 DEBUG
    # 这是 logger 的最低级别，允许所有级别的日志通过
    # 实际输出由 handler 的级别控制

    # 避免重复添加 Handler (行内注释)
    if logger.handlers:
        # 检查 logger 是否已经有 handlers
        # 如果有 handlers，说明已经配置过，直接返回

        return logger
        # 返回已配置的 logger，避免重复添加 handler 导致日志重复输出

    # 配置控制台 handler (行内注释)
    console_handler = logging.StreamHandler()
    # 创建控制台处理器 (StreamHandler)
    # StreamHandler 会将日志输出到 sys.stdout(控制台)

    console_handler.setLevel(console_level)
    # 设置控制台 handler 的日志级别
    # 默认只输出 INFO 及以上级别的日志

    console_handler.setFormatter(DEFAULT_LOG_FORMAT)
    # 设置控制台 handler 的日志格式为默认格式

    logger.addHandler(console_handler)
    # 将控制台 handler 添加到 logger
    # 这样 logger 就会将日志输出到控制台

    # 文件 Handler (行内注释)
    if log_file is None:
        # 如果没有指定日志文件路径

        log_file = os.path.join(LOG_ROOT, f"{name}.log")
        # 使用默认日志文件路径
        # 例如："D:\...\logs\agent.log"
        # LOG_ROOT 是日志目录，name.log 是文件名

    file_handler = logging.FileHandler(log_file, encoding="utf-8")
    # 创建文件处理器 (FileHandler)
    # FileHandler 会将日志写入到文件
    # encoding="utf-8" 指定文件编码，支持中文

    file_handler.setLevel(file_level)
    # 设置文件 handler 的日志级别
    # 默认记录 DEBUG 及以上所有级别

    file_handler.setFormatter(DEFAULT_LOG_FORMAT)
    # 设置文件 handler 的日志格式

    logger.addHandler(file_handler)
    # 将文件 handler 添加到 logger
    # 这样 logger 就会同时将日志输出到文件和控制台

    return logger
    # 返回配置好的 logger 对象


# 快捷获取日志器 (行内注释)
logger = get_logger()
# 创建一个默认的 logger 对象，名称为 "agent"
# 其他模块可以通过 from utils.logger_handler import logger 直接导入使用
# 这样整个项目可以共用同一个 logger 实例

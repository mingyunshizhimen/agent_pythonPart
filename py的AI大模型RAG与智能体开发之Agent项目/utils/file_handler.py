import hashlib
# 导入 Python 标准库的 hashlib 模块，用于计算文件的 MD5 哈希值

import os
# 导入 Python 标准库的 os 模块，用于文件和目录操作

from langchain_core.documents import Document
# 从 langchain_core 导入 Document 类，用于表示文档对象
# Document 包含 page_content(文本内容) 和 metadata(元数据) 属性

from langchain_community.document_loaders import PyPDFLoader, TextLoader
# 从 langchain_community 导入文档加载器
# PyPDFLoader: 用于加载 PDF 文件
# TextLoader: 用于加载 TXT 文本文件

from utils.logger_handler import logger


# 从日志模块导入 logger 对象，用于记录日志信息

def get_file_md5_hex(filepath: str):
    # 定义函数获取文件的 MD5 十六进制字符串
    # 参数 filepath: 文件路径
    # 返回值：MD5 十六进制字符串，如果出错返回 None

    # 获取文件的 md5 的十六进制字符串 (行内注释)

    if not os.path.exists(filepath):
        # 检查文件是否存在
        # 如果文件不存在，执行此分支

        logger.error(f"[md5 计算] 文件不存在:{filepath}")
        # 记录错误日志，输出文件路径

        return
        # 提前返回 None，结束函数

    if not os.path.isfile(filepath):
        # 检查路径是否为文件 (而非目录)
        # 如果是目录或其他类型，执行此分支

        logger.error(f"[md5 计算] 不是文件:{filepath}")
        # 记录错误日志

        return
        # 提前返回 None

    md5_obj = hashlib.md5()
    # 创建 MD5 哈希对象

    chunk_size = 4096
    # 定义每次读取的块大小为 4096 字节 (4KB)
    # 避免文件过大爆内存 (行内注释)
    # 分块读取大文件，防止一次性加载到内存

    try:
        # 开始异常处理块，捕获可能的文件读取错误

        with open(filepath, "rb") as f:
            # 以二进制只读模式 ("rb") 打开文件
            # 计算文件 md5 必须二进制读取 (行内注释)
            # f 为文件对象

            while chunk := f.read(chunk_size):
                # 使用海象运算符 (:=) 读取文件块并赋值给 chunk
                # while 循环持续读取，直到文件末尾 (返回空字节)
                # 每次读取 4096 字节

                md5_obj.update(chunk)
                # 将读取的文件块更新到 MD5 对象中，累积计算哈希值

            return md5_obj.hexdigest()
                # hexdigest() 返回 MD5 哈希值的十六进制字符串格式

    except Exception as e:
        # 捕获所有异常

        logger.error(f"[md5 计算] 文件读取错误:{filepath},{str(e)}")
        # 记录错误日志，包含文件路径和异常信息

        return None
        # 返回 None 表示计算失败


def listdir_with_allowed_type(path: str, allowed_type: tuple[str]):
    # 定义函数列出目录下指定类型的文件
    # 参数 path: 目录路径
    # 参数 allowed_type: 允许的文件后缀元组，如 (".txt", ".pdf")
    # 返回值：符合条件的文件绝对路径元组

    # 返回文件夹的文件列表 (允许的文件后缀) (行内注释)

    files = []
    # 初始化空列表，用于存储符合条件的文件路径

    if not os.path.exists(path):
        # 检查目录是否存在

        logger.error(f"[listdir_with_allowed_type] 文件不存在:{path}")
        # 记录错误日志

        return
        # 提前返回 None

    if not os.path.isdir(path):
        # 检查路径是否为目录

        logger.error(f"[listdir_with_allowed_type] 不是文件夹:{path}")
        # 记录错误日志

        return
        # 提前返回 None

    for f in os.listdir(path):
        # 遍历目录下的所有文件和子目录
        # os.listdir(path) 返回目录中所有条目的名称列表
        # f 为当前遍历的文件/目录名

        if f.endswith(allowed_type):
            # 检查文件名是否以指定的后缀结尾
            # allowed_type 是元组，如 (".txt", ".pdf")
            # endswith 支持元组，匹配任意一个后缀即返回 True

            files.append(os.path.join(path, f))
            # 将文件路径添加到 files 列表
            # os.path.join(path, f) 拼接目录路径和文件名，得到完整路径

    return tuple(files)
    # 将列表转换为元组并返回
    # 返回包含所有符合条件文件绝对路径的元组


def pdf_loader(filepath: str, passwd: str = None) -> list[Document]:
    # 定义函数加载 PDF 文档
    # 参数 filepath: PDF 文件路径
    # 参数 passwd: PDF 密码 (可选)，默认为 None
    # 返回值：Document 对象列表

    # 加载 pdf 文档的方法 (行内注释)

    return PyPDFLoader(filepath, passwd).load()
    # 创建 PyPDFLoader 对象并调用 load() 方法加载 PDF
    # 返回 Document 对象列表，每个 Document 代表 PDF 的一页内容


def txt_loader(filepath: str) -> list[Document]:
    # 定义函数加载 TXT 文本文件
    # 参数 filepath: TXT 文件路径
    # 返回值：Document 对象列表

    return TextLoader(filepath, encoding="utf-8").load()
    # 创建 TextLoader 对象，指定编码为 utf-8
    # 调用 load() 方法加载文本文件
    # 返回 Document 对象列表

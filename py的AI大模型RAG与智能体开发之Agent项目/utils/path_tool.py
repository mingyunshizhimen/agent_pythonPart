# 为整个工程提供统一的绝对路径
# 文件头部注释，说明此模块的作用是为项目提供统一的路径处理功能

import os


# 导入 Python 标准库的 os 模块，用于文件和目录路径操作

def get_project_root() -> str:
    """
    获取项目根目录
    :return:
    """
    # 定义函数获取项目根目录，返回类型为字符串
    # 函数文档字符串，说明函数功能：返回项目根目录的绝对路径

    # os.path.abspath(__file__) 为获取当前文件的绝对路径，然后 os.path.dirname 两次获取上级目录就获取到了根目录 (我的项目中是这样的)
    # 代码注释，解释获取项目根目录的逻辑
    return os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    # os.path.abspath(__file__): 获取当前文件 (path_tool.py) 的绝对路径
    # 第一个 os.path.dirname(): 获取 utils 目录路径
    # 第二个 os.path.dirname(): 获取项目根目录路径
    # 返回项目根目录的绝对路径字符串


def get_abs_path(relative_path: str):
    """
    获取绝对路径
    :param relative_path: 相对路径
    :return:
    """
    # 定义函数将相对路径转换为绝对路径，参数为相对路径字符串
    # 函数文档字符串，说明参数和返回值

    project_root = get_project_root()
    # 调用 get_project_root() 函数获取项目根目录的绝对路径

    return os.path.join(project_root, relative_path)
    # 使用 os.path.join() 将项目根目录与相对路径拼接，返回完整的绝对路径

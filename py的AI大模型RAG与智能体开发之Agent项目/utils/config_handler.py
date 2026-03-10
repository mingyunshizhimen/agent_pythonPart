# yaml,k:v
# 文件头部注释，说明此模块用于加载 YAML 配置文件，k:v 表示 YAML 的键值对格式

import yaml
# 导入 PyYAML 库，用于解析和读取 YAML 格式的配置文件

from utils.path_tool import get_abs_path


# 从路径工具模块导入 get_abs_path 函数，用于获取配置文件的绝对路径

def load_rag_config(config_path: str = get_abs_path("config/rag.yml"), encoding: str = "utf-8"):
    # 定义加载 RAG 配置的函数
    # 参数 config_path: 配置文件路径，默认值为 "config/rag.yml" 的绝对路径
    # 参数 encoding: 文件编码格式，默认为 "utf-8"

    with open(config_path, "r", encoding=encoding) as f:
        # 使用上下文管理器打开配置文件，只读模式，指定编码格式
        # f 为文件对象

        config = yaml.load(f, Loader=yaml.FullLoader)
        # 使用 yaml.load() 解析 YAML 文件内容
        # Loader=yaml.FullLoader 使用完整加载器，支持所有 YAML 标签
        # 解析结果存储在 config 字典中

    return config
    # 返回解析后的配置字典对象


def load_chroma_config(config_path: str = get_abs_path("config/chroma.yml"), encoding: str = "utf-8"):
    # 定义加载 Chroma 向量库配置的函数
    # 默认读取 "config/chroma.yml" 配置文件

    with open(config_path, "r", encoding=encoding) as f:
        # 打开 Chroma 配置文件
        config = yaml.load(f, Loader=yaml.FullLoader)
        # 解析 YAML 内容

    return config
    # 返回 Chroma 配置字典


def load_prompt_config(config_path: str = get_abs_path("config/prompt.yml"), encoding: str = "utf-8"):
    # 定义加载提示词配置的函数
    # 默认读取 "config/prompt.yml" 配置文件

    with open(config_path, "r", encoding=encoding) as f:
        # 打开提示词配置文件
        config = yaml.load(f, Loader=yaml.FullLoader)
        # 解析 YAML 内容

    return config
    # 返回提示词配置字典


def load_agent_config(config_path: str = get_abs_path("config/agent.yml"), encoding: str = "utf-8"):
    # 定义加载 Agent 配置的函数
    # 默认读取 "config/agent.yml" 配置文件

    with open(config_path, "r", encoding=encoding) as f:
        # 打开 Agent 配置文件
        config = yaml.load(f, Loader=yaml.FullLoader)
        # 解析 YAML 内容

    return config
    # 返回 Agent 配置字典


rag_config = load_rag_config()
# 调用 load_rag_config() 加载 RAG 配置，存储到 rag_config 全局变量
# 其他模块可通过 from utils.config_handler import rag_config 导入使用

chroma_config = load_chroma_config()
# 调用 load_chroma_config() 加载 Chroma 向量库配置，存储到 chroma_config 全局变量

prompt_config = load_prompt_config()
# 调用 load_prompt_config() 加载提示词配置，存储到 prompt_config 全局变量

agent_config = load_agent_config()
# 调用 load_agent_config() 加载 Agent 配置，存储到 agent_config 全局变量

if __name__ == "__main__":
    # 判断是否直接运行此脚本（非导入时）
    # __name__ 为模块名，直接运行时为 "__main__"

    print(rag_config)
    # 打印 RAG 配置内容，用于测试配置加载是否成功

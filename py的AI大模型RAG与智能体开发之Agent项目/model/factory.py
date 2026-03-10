from abc import ABC, abstractmethod
# 从 abc 模块导入抽象基类 ABC 和抽象方法装饰器 abstractmethod
# ABC: Abstract Base Class 的缩写，用于定义抽象基类
# abstractmethod: 装饰器，用于标记抽象方法，子类必须实现这些方法
# 作用：定义接口规范，强制子类实现特定方法

from typing import Optional
# 从 typing 模块导入 Optional 类型提示
# Optional[X] 表示返回值可能是 X 类型或 None
# 用于类型注解，提高代码可读性和 IDE 智能提示

from langchain_core.embeddings import Embeddings
# 从 langchain_core 导入 Embeddings 基类
# Embeddings 是文本嵌入模型的抽象接口，用于将文本转换为向量
# 所有嵌入模型类都继承自 Embeddings

from langchain_community.chat_models.tongyi import BaseChatModel
# 从 langchain_community 导入通义千问聊天模型的基类 BaseChatModel
# BaseChatModel 是所有聊天模型的抽象父类
# 定义了聊天模型的基本接口和方法

from langchain_community.embeddings import DashScopeEmbeddings
# 从 langchain_community 导入通义千问的文本嵌入模型 DashScopeEmbeddings
# 用于将文本转换为向量表示，支持中文文本
# 适用于 RAG 系统的向量检索场景

from langchain_community.chat_models.tongyi import ChatTongyi
# 从 langchain_community 导入通义千问聊天模型 ChatTongyi
# 这是阿里云通义千问大模型的 LangChain 封装
# 支持对话、问答、文本生成等功能

from utils.config_handler import rag_config


# 从配置处理模块导入 rag_config 配置对象
# rag_config 包含 RAG 系统的配置信息，如模型名称等
# 用于动态指定使用的模型

# 定义基础模型工厂抽象基类，继承 ABC 实现抽象类约束 (行内注释)
class BaseModelFactory(ABC):
    # 定义抽象基类 BaseModelFactory，继承 ABC
    # ABC 确保此类不能被实例化，只能被继承
    # 作用：定义模型工厂的统一接口

    # 定义抽象方法 generator，子类必须实现此方法 (行内注释)
    @abstractmethod
    # @abstractmethod 装饰器标记这是一个抽象方法
    # 任何继承 BaseModelFactory 的子类都必须实现此方法
    # 否则实例化时会报错

    def generator(self) -> Optional[Embeddings | BaseChatModel]:
        # 定义抽象方法 generator
        # 返回值类型注解：可能返回 Embeddings、BaseChatModel 或 None
        # Embeddings | BaseChatModel 是联合类型，表示可以返回两种类型之一
        # 方法作用：生成并返回模型实例

        pass
        # 抽象方法体，pass 表示不实现具体逻辑
        # 具体实现由子类完成


# 定义聊天模型工厂类，继承基础模型工厂 (行内注释)
class ChatModelFactory(BaseModelFactory):
    # 定义聊天模型工厂类 ChatModelFactory，继承自 BaseModelFactory
    # 作用：专门用于创建聊天模型实例
    # 使用工厂模式，将模型创建逻辑封装在类中

    # 实现父类的抽象方法 generator (行内注释)
    def generator(self) -> Optional[Embeddings | BaseChatModel]:
        # 实现父类的抽象方法 generator
        # 返回类型：BaseChatModel 或其子类实例
        # 此方法创建并返回聊天模型

        # 从 rag 配置中读取聊天模型名称，创建通义千问聊天模型实例 (行内注释)
        return ChatTongyi(model=rag_config["chat_model_name"])
        # 从配置中读取聊天模型名称：rag_config["chat_model_name"]
        # 例如："qwen3-max" 或 "qwen-turbo"
        # 创建 ChatTongyi 实例，使用配置的模型名称
        # 返回聊天模型对象，可用于对话和文本生成


# 定义嵌入模型工厂类，继承基础模型工厂 (行内注释)
class EmbeddingsFactory(BaseModelFactory):
    # 定义嵌入模型工厂类 EmbeddingsFactory，继承自 BaseModelFactory
    # 作用：专门用于创建文本嵌入模型实例
    # 嵌入模型用于将文本转换为向量，用于相似度检索

    # 实现父类的抽象方法 generator (行内注释)
    def generator(self) -> Optional[Embeddings | BaseChatModel]:
        # 实现父类的抽象方法 generator
        # 返回类型：Embeddings 或其子类实例
        # 此方法创建并返回嵌入模型

        # 从 rag 配置中读取嵌入模型名称，创建通义千问嵌入模型实例 (行内注释)
        return DashScopeEmbeddings(model=rag_config["embedding_model_name"])
        # 从配置中读取嵌入模型名称：rag_config["embedding_model_name"]
        # 例如："text-embedding-v4"
        # 创建 DashScopeEmbeddings 实例，使用配置的模型名称
        # 返回嵌入模型对象，可用于文本向量化


chat_model = ChatModelFactory().generator()
# 创建聊天模型实例并赋值给全局变量 chat_model
# ChatModelFactory(): 实例化聊天模型工厂类
# .generator(): 调用工厂方法创建模型实例
# 相当于：chat_model = ChatTongyi(model="qwen3-max")
# 其他模块可通过 from model.factory import chat_model 导入使用

embed_model = EmbeddingsFactory().generator()
# 创建嵌入模型实例并赋值给全局变量 embed_model
# EmbeddingsFactory(): 实例化嵌入模型工厂类
# .generator(): 调用工厂方法创建模型实例
# 相当于：embed_model = DashScopeEmbeddings(model="text-embedding-v4")
# 其他模块可通过 from model.factory import embed_model 导入使用

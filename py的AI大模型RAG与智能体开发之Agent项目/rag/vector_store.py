import os
# 导入 Python 标准库的 os 模块
# 用于文件和目录操作，如检查文件是否存在、路径拼接等

from langchain_chroma import Chroma
# 从 langchain_chroma 导入 Chroma 类
# Chroma 是一个轻量级向量数据库
# 用于存储和检索文本的向量表示

from langchain_core.documents import Document
# 从 langchain_core 导入 Document 类
# Document 是 LangChain 的文档对象，包含 page_content(文本内容) 和 metadata(元数据)

from langchain_text_splitters import RecursiveCharacterTextSplitter
# 从 langchain_text_splitters 导入递归字符文本分割器
# 用于将长文本切分成小块，便于向量化处理

from utils.config_handler import chroma_config
# 从配置处理模块导入 chroma_config 配置对象
# 包含 Chroma 向量库的所有配置参数

from utils.file_handler import pdf_loader, txt_loader, listdir_with_allowed_type, get_file_md5_hex
# 从文件处理模块导入多个工具函数
# pdf_loader: 加载 PDF 文件
# txt_loader: 加载 TXT 文件
# listdir_with_allowed_type: 列出指定类型的文件
# get_file_md5_hex: 计算文件的 MD5 值用于去重

from utils.logger_handler import logger
# 从日志处理模块导入 logger 对象
# 用于记录日志信息

from utils.path_tool import get_abs_path
# 从路径工具模块导入 get_abs_path 函数
# 用于将相对路径转换为绝对路径

from model.factory import embed_model


# 从模型工厂模块导入 embed_model 嵌入模型实例
# 用于将文本转换为向量

class VectorStoreService:
    # 定义向量存储服务类
    # 封装向量库的创建、文档加载、检索等功能

    def __init__(self):
        # 定义类的构造函数（初始化方法）
        # 在创建 VectorStoreService 实例时自动调用

        self.vector_store = Chroma(
            # 创建 Chroma 向量库实例并赋值给实例变量 self.vector_store
            # self.vector_store 可在类的其他方法中使用

            collection_name=chroma_config['collection_name'],
            # collection_name: 向量集合名称
            # 从配置中读取，默认为 "agent"
            # 用于标识存储扫地机器人知识的向量库

            embedding_function=embed_model,
            # embedding_function: 嵌入函数，用于将文本转换为向量
            # 使用从 model.factory 导入的 embed_model 实例
            # 该模型是 DashScopeEmbeddings 的通义千问嵌入模型

            persist_directory=get_abs_path(chroma_config['persist_directory']),
            # persist_directory: 向量数据持久化目录
            # chroma_config['persist_directory'] 为 "chroma_db"
            # get_abs_path() 将其转换为绝对路径
            # 向量库文件会保存在此目录中
        )

        self.spliter = RecursiveCharacterTextSplitter(
            # 创建递归字符文本分割器并赋值给实例变量 self.spliter
            # 用于将长文档切分成小块

            chunk_size=chroma_config['chunk_size'],
            # chunk_size: 文本块大小，默认为 200 个字符
            # 每个文本片段最多包含 200 个字符

            chunk_overlap=chroma_config['chunk_overlap'],
            # chunk_overlap: 文本块重叠大小，默认为 20 个字符
            # 相邻片段之间重叠 20 个字符，保持上下文连贯性

            separators=chroma_config['separators'],
            # separators: 文本分割优先级列表
            # 按顺序尝试用这些分隔符切分：段落 (\n\n)、换行 (\n)、句子 (.!?)、词语 (, 空格)
            # 优先按大单位分割，分割不开再按小单位分割

            length_function=len
            # length_function: 计算文本长度的函数
            # len 是 Python 内置函数，返回字符串的字符数
        )

    def get_retriever(self):
        # 定义获取检索器的方法
        # 返回一个检索器对象，用于从向量库中查询相似文档

        return self.vector_store.as_retriever(
            # 调用向量库的 as_retriever() 方法转换为检索器
            # as_retriever() 返回一个 Retriever 对象，支持 invoke() 等方法

            search_kwargs={"k": chroma_config['k']}
            # search_kwargs: 检索参数字典
            # "k": chroma_config['k']，默认为 3
            # 表示每次检索返回 3 条最相关的结果
        )

    def load_documents(self):
        # 定义加载文档的方法
        # 从 data 目录读取文件，切分后存入向量库

        # 从数据文件夹内读取数据文件，转为向量存入向量库，要计算文件的 MD5 去重 (行内注释)

        def check_md5_hex(md5_for_check: str):
            # 定义内部函数：检查 MD5 是否已处理过
            # 参数 md5_for_check: 待检查的文件 MD5 值

            if not os.path.exists(get_abs_path(chroma_config['md5_hex_store'])):
                # 检查 MD5 记录文件是否存在
                # chroma_config['md5_hex_store'] 为 "md5.text"
                # get_abs_path() 转换为绝对路径

                open(get_abs_path(chroma_config['md5_hex_store']), "w", encoding="utf-8").close()
                # 如果文件不存在，创建空文件
                # 以写入模式 ("w") 打开，encoding="utf-8" 支持中文
                # close() 立即关闭文件

                return False
                # 返回 False 表示此 MD5 未处理过

            with open(get_abs_path(chroma_config['md5_hex_store']), "r", encoding="utf-8") as f:
                # 以只读模式 ("r") 打开 MD5 记录文件
                # f 为文件对象

                for line in f.readlines():
                    # 遍历文件的每一行
                    # f.readlines() 返回所有行的列表

                    line = line.strip()
                    # strip() 去除行首尾的空白字符（包括换行符 \n）

                    if line == md5_for_check:
                        # 如果文件中的某一行与待检查的 MD5 匹配

                        return True
                        # 返回 True 表示此 MD5 已处理过

                return False
                # 遍历完所有行都没找到，返回 False 表示未处理过

        def save_md5_hex(md5_for_check: str):
            # 定义内部函数：保存 MD5 到记录文件
            # 参数 md5_for_check: 要保存的文件 MD5 值

            with open(get_abs_path(chroma_config['md5_hex_store']), "a", encoding="utf-8") as f:
                # 以追加模式 ("a") 打开 MD5 记录文件
                # 追加模式会在文件末尾写入，不会覆盖原有内容

                f.write(md5_for_check + "\n")
                # 将 MD5 值写入文件，并添加换行符
                # 每个 MD5 占一行

        def get_file_documents(read_path: str):
            # 定义内部函数：根据文件类型加载文档
            # 参数 read_path: 文件路径

            if read_path.endswith(".pdf"):
                # 检查文件是否以 ".pdf" 结尾

                return pdf_loader(read_path)
                # 如果是 PDF 文件，调用 pdf_loader() 加载
                # 返回 Document 对象列表

            if read_path.endswith(".txt"):
                # 检查文件是否以 ".txt" 结尾

                return txt_loader(read_path)
                # 如果是 TXT 文件，调用 txt_loader() 加载
                # 返回 Document 对象列表

            return []
            # 如果既不是 PDF 也不是 TXT，返回空列表

        allowed_files_path = listdir_with_allowed_type(
            # 调用函数获取允许的文件类型列表
            # allowed_files_path 将包含所有符合条件的文件绝对路径

            get_abs_path(chroma_config['data_path']),
            # 第一个参数：数据目录路径
            # chroma_config['data_path'] 为 "data"
            # get_abs_path() 转换为绝对路径，如 "D:\...\data"

            tuple(chroma_config['allow_knowledge_file_type']),
            # 第二个参数：允许的文件后缀元组
            # chroma_config['allow_knowledge_file_type'] 为 [".txt", ".pdf"]
            # tuple() 将列表转换为元组 (".txt", ".pdf")
        )

        for path in allowed_files_path:
            # 遍历所有符合条件的文件路径
            # path 为当前处理的文件绝对路径

            md5_hex = get_file_md5_hex(path)
            # 调用函数计算文件的 MD5 值
            # md5_hex 为 32 位十六进制字符串

            if check_md5_hex(md5_hex):
                # 检查此 MD5 是否已处理过

                logger.info(f"[加载知识库]{path}内容已经存在知识库中，跳过")
                # 如果已处理过，记录信息日志并跳过
                # 避免重复加载相同文件

                continue
                # 跳过本次循环，处理下一个文件

            try:
                # 开始异常处理块，捕获文件处理过程中可能出现的错误

                documents: list[Document] = get_file_documents(path)
                # 调用 get_file_documents() 加载文件内容
                # documents 是 Document 对象列表
                # : list[Document] 是类型注解

                if not documents:
                    # 如果加载的文档为空列表

                    logger.warning(f"[加载知识库]{path}内没用有效文本内容")
                    # 记录警告日志

                    continue
                    # 跳过此文件，处理下一个

                split_document: list[Document] = self.spliter.split_documents(documents)
                # 调用文本分割器将文档切分成小块
                # self.spliter 是在 __init__ 中创建的 RecursiveCharacterTextSplitter
                # split_documents() 返回切分后的 Document 列表
                # 例如：一个 1000 字的文档可能被切分成 5 个 200 字的片段

                if not split_document:
                    # 如果切分后仍为空

                    logger.warning(f"[加载知识库]{path}分片后没用有效文本内容")
                    # 记录警告日志

                    continue
                    # 跳过此文件

                # 将内容存入向量库 (行内注释)
                self.vector_store.add_documents(split_document)
                # 调用向量库的 add_documents() 方法添加文档
                # 自动将文档内容通过 embed_model 转换为向量并存储
                # 同时保存原文本和元数据

                # 记录这个已经处理好的文件的 md5，避免下次重复加载 (行内注释)
                save_md5_hex(md5_hex)
                # 将文件的 MD5 值保存到记录文件
                # 下次运行时会跳过此文件

                logger.info(f"[加载知识库]{path}内容已存入知识库中")
                # 记录成功日志

            except Exception as e:
                # 捕获所有异常，e 为异常对象

                # exc_info 为 True 会记录详细的报错堆栈，如果为 False 只记录报错信息本身 (行内注释)
                logger.error(f"[加载知识库] 加载文件{path}出错:{str(e)}", exc_info=True)
                # 记录错误日志
                # exc_info=True 会输出完整的错误堆栈信息，便于调试

                continue
                # 跳过此文件，继续处理下一个文件


if __name__ == "__main__":
    # 判断是否直接运行此脚本
    # __name__ 为模块名，直接运行时为 "__main__"
    # 被导入时 __name__ 为模块名 "vector_store"

    vs = VectorStoreService()
    # 创建 VectorStoreService 实例
    # 自动初始化向量库和文本分割器

    vs.load_documents()
    # 调用 load_documents() 方法加载所有文档到向量库
    # 会遍历 data 目录下的所有 PDF 和 TXT 文件

    retriever = vs.get_retriever()
    # 调用 get_retriever() 获取检索器
    # retriever 可用于查询向量库

    res = retriever.invoke("外卖")
    # 调用检索器的 invoke() 方法查询向量库
    # 参数 "迷路" 是查询关键词
    # res 是检索结果，包含 k 条（默认 3 条）最相关的 Document 对象

    for r in res:
        # 遍历检索结果
        # r 为每个 Document 对象

        print(r.page_content)
        # 打印文档的文本内容
        # page_content 属性存储文档的原始文本

        print("-" * 20)
        # 打印 20 个短横线作为分隔符
        # 便于区分不同的检索结果

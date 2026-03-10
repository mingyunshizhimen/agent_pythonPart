import os.path
# 导入 os.path 模块，用于路径操作（如检查文件是否存在）

import random
# 导入 random 模块，用于生成随机数
# 这里用于随机返回用户 ID、月份等模拟数据

from utils.config_handler import agent_config
# 从配置处理模块导入 agent_config 配置对象
# 包含 Agent 相关的配置参数

from langchain_core.tools import tool
# 从 langchain_core 导入 tool 装饰器
# 用于将普通函数包装成 LangChain 工具，供 Agent 调用

from rag.rag_service import RagSummarizeService
# 从 RAG 服务模块导入 RagSummarizeService 类
# 用于提供 RAG 检索功能

from utils.logger_handler import logger
# 从日志处理模块导入 logger 对象
# 用于记录日志

from utils.path_tool import get_abs_path

# 从路径工具模块导入 get_abs_path 函数
# 用于将相对路径转换为绝对路径

rag = RagSummarizeService()
# 创建 RAG 总结服务实例
# 用于后续的 rag_summarize 工具调用

user_ids = ["1001", "1002", "1003", "1004", "1005", "1006", "1007", "1008", "1009", "1010"]
# 定义用户 ID 数组
# 包含 10 个模拟用户 ID，用于 get_user_id() 随机返回

month_arr = ["2025-01", "2025=02", "2025-03", "2025-04", "2025-05", "2025-06",
             "2025-07", "2025-08", "2025-09", "2025-10", "2025-11", "2025-12"]
# 定义月份数组
# 包含 12 个月份字符串（注意："2025=02" 应该是笔误，应该是 "2025-02"）
# 用于 get_current_month() 随机返回

external_data = {}
# 定义外部数据列表
# 用于存储从 CSV 文件读取的用户使用记录

@tool(description="从向量存储中检索参考资料")
# @tool 装饰器将函数包装成 LangChain 工具
# description 参数描述工具的功能，Agent 会根据这个描述决定何时调用
def rag_summarize(query: str) -> str:
    # 定义 RAG 检索工具函数
    # 参数 query: 检索关键词（字符串类型）
    # 返回值：检索到的资料（字符串类型）

    return rag.rag_summarize(query)
    # 调用 RagSummarizeService 的 rag_summarize 方法
    # 从向量库检索与 query 相关的知识


@tool(description="获取天气信息，以消息字符串的形式返回")
# 定义获取天气的工具
def get_weather(city: str) -> str:
    # 参数 city: 城市名称
    # 返回值：天气信息字符串

    return f"城市{city}天气为晴天，气温 26 度，空气湿度 50%"
    # 返回模拟的天气信息
    # 实际项目中应该调用真实天气 API


@tool(description="获取用户所在城市的名称，以纯字符串形式返回")
# 定义获取用户位置的工具
def get_user_location() -> str:
    # 无参数
    # 返回值：城市名称字符串

    return random.choice(["北京", "上海", "广州", "深圳"])
    # 从城市列表中随机返回一个
    # 模拟获取用户位置


@tool(description="获取用户的 ID，以纯字符串形式返回")
# 定义获取用户 ID 的工具
def get_user_id() -> str:
    # 无参数
    # 返回值：用户 ID 字符串

    return random.choice(user_ids)
    # 从 user_ids 数组中随机返回一个用户 ID
    # 例如："1005"


@tool(description="获取当前月份，以纯字符串形式返回")
# 定义获取当前月份的工具
def get_current_month() -> str:
    # 无参数
    # 返回值：月份字符串

    return random.choice(month_arr)
    # 从 month_arr 数组中随机返回一个月份
    # 例如："2025-06"


def generate_external_data():
    # 定义生成外部数据的函数
    # 从 CSV 文件读取用户使用记录并存储到 external_data

    if not external_data:
        # 检查 external_data 是否为空
        # 如果为空（还没加载过数据），则执行加载

        external_data_path = get_abs_path(agent_config["external_data_path"])
        # 从配置中读取外部数据文件路径
        # agent_config["external_data_path"] 可能是 "data/external/records.csv"
        # get_abs_path() 转换为绝对路径

        if not os.path.exists(external_data_path):
            # 检查文件是否存在

            raise FileNotFoundError(f"外部数据文件{external_data_path}不存在")
            # 如果文件不存在，抛出文件未找到异常

        with open(external_data_path, "r", encoding="utf-8") as f:
            # 以只读模式打开 CSV 文件，编码为 utf-8
            # f 为文件对象

            for line in f.readlines()[1:]:
                # 读取文件所有行，跳过第 1 行（标题行）
                # 从第 2 行开始遍历每一行数据
                # 例如："1001","爱干净","高效","正常","比上月提升 5%","2025-01"

                # 跳过第一行，也就是跳过标题行，意为从第二行开始读取数据（行内注释）

                arr: list[str] = line.strip().split(",")
                # strip() 去除行首尾空白字符和换行符
                # split(",") 按逗号分割成数组
                # arr 是字符串列表，例如：['"1001"', '"爱干净"', '"高效"', ...]

                user_id: str = arr[0].replace('"', "")
                # arr[0] 是第 1 列（用户 ID）
                # replace('"', "") 去除双引号
                # 例如：'"1001"' → '1001'

                feature: str = arr[1].replace('"', "")
                # arr[1] 是第 2 列（用户特征）
                # 例如：'"爱干净"' → '爱干净'

                efficiency: str = arr[2].replace('"', "")
                # arr[2] 是第 3 列（清洁效率）
                # 例如：'"高效"' → '高效'

                consumables: str = arr[3].replace('"', "")
                # arr[3] 是第 4 列（耗材状态）
                # 例如：'"正常"' → '正常'

                comparison: str = arr[4].replace('"', "")
                # arr[4] 是第 5 列（使用对比）
                # 例如：'"比上月提升 5%"' → '比上月提升 5%'

                time: str = arr[5].replace('"', "")
                # arr[5] 是第 6 列（时间/月份）
                # 例如：'"2025-01"' → '2025-01'

                if user_id not in external_data:
                    # 检查这个用户 ID 是否已经在 external_data 中
                    # 如果是新用户，初始化他的数据

                    external_data[user_id] = {}
                    # 【字典套字典的关键！】
                    # 为这个用户创建一个空字典
                    # 例如：external_data["1001"] = {}

                external_data[user_id][time] = {
                    # 【字典套字典的核心！】
                    # external_data 是一个大字典
                    # 第一层键：user_id（用户 ID）
                    # 第二层键：time（月份）
                    # 值：包含特征、效率、耗材、对比的字典

                    # 示例结构：
                    # external_data = {
                    #     "1001": {
                    #         "2025-01": {
                    #             "特征": "爱干净",
                    #             "效率": "高效",
                    #             "耗材": "正常",
                    #             "对比": "比上月提升 5%"
                    #         },
                    #         "2025-02": {
                    #             "特征": "爱干净",
                    #             "效率": "高效",
                    #             "耗材": "正常",
                    #             "对比": "与上月持平"
                    #         }
                    #     },
                    #     "1002": {
                    #         "2025-01": {
                    #             "特征": "注重节能",
                    #             "效率": "中等",
                    #             "耗材": "正常",
                    #             "对比": "比上月下降 3%"
                    #         }
                    #     }
                    # }

                    "特征": feature,
                    # 存储用户特征

                    "效率": efficiency,
                    # 存储清洁效率

                    "耗材": consumables,
                    # 存储耗材状态

                    "对比": comparison,
                    # 存储使用对比数据
                }


@tool(description="从外部系统中获取指定用户在指定月份的使用记录，以纯字符串形式返回，如果没用检索到返回空字符串")
# 定义获取外部数据的工具
def fetch_external_data(user_id: str, month: str) -> str:
    # 参数 user_id: 用户 ID
    # 参数 month: 月份（格式：YYYY-MM）
    # 返回值：使用记录字符串

    generate_external_data()
    # 调用函数生成/加载外部数据
    # 确保数据已经加载到 external_data 中

    try:
        return external_data[user_id][month]
        # 【访问字典套字典】
        # 第一层：external_data[user_id] 获取该用户的所有月份数据
        # 第二层：[month] 获取指定月份的数据
        # 例如：external_data["1001"]["2025-01"]
        # 返回：{"特征": "爱干净", "效率": "高效", "耗材": "正常", "对比": "比上月提升 5%"}

    except KeyError:
        # 捕获 KeyError 异常
        # 当用户 ID 或月份不存在时会抛出此异常

        logger.warning(f"[fetch_external_data] 未找到用户{user_id}在{month}的记录")
        # 记录警告日志

        return ""
        # 返回空字符串表示未找到
@tool(description='无入参,无返回值,调用后触发中间件自动为报告生成的场景动态注入上下文信息,为后续提示词切换提供上下文信息')
def fill_context_for_report():
    return "fill_context_for_report已经调用"
if __name__ == "__main__":
    # 测试代码
    # 运行此文件时，将生成外部数据并测试获取外部数据的功能

    print(fetch_external_data("1001", "2025-01"))
    # 获取用户 1001 在 2025-01 的使用记录
    # 输出：{"特征": "爱干净", "效率": "高效", "耗材": "正常", "对比": "比上月提升 5%"}

from langchain.agents import create_agent
# 从 langchain 导入 create_agent 函数
# 用于创建 Agent（智能体）
from agent.tools.skyway_crud_tools import tools as skyway_tools
from agent.tools.agent_tools import rag_summarize, get_weather, get_user_location, get_user_id, get_current_month, \
    fetch_external_data, fill_context_for_report
# 从工具模块导入 7 个工具函数：
# - rag_summarize: RAG 检索工具
# - get_weather: 获取天气
# - get_user_location: 获取用户位置
# - get_user_id: 获取用户 ID
# - get_current_month: 获取当前月份
# - fetch_external_data: 获取外部数据
# - fill_context_for_report: 填充报告上下文

from agent.tools.middleware import monitor_tool, log_before_model, report_prompt_switch
# 从中间件模块导入 3 个中间件：
# - monitor_tool: 监控工具调用
# - log_before_model: 模型调用前日志
# - report_prompt_switch: 动态切换提示词

from model.factory import chat_model
# 从模型工厂导入 chat_model 聊天模型实例
# 这是通义千问大模型

from utils.prompt_loader import load_system_prompts, load_sky_prompt


# 从提示词加载模块导入 load_system_prompts 函数
# 用于加载系统提示词


class ReactAgent:
    # 定义 ReAct Agent 类
    # ReAct = Reasoning + Acting（推理 + 行动）

    def __init__(self):
        # 构造函数（初始化方法）
        # 创建 Agent 实例时自动调用

        self.agent = create_agent(
            # 调用 create_agent 创建 Agent
            # self.agent 是创建好的 Agent 对象

            model=chat_model,
            # model 参数：指定使用的大模型
            # chat_model 是从 model.factory 导入的 ChatTongyi 实例

            system_prompt=load_sky_prompt(),
            # sky_prompt 参数：系统提示词
            # load_sky_prompts() 从文件加载提示词
            # 提示词内容："你是苍穹外卖的专业智能客服..."

            tools=[rag_summarize, get_weather, get_user_location, get_user_id,
                   get_current_month, fetch_external_data, fill_context_for_report,*skyway_tools],
            # tools 参数：工具列表
            # Agent 可以调用的 7 个工具
            # 当需要额外信息时，Agent 会自动调用这些工具

            middleware=[monitor_tool, log_before_model, report_prompt_switch],
            # middleware 参数：中间件列表
            # 3 个中间件会在特定时机自动执行：
            # - monitor_tool: 每次调用工具前
            # - log_before_model: 每次调用模型前
            # - report_prompt_switch: 每次生成提示词前
        )

    def execute_stream(self, query: str):
        # 【核心方法】执行流式处理
        # 参数 query: 用户的问题（字符串）
        # 返回值：生成器（yield），逐步返回回答内容

        # ==================== execute_stream 详解 ====================

        input_dict = {
            # 创建输入字典，包含对话消息
            # 这是传给 Agent 的标准格式

            "messages": [
                # messages 是消息列表，包含所有对话历史

                {
                    "role": "user",
                    # role: 消息角色
                    # "user" 表示这是用户发送的消息

                    "content": query,
                    # content: 消息内容
                    # query 是用户输入的问题
                    # 例如："扫地机器人迷路了怎么办？"
                },
            ]
        }

        # 第三个参数 context 就是上下文 runtime 中的信息，就是我们做提示词切换的标记 (行内注释)

        for chunk in self.agent.stream(input_dict, stream_mode="values", context={"report": False}):
            # 【关键】调用 Agent 的 stream 方法，流式处理 Agent 响应
            # stream() 会逐步返回 Agent 的思考过程和最终回答

            # 参数详解：
            # - input_dict: 输入消息字典
            # - stream_mode="values": 流式模式为 "values"
            #   表示返回每个步骤的完整状态值
            # - context={"report": False}: 运行时上下文
            #   设置 report=False 表示"这不是报告生成场景"
            #   如果是报告生成，设置为 True，中间件会切换提示词

            # chunk 是什么？
            # chunk 是 Agent 执行过程中的每个"片段"
            # 包含：思考过程、工具调用、工具结果、最终回答
            # 例如：
            # {
            #     "messages": [
            #         HumanMessage("扫地机器人迷路了怎么办？"),
            #         AIMessage("我来查一下相关知识..."),
            #         ToolMessage("检索到 3 条相关知识..."),
            #         AIMessage("根据资料，建议您...")  ← 最终回答
            #     ]
            # }

            latest_message = chunk['messages'][-1]
            # 获取最新消息
            # chunk['messages'] 是当前所有消息列表
            # [-1] 获取最后一条消息（最新消息）
            # 最新消息可能是：
            # - 工具调用（"调用 rag_summarize 工具"）
            # - 工具结果（"检索到 3 条知识"）
            # - 最终回答（"根据资料，建议您..."）

            if latest_message.content:
                # 检查消息是否有内容
                # 如果有内容，则返回给调用者

                yield latest_message.content.strip() + "\n"
                # 【关键】yield 是生成器的关键字
                # 逐步返回内容，而不是一次性返回所有内容

                # yield vs return 的区别：
                # return: 一次性返回所有结果，函数结束
                # yield: 返回一个结果，暂停函数，下次继续

                # 例如：
                # 第 1 次 yield: "根据相关资料..."
                # 暂停 ⏸️
                # 第 2 次 yield: "扫地机器人迷路时..."
                # 暂停 ⏸️
                # 第 3 次 yield: "建议您检查传感器..."
                # 结束 ✅

                # 这样做的好处：
                # 1. 流式输出：用户可以逐步看到回答，不用等全部生成完
                # 2. 节省内存：不需要一次性存储所有回答
                # 3. 实时反馈：用户可以看到 Agent 的思考过程

        # ==================== execute_stream 流程总结 ====================
        """
        用户输入："扫地机器人迷路了怎么办？"
            ↓
        创建 input_dict
            ↓
        调用 self.agent.stream(...)
            ↓
        Agent 开始执行（思考 → 调用工具 → 再思考 → 回答）
            ↓
        每次执行一步，返回一个 chunk
            ↓
        获取最新消息
            ↓
        如果有内容，yield 返回
            ↓
        继续执行下一步...
            ↓
        所有步骤完成，生成器结束
        """


if __name__ == "__main__":
    # 判断是否直接运行此脚本
    # 如果是直接运行（不是被导入），则执行测试代码

    agent = ReactAgent()
    # 创建 ReactAgent 实例
    # 会自动调用 __init__，创建内部的 Agent

    for chunk in agent.execute_stream("我想查询你们平台的菜品都有啥"):
        # 调用 execute_stream 方法
        # 传入测试问题："扫地机器人在我所在的地区的气温下如何保养"

        # execute_stream 返回一个生成器
        # for 循环逐步获取每个 chunk

        print(chunk, end="", flush=True)
        # 打印每个 chunk
        # end="": 不换行（因为 chunk 已经包含 \n）
        # flush=True: 立即刷新输出（流式显示效果）

        # 输出示例：
        # 让我先获取您所在的城市...
        # 调用工具：get_user_location
        # 工具结果：北京
        # 让我查询北京的天气...
        # 调用工具：get_weather
        # 工具结果：北京天气晴朗，26 度
        # 根据查询结果，在您的地区...

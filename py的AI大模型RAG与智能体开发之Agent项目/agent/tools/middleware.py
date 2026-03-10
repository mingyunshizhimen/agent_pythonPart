from typing import Callable
# 【你手动导入】用于类型标注，标注函数类型

from langchain.agents import AgentState
# 【你手动导入】Agent 状态类，包含对话历史

from langchain.agents.middleware import wrap_tool_call, before_model, dynamic_prompt, ModelRequest
# 【你手动导入】3 个装饰器（LangChain 提供的钩子）
# 你用这些装饰器注册你的函数到 LangChain 框架

from langchain.tools.tool_node import ToolCallRequest
# 【你手动导入】工具调用请求封装类

from langchain_core.messages import ToolMessage
# 【你手动导入】工具返回消息类

from langgraph.runtime import Runtime
# 【你手动导入】运行时上下文对象

from langgraph.types import Command
# 【你手动导入】命令类型（控制 Agent 流程）

from typing_extensions import runtime
# 【你手动导入】类型扩展

from utils.logger_handler import logger
# 【你手动导入】你的项目日志模块

from utils.prompt_loader import load_report_prompts, load_system_prompts


# 【你手动导入】你的项目提示词加载函数


# ==================== 你手动编写的中间件函数 1 ====================
# 作用：监控所有工具调用（记录日志、设置标记）

@wrap_tool_call
# 【LangChain 装饰器】
# 作用：把你的 monitor_tool 函数注册到 LangChain 框架
# LangChain 看到此装饰器后，会在每次调用工具前自动执行你的 monitor_tool

def monitor_tool(
        # 【你手动定义】工具监控函数
        # 这个函数会被 LangChain 自动调用（你不需要手动调用它）

        request: ToolCallRequest,
        # 【LangChain 自动传入】请求对象
        # LangChain 框架在调用工具时自动创建并传入此对象
        # 包含：工具名称、参数、调用 ID 等
        # 例如：{"name": "get_weather", "args": {"city": "北京"}, "id": "call_123"}

        handler: Callable[[ToolCallRequest], ToolMessage | Command],
        # 【LangChain 自动传入】实际执行工具的函数
        # LangChain 从工具注册表中获取对应的工具函数，作为参数传给你
        # 你需要调用它来执行真正的工具逻辑
) -> ToolMessage | Command:
    # 【你手动定义】返回值类型
    # 必须返回 ToolMessage 或 Command，LangChain 需要这个返回值

    # ==================== 你手动编写的逻辑 ====================
    logger.info(f"[tool monitor] 执行工具:{request.tool_call['name']}")
    # 记录日志：打印工具名称
    # 例如："[tool monitor] 执行工具:get_weather"

    logger.info(f"[tool monitor] 传入参数:{request.tool_call['args']}")
    # 记录日志：打印工具参数
    # 例如："[tool monitor] 传入参数:{'city': '北京'}"

    try:
        # 【关键】你手动调用 handler
        result = handler(request)
        # handler 是 LangChain 传入的工具函数
        # 你必须调用它，真正的工具逻辑才会执行
        # 例如：调用 get_weather("北京")

        logger.info(f"[tool monitor] 工具{request.tool_call}执行结果:{result}")
        # 记录日志：打印工具执行结果

        if request.tool_call["name"] == "fill_context_for_report":
            # 【你手动编写的特殊逻辑】
            # 检查是否是报告生成工具
            # 如果是，设置全局标记

            request.runtime.context['report'] = True
            # runtime.context 是 LangChain 提供的全局共享字典
            # 你设置 'report': True，后续的 dynamic_prompt 可以读取
        # ==================== 你手动编写的逻辑结束 ====================

        return result
        # 【必须】返回工具执行结果给 LangChain

    except Exception as e:
        # 【你手动编写的异常处理】
        logger.error(f"[tool monitor] 工具{request.tool_call}执行错误:{str(e)}")
        # 记录错误日志

        raise e
        # 【必须】重新抛出异常，让 LangChain 知道出错了


# ==================== 你手动编写的中间件函数 2 ====================
# 作用：在模型调用前记录日志

@before_model
# 【LangChain 装饰器】
# 作用：把你的 log_before_model 函数注册到 LangChain 框架
# LangChain 会在每次调用大模型前自动执行你的 log_before_model

def log_before_model(
        # 【你手动定义】模型调用前的日志函数
        # 这个函数会被 LangChain 自动调用（你不需要手动调用它）

        state: AgentState,
        # 【LangChain 自动传入】Agent 当前状态
        # LangChain 框架自动传入，包含所有对话消息
        # state['messages'] 是消息列表

        runtime: Runtime,
        # 【LangChain 自动传入】运行时上下文
        # LangChain 框架自动传入，包含执行过程的各种信息
):
    # ==================== 你手动编写的逻辑 ====================
    logger.info(f"[log_before_model] 即将调用模型，带有{len(state['messages'])}条消息")
    # 记录日志：打印当前消息数量
    # 例如："[log_before_model] 即将调用模型，带有 5 条消息"

    logger.debug(f"[log_before_model]{type(state['messages'][-1]).__name__}|{state['messages'][-1].content.strip()}")
    # 记录调试日志：打印最后一条消息
    # state['messages'][-1] 获取最后一条消息
    # 例如："HumanMessage|扫地机器人迷路了怎么办"
    # ==================== 你手动编写的逻辑结束 ====================

    return None
    # 【可选】返回 None 表示不修改任何状态
    # 如果返回修改后的 state，LangChain 会使用你的修改


# ==================== 你手动编写的中间件函数 3 ====================
# 作用：动态切换提示词（报告场景 vs 普通场景）

@dynamic_prompt
# 【LangChain 装饰器】
# 作用：把你的 report_prompt_switch 函数注册到 LangChain 框架
# LangChain 会在每次生成提示词前自动执行你的 report_prompt_switch

def report_prompt_switch(requests: ModelRequest):
    # 【你手动定义】提示词切换函数
    # 这个函数会被 LangChain 自动调用（你不需要手动调用它）

    requests: ModelRequest
    # 【LangChain 自动传入】模型请求对象
    # LangChain 框架自动传入，包含当前状态、运行时上下文等

    # ==================== 你手动编写的逻辑 ====================
    is_report = requests.runtime.context.get('report', False)
    # 从 LangChain 提供的 runtime.context 中读取 'report' 标记
    # 这个标记是你在 monitor_tool 中设置的
    # .get('report', False) 如果不存在则返回 False

    if is_report:
        # 如果是报告生成场景

        return load_report_prompts()
        # 【必须】返回报告生成提示词
        # LangChain 会使用你返回的提示词作为系统提示

    return load_system_prompts()
    # 【必须】返回默认系统提示词
    # 如果不是报告场景，返回普通客服提示词
    # ==================== 你手动编写的逻辑结束 ====================


# ==================== 总结：哪些是 LangChain 自动的，哪些是你手动的 ====================

"""
【你手动编写的部分】（你的业务逻辑）：
1. 导入模块（所有 import）
2. 定义 3 个中间件函数（monitor_tool、log_before_model、report_prompt_switch）
3. 函数内部的逻辑（记录日志、设置标记、返回提示词）
4. 调用 handler(request) 执行真正的工具

【LangChain 自动调用的部分】（框架自动执行）：
1. @wrap_tool_call、@before_model、@dynamic_prompt 装饰器注册你的函数
2. 在合适的时机自动调用你的函数：
   - 每次调用工具前 → 自动调用 monitor_tool(request, handler)
   - 每次调用模型前 → 自动调用 log_before_model(state, runtime)
   - 每次生成提示词前 → 自动调用 report_prompt_switch(requests)
3. 自动传入参数（request、handler、state、runtime、requests）
4. 使用你的返回值（ToolMessage、提示词字符串）

【你不需要做的】：
1. 不需要手动调用 monitor_tool、log_before_model、report_prompt_switch
2. 不需要手动创建 request、handler、state、runtime 等对象
3. 不需要关心什么时候调用这些函数

【你必须做的】：
1. 用装饰器标记你的函数（@wrap_tool_call 等）
2. 函数签名必须匹配（参数类型、返回值类型）
3. 在 monitor_tool 中必须调用 handler(request)
4. 在 dynamic_prompt 中必须返回提示词字符串
"""

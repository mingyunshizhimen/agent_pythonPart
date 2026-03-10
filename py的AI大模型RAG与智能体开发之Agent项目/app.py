import time
# 导入 time 模块
# 用于实现打字机效果（逐字输出时的延迟）

import streamlit as st
# 导入 Streamlit 库
# Streamlit 是一个快速创建 Web 应用的 Python 库
# 用于构建聊天界面

from agent.react_agent import ReactAgent

# 从 agent 模块导入 ReactAgent 类
# 这是我们的扫地机器人智能客服 Agent


# 标题 (行内注释)
st.title("智扫通机器人智能客服")
# 设置网页标题
# 显示在页面顶部的大标题

st.divider()
# 添加一条水平分割线
# 分隔标题和聊天区域

if "agent" not in st.session_state:
    # 检查 session_state 中是否有 "agent" 键
    # session_state 是 Streamlit 的会话状态
    # 用于在页面刷新时保持数据

    st.session_state["agent"] = ReactAgent()
    # 如果没有，创建 ReactAgent 实例并保存
    # ReactAgent() 会初始化 Agent（加载模型、工具等）
    # 保存到 session_state，避免每次请求都重新创建

if "message" not in st.session_state:
    # 检查 session_state 中是否有 "message" 键

    st.session_state["message"] = []
    # 如果没有，初始化为空列表
    # 用于存储所有对话历史

for message in st.session_state["message"]:
    # 遍历所有历史消息
    # message 是当前遍历到的消息字典

    if message["role"] == "user":
        # 检查消息角色是否为用户

        st.chat_message("user").write(message["content"])
        # 如果是用户消息，显示在用户气泡中
        # message["content"] 是消息内容

    else:
        # 如果是其他角色（assistant）

        st.chat_message("assistant").write(message["content"])
        # 显示在助手气泡中

# 用户输入提示词 (行内注释)
prompt = st.chat_input()
# 创建聊天输入框
# 用户在这里输入问题
# prompt 是用户输入的文本（字符串）

if prompt:
    # 如果用户输入了内容（prompt 不为空）

    st.chat_message("user").write(prompt)
    # 立即在界面上显示用户的问题

    st.session_state["message"].append({"role": "user", "content": prompt})
    # 将用户消息添加到历史记录
    # 这样页面刷新后消息不会丢失

    response_messages = []
    # 创建空列表，用于存储 AI 的回复
    # 每个元素是 AI 回复的一个片段

    with st.spinner("正在思考..."):
        # 创建一个"正在思考..."的加载动画
        # 在 AI 生成回复时显示旋转图标

        response = st.session_state["agent"].execute_stream(prompt)


        # 【关键】调用 Agent 的 execute_stream 方法
        # 传入用户问题 prompt
        # execute_stream 返回一个生成器（generator）
        # 生成器会逐步返回 AI 的回答片段

        # ==================== capture 函数详解 ====================
        def capture(generate, cache_list):
            # 【核心】定义 capture 生成器函数
            # 作用：包装 AI 的流式输出，添加逐字显示效果

            # 参数：
            # - generate: 生成器对象（response）
            #   来自 agent.execute_stream(prompt)
            #   会逐步返回 AI 的回答片段
            #   例如："根据相关资料..."、"建议您..."

            # - cache_list: 列表（response_messages）
            #   用于缓存所有片段，最后保存到历史记录

            for chunk in generate:
                # 遍历生成器中的每个 chunk
                # chunk 是 AI 返回的一个片段（字符串）
                # 例如："根据相关资料，扫地机器人的保养需要注意以下几点：\n"

                cache_list.append(chunk)
                # 将当前片段添加到缓存列表
                # 这样最后可以拼接成完整的回复

                for char in chunk:
                    # 【打字机效果】逐字遍历 chunk 中的每个字符
                    # char 是当前字符
                    # 例如：'根'、'据'、'相'、'关'...

                    time.sleep(0.01)
                    # 延迟 0.01 秒
                    # 制造打字机效果（逐字输出）
                    # 如果不延迟，文字会瞬间全部显示

                    yield char
                    # 【关键】yield 返回当前字符
                    # 这是一个生成器函数
                    # 每次 yield 一个字符，暂停，等待下次调用

                    # 流程示例：
                    # 第 1 次：yield '根' → 暂停 ⏸️ → 显示"根"
                    # 第 2 次：yield '据' → 暂停 ⏸️ → 显示"根据"
                    # 第 3 次：yield '相' → 暂停 ⏸️ → 显示"根据相"
                    # ...
                    # 最终效果：文字逐字显示，像打字机一样


        # ==================== capture 使用示例 ====================
        """
        假设 AI 返回：
        chunk1 = "根据资料...\n"
        chunk2 = "建议您...\n"

        capture 函数的执行流程：
        1. 获取 chunk1
        2. 添加到缓存：cache_list = ["根据资料...\n"]
        3. 逐字 yield：
           - yield '根' (延迟 0.01 秒)
           - yield '据' (延迟 0.01 秒)
           - yield '资' (延迟 0.01 秒)
           - ...
        4. 获取 chunk2
        5. 添加到缓存：cache_list = ["根据资料...\n", "建议您...\n"]
        6. 逐字 yield：
           - yield '建' (延迟 0.01 秒)
           - yield '议' (延迟 0.01 秒)
           - ...

        最终效果：
        用户看到文字逐字显示：
        根→据→资→料→...→建→议→您→...
        """

        st.chat_message("assistant").write_stream(capture(response, response_messages))
        # 【关键】调用 write_stream 显示 AI 回复
        # write_stream 接收一个生成器，并流式显示其输出

        # 参数：
        # - capture(response, response_messages): 调用 capture 生成器
        #   response: AI 的流式输出生成器
        #   response_messages: 缓存列表

        # write_stream 的作用：
        # 1. 自动调用生成器，获取每个 yield 的值
        # 2. 逐步显示在聊天界面
        # 3. 支持 Markdown 格式

        # 完整流程：
        # write_stream → capture → response (AI 生成器)
        #     ↓              ↓           ↓
        #   显示在界面   逐字处理   返回 AI 片段

        st.session_state["message"].append({"role": "assistant", "content": response_messages[-1]})
        # 将 AI 回复添加到历史记录
        # response_messages[-1] 获取最后一个片段
        # 【注意】这里可能有 bug，应该是 "".join(response_messages) 拼接所有片段

        st.rerun()
        # 重新运行页面
        # 这样新的消息会立即显示在界面上
        # 页面刷新后，session_state 中的消息会保留

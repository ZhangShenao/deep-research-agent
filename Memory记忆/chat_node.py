# -*- coding: utf-8 -*-
"""
@Time    : 2025/11/07 14:00
@Author  : ZhangShenao
@File    : chat_node.py
@Desc    : 聊天节点
"""

from state import State
from llm import LLM
from langchain_core.messages import SystemMessage
from mem0_client import mem0_client

# 系统提示词
SYSTEM_PROMPT = """
你是一位智能助手。请使用提供的上下文信息来个性化你的回复，并记住用户的偏好和过往的交互记录。

以下是来自之前对话的相关信息：\n
{context}
"""


def chat_node(state: State) -> State:
    """
    聊天节点
    """

    # 获取消息列表与Mem0 user_id
    messages = state["messages"]
    user_id = state["mem0_user_id"]

    # 基于最后一条消息,检索相关记忆
    memories = mem0_client.search(
        query=messages[-1].content, user_id=user_id, limit=10
    )["results"]

    # 构造上下文信息
    context = "\n".join([f"- {memory["memory"]}" for memory in memories])
    system_message = SystemMessage(content=SYSTEM_PROMPT.format(context=context))

    # 构造完整消息列表
    full_messages = [system_message] + messages

    # 调用LLM,生成回复
    response = LLM.invoke(full_messages)

    # 将交互记录存储到 Mem0
    interaction = [
        {"role": "human", "content": messages[-1].content},
        {"role": "ai", "content": response.content},
    ]
    result = mem0_client.add(messages=interaction, user_id=user_id, infer=False)
    print(f"【成功保存 {len(result.get("results", []))} 条记忆】")

    # 返回更新后的状态
    return {"messages": [response]}

# -*- coding: utf-8 -*-
"""
@Time    : 2025/10/22 13:32
@Author  : ZhangShenao
@File    : llm_node.py
@Desc    : 人类节点
"""

from langgraph.types import interrupt
from langchain_core.messages import ToolMessage
from langgraph.graph.message import MessagesState


async def human_node(state: MessagesState) -> MessagesState:
    """人类处理节点"""

    # 获取最后一条工具消息
    # 能够进入到当前节点，说明一定是ask_human工具调用
    human_tool = state["messages"][-1].tool_calls[0]
    if human_tool is None or human_tool["name"] != "ask_human":
        print("不是人类工具调用,直接返回")
        return state

    # 中断当前任务，等待人类回答
    question = human_tool["args"]["question"]
    print(f"向人类的提问: {question}")
    human_answer = interrupt(question)
    print(f"人类回答: {human_answer}")

    # 保存工具调用结果
    tool_call_result = ToolMessage(content=human_answer, tool_call_id=human_tool["id"])

    # 更新状态
    state["messages"].append(tool_call_result)
    return state

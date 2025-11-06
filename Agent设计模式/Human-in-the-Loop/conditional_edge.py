# -*- coding: utf-8 -*-
"""
@Time    : 2025/11/6 13:32
@Author  : ZhangShenao
@File    : conditional_node.py
@Desc    : 条件边
"""

from langgraph.graph import END
from langgraph.graph.message import MessagesState


def conditional_edge(state: MessagesState) -> str:
    """
    条件边: 根据最后一条消息的类型，决定下一步执行哪个节点
    """

    # 如果最后一条消息不是工具调用消息，说明LLM直接生成了回复，则结束流程
    if len(state["messages"][-1].tool_calls) == 0:
        return END

    # 获取最后一条工具调用消息
    tool_call = state["messages"][-1].tool_calls[0]

    # 根据工具名称，决定下一步执行哪个节点
    tool_name = tool_call["name"]
    if tool_name == "ask_human":
        return "human_node"

    return "tool_node"

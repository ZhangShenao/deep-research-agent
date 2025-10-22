# -*- coding: utf-8 -*-
"""
@Time    : 2025/10/22 13:32
@Author  : ZhangShenao
@File    : tool_node.py
@Desc    : 工具调用节点
"""

from tools import TOOL_DICT
from langchain_core.messages import ToolMessage
from langgraph.graph.message import MessagesState


async def tool_node(state: MessagesState) -> MessagesState:
    """
    工具调用节点
    """

    # 获取最后一条工具消息
    tool_message = state["messages"][-1]
    if tool_message.tool_calls is None:
        return state

    # 遍历工具调用信息,执行工具调用
    for tool_call in tool_message.tool_calls:
        tool_name = tool_call["name"]
        tool = TOOL_DICT[tool_name]
        if tool is not None:
            tool_call_result = await tool.ainvoke(input=tool_call["args"])
            print(f"\n调用工具: {tool_name}, 执行结果: {tool_call_result}\n")

            # 在消息列表中保存工具调用结果
            state["messages"].append(
                ToolMessage(
                    content=tool_call_result,
                    tool_call_id=tool_call["id"],
                )
            )

    # 返回更新后的状态
    return state

# -*- coding: utf-8 -*-
"""
@Time    : 2025/9/29 13:32
@Author  : ZhangShenao
@File    : tool_node.py
@Desc    : 工具调用节点
"""

from state import PlanState
from tools import TOOL_DICT
from langchain_core.messages import ToolMessage


def tool_node(state: PlanState) -> PlanState:
    """
    工具调用节点
    """

    print("=" * 100)
    print("进入tool_node")

    # 获取工具调用信息
    tool_calls = state["messages"][-1].tool_calls
    if tool_calls is None:
        return state

    # 遍历工具调用信息,执行工具调用
    for tool_call in tool_calls:
        tool_name = tool_call["name"]
        tool_args = tool_call["args"]
        tool = TOOL_DICT[tool_name]
        if tool is not None:
            tool_call_result = tool.invoke(input=tool_args)
            print(f"工具执行结果: \n{tool_call_result}")

            # 在消息列表中保存工具调用结果
            state["messages"].append(
                ToolMessage(
                    content=f"工具调用结果: {tool_call_result}",
                    tool_call_id=tool_call["id"],
                )
            )

    # 返回更新后的状态
    return state

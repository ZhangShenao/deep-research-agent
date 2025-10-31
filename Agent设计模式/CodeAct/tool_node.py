# -*- coding: utf-8 -*-
"""
@Time    : 2025/9/28 14:47
@Author  : ZhangShenao
@File    : tool_node.py
@Desc    : 工具调用节点
"""

from state import GlobalState
from tools import TOOL_DICT
from langchain_core.messages import HumanMessage


def tool_node(state: GlobalState) -> GlobalState:
    """
    工具调用节点
    """

    print("=" * 100)
    print("enter tool_node")

    # 获取动作列表
    actions = state["actions"]
    print(actions)

    # 遍历动作列表,执行工具调用
    for action in actions:
        tool_name = action["tool_name"]
        tool_args = action["tool_args"]
        tool = TOOL_DICT[tool_name]
        if tool is not None:
            observation = tool.invoke(input=tool_args)

            # 将工具调用结果更新到状态中
            state["messages"].append(
                HumanMessage(content=f"##执行结果:\n{observation}")
            )

    # 返回更新后的状态
    return state

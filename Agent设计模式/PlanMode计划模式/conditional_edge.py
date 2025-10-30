# -*- coding: utf-8 -*-
"""
@Time    : 2025/9/29 13:32
@Author  : ZhangShenao
@File    : should_continue_node.py
@Desc    : 条件边
"""

from state import PlanAndExecuteState
from langgraph.graph import END


def conditional_edge(state: PlanAndExecuteState) -> str:
    """
    条件边
    """

    # 获取最后一条消息,如果消息内容中包含了"Final Answer"标识
    last_message = state["messages"][-1]
    if "Final Answer" in last_message.content:
        return END

    return "tool_node"

# -*- coding: utf-8 -*-
"""
@Time    : 2025/9/29 13:32
@Author  : ZhangShenao
@File    : should_continue_node.py
@Desc    : 是否继续执行节点
"""

from state import PlanState
from langgraph.graph import END


def should_continue_node(state: PlanState) -> str:
    """
    是否继续执行节点
    """

    print("=" * 100)
    print("进入should_continue_node")

    # 获取最后一条消息,如果消息内容中包含了"Final Answer"标识
    last_message = state["messages"][-1]
    if "Final Answer" in last_message.content:
        return END

    return "tool_node"

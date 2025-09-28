# -*- coding: utf-8 -*-
"""
@Time    : 2025/9/28 14:47
@Author  : ZhangShenao
@File    : process_node.py
@Desc    : 流程处理节点
"""

from state import GlobalState
from langgraph.graph import END


def process_node(state: GlobalState) -> str:
    """
    流程处理节点 - 决定下一步执行哪个节点
    """

    # 如果生成了最终结果,则结束流程
    if state.get("final_result") is not None and state["final_result"] != "":
        return END

    # 未生成最终结果,则进入工具节点
    return "tool_node"

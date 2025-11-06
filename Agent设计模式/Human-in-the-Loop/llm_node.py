# -*- coding: utf-8 -*-
"""
@Time    : 2025/10/22 13:32
@Author  : ZhangShenao
@File    : llm_node.py
@Desc    : LLM节点
"""

from llm import LLM_WITH_TOOLS
from langgraph.graph.message import MessagesState


async def llm_node(state: MessagesState) -> MessagesState:
    """
    LLM节点
    """

    # 调用LLM,获取结果
    resp = await LLM_WITH_TOOLS.ainvoke(input=state["messages"])
    print(f"\nLLM回答: \n{resp.content}")

    # 更新状态
    state["messages"].append(resp)

    # 返回更新后的状态
    return state

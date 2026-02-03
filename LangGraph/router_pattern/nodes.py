# -*- coding: utf-8 -*-
"""
@Time    : 2026/02/03
@Author  : ZhangShenao
@File    : nodes.py
@Desc    : 节点定义
"""

from langgraph.graph import StateGraph
import os
from langchain_openai import ChatOpenAI
from langgraph.graph.message import MessagesState
from tools import multiply
from llm import ZHIPU_LLM


def llm_node(state: MessagesState) -> MessagesState:
    """
    LLM节点
    """

    # 将LLM绑定工具
    llm_with_tools = ZHIPU_LLM.bind_tools([multiply])

    # 调用LLM,获取结果
    resp = llm_with_tools.invoke(input=state["messages"])

    # 返回更新后的状态
    return {"messages": [resp]}

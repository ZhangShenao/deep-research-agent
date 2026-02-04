# -*- coding: utf-8 -*-
"""
@Time    : 2026/02/04
@Author  : ZhangShenao
@File    : conditional_edge.py
@Desc    : 条件边
"""

from langgraph.graph.message import MessagesState
from typing import Literal
from langgraph.graph import END

# 设置聊天轮次阈值，超过该阈值后生成摘要
SUMMARY_TURNS = 4


def conditional_edge(state: MessagesState) -> Literal["summary_node", END]:
    """
    条件边
    """

    # 如果当前聊天记录超过指定轮次，则生成摘要，否则结束对话
    if len(state["messages"]) >= SUMMARY_TURNS:
        return "summary_node"
    else:
        return END

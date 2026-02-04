# -*- coding: utf-8 -*-
"""
@Time    : 2026/02/04
@Author  : ZhangShenao
@File    : state.py
@Desc    : Agent状态设计
"""

from langgraph.graph.message import MessagesState


class AgentState(MessagesState):
    """
    Agent状态定义
    """

    summary: str  # 保存聊天历史摘要，当聊天轮次超过一定数量时触发

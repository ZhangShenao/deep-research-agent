# -*- coding: utf-8 -*-
"""
@Time    : 2025/9/29 13:32
@Author  : ZhangShenao
@File    : state.py
@Desc    : 状态定义
"""

from langgraph.graph.message import MessagesState


class PlanState(MessagesState):
    """
    计划状态定义
    """

    plan: str  # 生成的计划

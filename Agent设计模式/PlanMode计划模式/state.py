# -*- coding: utf-8 -*-
"""
@Time    : 2025/9/29 13:32
@Author  : ZhangShenao
@File    : state.py
@Desc    : 状态定义
"""

from langgraph.graph.message import MessagesState


class PlanAndExecuteState(MessagesState):
    """
    计划和执行状态定义
    """

    plan: str  # 生成的计划
    step: int  # 当前步骤

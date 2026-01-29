# -*- coding: utf-8 -*-
"""
@Time    : 2026/01/28
@Author  : ZhangShenao
@File    : state.py
@Desc    : Graph 状态定义

State状态，是整个Graph执行过程中共享的数据结构。
所有节点都可以读取和修改这个状态。
"""

from typing import TypedDict


class GraphState(TypedDict):
    """
    Graph 状态定义

    """

    state: str  # Graph 状态

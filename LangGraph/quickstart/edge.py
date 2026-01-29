# -*- coding: utf-8 -*-
"""
@Time    : 2026/01/28
@Author  : ZhangShenao
@File    : edge.py
@Desc    : Graph 边定义

Edge边，是Node节点间的连接关系，定义了State状态的转移逻辑。

边的类型:
1. 普通边（Normal Edges）
用途：当你希望总是从一个节点到另一个节点时使用
特点：无条件执行，路径固定
示例：`START` → `node_1`，`node_2` → `END`

2. 条件边（Conditional Edges）
用途：当你希望有条件地在节点之间路由时使用
特点：根据某些逻辑动态决定下一个节点
实现：通过函数实现，函数返回下一个要访问的节点名称

条件边是实现Graph动态性的关键！

"""

from tkinter import N
from state import GraphState
from typing import Literal
import random


def decide_mood(state: GraphState) -> Literal["node2", "node3"]:
    """
    条件边: 根据当前状态决定下一步执行哪个节点
    """

    print("执行Conditional Edge")

    # 获取当前状态
    current_state = state["state"]

    # 采用随机策略，动态选择下一个Node
    next_node = random.choice(["node2", "node3"])

    # 否则执行node_3
    print(f"选择下一个Node: {next_node}")
    return next_node

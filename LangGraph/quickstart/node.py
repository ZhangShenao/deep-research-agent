# -*- coding: utf-8 -*-
"""
@Time    : 2026/01/28
@Author  : ZhangShenao
@File    : node.py
@Desc    : Graph 节点定义

Node节点，是Graph的基本执行单元。
每个Node节点都是一个函数，接收一个State状态，返回一个State状态。
Node节点之间通过边连接，形成一个有向无环图。

Node 执行流程：
1. 接收当前状态作为输入
2. 执行特定的业务逻辑
3. 返回包含更新字段的字典
4. LangGraph自动将返回的字段合并到状态中
"""

from state import GraphState


def node1(state: GraphState) -> GraphState:
    """
    Node1
    """

    print("执行node1")

    # 获取当前状态
    current_state = state["state"]

    # 更新状态
    new_state = current_state + "I am"

    # 返回更新后的状态
    return {"state": new_state}


def node2(state: GraphState) -> GraphState:
    """
    Node2
    """

    print("执行node2")

    # 获取当前状态
    current_state = state["state"]

    # 更新状态
    new_state = current_state + " happy! "

    # 返回更新后的状态
    return {"state": new_state}


def node3(state: GraphState) -> GraphState:
    """
    Node3
    """

    print("执行node3")

    # 获取当前状态
    current_state = state["state"]

    # 更新状态
    new_state = current_state + "sad! "

    # 返回更新后的状态
    return {"state": new_state}

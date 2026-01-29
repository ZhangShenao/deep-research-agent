# -*- coding: utf-8 -*-
"""
@Time    : 2026/01/28
@Author  : ZhangShenao
@File    : agent.py
@Desc    : Graph Agent

使用Graph构建一个简单的Agent，实现一个简单的情绪状态机。
"""

from langgraph.graph import StateGraph
from state import GraphState
from node import node1, node2, node3
from edge import decide_mood
from langgraph.graph import START, END
from langgraph.graph.state import CompiledStateGraph


def build_graph() -> CompiledStateGraph:
    """
    构建Graph图
    """

    # 基于自定义的State状态，构建一个Graph Agent
    builder = StateGraph(GraphState)

    # 添加Node节点
    # 每个Node都是一个函数，有一个唯一的名称作为标识符
    builder.add_node("node1", node1)
    builder.add_node("node2", node2)
    builder.add_node("node3", node3)

    # 添加普通边
    # 普通边: 无条件执行，路径固定
    builder.add_edge(START, "node1")
    builder.add_edge("node2", END)
    builder.add_edge("node3", END)

    # 添加条件边
    # 条件边: 根据某些逻辑动态决定下一个节点
    builder.add_conditional_edges(source="node1", path=decide_mood)

    # 编译Graph图
    # 编译时,会对Graph进行结构检查，并创建可执行的图
    # 编译后的Graph实现了Runnable协议，可以以invoke的标准方式进行调用
    graph = builder.compile()

    # 可视化图，生成Mermaid图表
    # 这有助于理解图的结构和执行流程
    png_data = graph.get_graph().draw_mermaid_png()
    output_file = "graph.png"
    with open(output_file, "wb") as f:
        f.write(png_data)

    # 返回编译后的Agent
    return graph


if __name__ == "__main__":
    graph = build_graph()

    # 初始化State
    init_state = GraphState(state="Hello, this is ZSA~ ")

    # 运行Graph图
    result_state = graph.invoke(init_state)

    print(f"最终执行结果: {result_state["state"]}")

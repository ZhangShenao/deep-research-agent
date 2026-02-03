# -*- coding: utf-8 -*-
"""
@Time    : 2026/02/03
@Author  : ZhangShenao
@File    : graph.py
@Desc    : 构造Graph图
"""

from langgraph.graph import StateGraph
from nodes import llm_node
from langgraph.graph.message import MessagesState
from langgraph.prebuilt import ToolNode
from tools import multiply
from langgraph.graph import START
from langgraph.prebuilt import tools_condition
from langgraph.graph.state import CompiledStateGraph
from langchain_core.messages import HumanMessage


def build_graph() -> CompiledStateGraph:
    # 创建GraphBuilder
    builder = StateGraph(MessagesState)

    # 添加自定义的LLM节点,用于LLM调用
    builder.add_node("llm_node", llm_node)

    # 添加LangGraph内置的ToolNode节点,用于工具调用
    builder.add_node("tools", ToolNode(tools=[multiply]))

    # 添加普通Edge
    builder.add_edge(START, "llm_node")
    builder.add_edge("tools", "llm_node")

    # 添加条件Edge
    builder.add_conditional_edges(
        source="llm_node",
        path=tools_condition,  # 使用LangGraph内置的tools_condition条件边
        # This utility function implements the standard conditional logic for ReAct-style
        # agents: if the last `AIMessage` contains tool calls, route to the tool execution
        # node; otherwise, end the workflow. This pattern is fundamental to most tool-calling
        # agent architectures.
    )

    # 编译Graph图
    graph = builder.compile()

    # 打印Graph图,并保存到本地
    graph.get_graph().draw_mermaid_png(output_file_path="./router_pattern_graph.png")

    # 返回编译后的Graph图
    return graph


if __name__ == "__main__":
    # 构建Graph图
    graph = build_graph()

    # 测试简单问题
    print(
        "--------------------------------测试简单问题--------------------------------"
    )
    init_state = {"messages": [HumanMessage(content="你是什么模型？")]}
    result = graph.invoke(init_state)

    # 打印执行过程
    for i, m in enumerate(result["messages"]):
        print(f"\n步骤 {i+1}:")
        m.pretty_print()
    print("=" * 100)

    # 测试复杂问题
    print(
        "--------------------------------测试复杂问题--------------------------------"
    )
    init_state = {"messages": [HumanMessage(content="10和20的乘积是多少？")]}
    result = graph.invoke(init_state)

    # 打印执行过程
    for i, m in enumerate(result["messages"]):
        print(f"\n步骤 {i+1}:")
        m.pretty_print()
